import sys
import pygame
from typing import List
from src.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, FPS,
    COLOR_BLACK, COLOR_WHITE, COLOR_RED, COLOR_PINK, COLOR_CYAN, COLOR_ORANGE, COLOR_PACMAN,
    STATE_START, STATE_PLAYING, STATE_PAUSED, STATE_READY, STATE_GAME_OVER, STATE_VICTORY, STATE_DYING
)
from src.board import Board
from src.pacman import Pacman
from src.ghost import Ghost
from src.sound import ArcadeSoundManager

class Game:
    """Main game coordinator acting as the VBLANK interrupt simulator and engine."""

    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AntiGravity Pac-Man (Retro Arcade Exact)")
        self.clock = pygame.time.Clock()
        
        # Load Retro Font
        try:
            self.font = pygame.font.SysFont("consolas", 20, bold=True)
            self.large_font = pygame.font.SysFont("consolas", 24, bold=True)
        except Exception:
            self.font = pygame.font.Font(None, 24)
            self.large_font = pygame.font.Font(None, 30)

        # Initialize Sound Manager
        self.sounds = ArcadeSoundManager()
        self.sounds.initialize_sounds()

        # Initialize Sprite Loader
        from src.sprites import SpriteLoader
        self.sprites = SpriteLoader()
        self.sprites.load_sprites()

        # Initialize Game Components
        self.board = Board()
        
        # Pacman spawn location is col 14, row 26 (screen row 26)
        # Maze starts offset by 3, so row 26 is index 23 of the layout grid (3 + 23 = 26)
        self.pacman = Pacman(14, 26)

        # Ghost spawn locations (inside house: Inky at 11.5, Pinky at 13.5, Clyde at 15.5, except Blinky outside at 13)
        self.blinky = Ghost("Blinky", COLOR_RED, 13, 14)
        self.pinky = Ghost("Pinky", COLOR_PINK, 13.5, 17)
        self.inky = Ghost("Inky", COLOR_CYAN, 11.5, 17)
        self.clyde = Ghost("Clyde", COLOR_ORANGE, 15.5, 17)

        self.ghosts: List[Ghost] = [self.blinky, self.pinky, self.inky, self.clyde]

        # Game Stats
        self.score = 0
        self.high_score = 10000
        self.lives = 3
        self.level = 1
        
        # Timing / State Machine variables
        self.state = STATE_START
        self.state_timer = 0
        self.flash_timer = 0
        self.ghost_eat_combo = 0  # 200, 400, 800, 1600 points per power pellet
        self.game_ticks = 0

    def reset_level(self) -> None:
        """Reset player and ghost entities back to spawn configurations (keep layout/score)."""
        self.pacman.reset()
        for ghost in self.ghosts:
            ghost.reset()
        self.ghost_eat_combo = 0

    def reset_full_game(self) -> None:
        """Reset score, lives, level, board, and entities."""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.board.reset()
        self.reset_level()

    def run(self) -> None:
        """Main game loop simulating hardware VBLANK interrupts at 60Hz."""
        while True:
            # 1. Simulate VBLANK interrupt trigger (Lock frame rate to 60Hz)
            self.clock.tick(FPS)
            self.game_ticks += 1
            
            # 2. Run VBLANK Interrupt Handler (inputs, logic, sound updates)
            self.vblank_interrupt_handler()

    def vblank_interrupt_handler(self) -> None:
        """Simulates CPU interrupt handler executed once per VBLANK (every frame)."""
        # A. Process CPU inputs (I/O registers)
        self.process_inputs()

        # B. Run State Update logic
        self.update_game_state()

        # C. Render visual scanlines to display buffer
        self.render()

    def process_inputs(self) -> None:
        """Handle keyboard input events and state switches."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.sounds.stop_all()
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if self.state == STATE_START:
                    # Press any key during start screen to begin
                    self.sounds.stop_all()
                    self.state = STATE_READY
                    self.state_timer = 180  # 3 seconds ready
                    self.sounds.play("intro")
                
                elif self.state == STATE_PLAYING:
                    # Direction Queuing (W/A/S/D or Arrows)
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.pacman.set_direction(0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.pacman.set_direction(0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.pacman.set_direction(-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.pacman.set_direction(1, 0)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = STATE_PAUSED
                
                elif self.state == STATE_PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_PLAYING

    def update_game_state(self) -> None:
        """Core state machine logic updated 60 times a second."""
        if self.state == STATE_START:
            # Flashing menu text
            self.state_timer += 1
            if self.state_timer == 1:
                # Play loop siren softly on start screen
                pass

        elif self.state == STATE_READY:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = STATE_PLAYING
                self.sounds.play("siren", loops=-1)

        elif self.state == STATE_PLAYING:
            # 1. Update Entities
            self.pacman.update(self.board)
            for ghost in self.ghosts:
                ghost.update(self.board, self.pacman, self.blinky)

            # 2. Check Pellet Eating
            p_col, p_row = self.pacman.grid_pos
            points, p_type = self.board.check_pellet(p_col, p_row)
            
            if points > 0:
                self.score += points
                if self.score > self.high_score:
                    self.high_score = self.score

                # Play munch sound
                self.sounds.play("waka")

                if p_type == 'power':
                    # Set ghosts to frightened state
                    # Speed increases, state timer set (6 seconds = 360 frames)
                    frightened_duration = max(120, 360 - (self.level * 30))
                    for ghost in self.ghosts:
                        ghost.set_state("frightened", frightened_duration)
                    self.ghost_eat_combo = 0
                    self.sounds.play("frightened", loops=-1)

            # 3. Check Background sound toggle
            # If all ghosts are back to normal, turn siren back on
            any_frightened = any(g.state == "frightened" for g in self.ghosts)
            if not any_frightened and self.sounds.initialized:
                # Siren loop
                # If siren isn't playing on channel 0, start it
                chan = pygame.mixer.Channel(0)
                if not chan.get_busy() or chan.get_sound() == self.sounds.sounds.get("frightened"):
                    self.sounds.play("siren", loops=-1)

            # 4. Check Level Win Condition
            if self.board.pellets_left <= 0:
                self.state = STATE_VICTORY
                self.state_timer = 150  # ~2.5 seconds victory flash
                self.sounds.stop_all()

            # 5. Check Collisions with Ghosts
            for ghost in self.ghosts:
                # Simple distance collision check in pixels
                dx = self.pacman.x - ghost.x
                dy = self.pacman.y - ghost.y
                # If within half tile width, register collision
                if dx**2 + dy**2 < (TILE_SIZE // 1.5) ** 2:
                    if ghost.state == "frightened":
                        # Pacman eats the ghost
                        ghost.set_state("eaten")
                        self.ghost_eat_combo += 1
                        # Double points each consecutive eaten ghost: 200, 400, 800, 1600
                        eat_score = 200 * (2 ** (self.ghost_eat_combo - 1))
                        self.score += min(1600, eat_score)
                        self.sounds.play("eat_ghost")
                    elif ghost.state in ("chase", "scatter"):
                        # Pacman dies
                        self.state = STATE_DYING
                        self.state_timer = 120  # 2 seconds dying state
                        self.sounds.stop_all()
                        break

        elif self.state == STATE_DYING:
            self.state_timer -= 1
            if self.state_timer == 90:
                self.sounds.play("death")
            elif self.state_timer <= 0:
                self.lives -= 1
                if self.lives <= 0:
                    self.state = STATE_GAME_OVER
                    self.state_timer = 180  # 3 seconds game over display
                else:
                    self.reset_level()
                    self.state = STATE_READY
                    self.state_timer = 120  # 2 seconds ready phase

        elif self.state == STATE_GAME_OVER:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.reset_full_game()
                self.state = STATE_START
                self.state_timer = 0

        elif self.state == STATE_VICTORY:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.level += 1
                self.board.reset()
                self.reset_level()
                self.state = STATE_READY
                self.state_timer = 120

    def render(self) -> None:
        """Clear frame buffer, draw screen scanlines, and update output display."""
        # Clear screen
        self.screen.fill(COLOR_BLACK)

        # 1. Draw Maze & Pellets
        # In victory state, flash walls between Blue and White
        flash = False
        if self.state == STATE_VICTORY:
            # Flash wall every 15 frames
            flash = (self.state_timer // 15) % 2 == 0
        
        # In start screen, alternate between showing empty maze (with pellets) and showing the ghosts list
        draw_maze = True
        if self.state == STATE_START:
            show_maze = (self.game_ticks // 300) % 2 == 1
            if not show_maze:
                draw_maze = False
                
        if draw_maze:
            self.board.draw(self.screen, self.sprites, flash)

        # 2. Draw Entities (skip only during start screen's ghost list phase)
        draw_entities = True
        if self.state == STATE_START:
            show_maze = (self.game_ticks // 300) % 2 == 1
            if not show_maze:
                draw_entities = False

        if draw_entities:
            if self.state != STATE_DYING or self.state_timer > 90:
                # Don't draw ghosts during the actual death spinning animation
                for ghost in self.ghosts:
                    ghost.draw(self.screen, self.sprites)
            
            if self.state == STATE_DYING and self.state_timer <= 90:
                # Draw pixel-art Pacman dying animation
                cx = self.pacman.x + TILE_SIZE // 2
                cy = self.pacman.y + TILE_SIZE // 2
                progress = max(0, self.state_timer) / 90.0
                frame_idx = int((1.0 - progress) * 10)
                frame_idx = max(0, min(10, frame_idx))
                sprite = self.sprites.get_pacman_dying_sprite(frame_idx)
                self.screen.blit(sprite, (cx - 24, cy - 24))
            else:
                self.pacman.draw(self.screen, self.sprites)

        # 3. Draw HUD Texts (Arcade accurate locations)
        # Score header
        txt_1up = self.font.render("1UP", True, COLOR_WHITE)
        score_val = self.font.render(f"{self.score:02d}", True, COLOR_WHITE)
        self.screen.blit(txt_1up, (TILE_SIZE * 3, TILE_SIZE * 1))
        self.screen.blit(score_val, (TILE_SIZE * 3, TILE_SIZE * 2))

        txt_hs = self.font.render("HIGH SCORE", True, COLOR_WHITE)
        hs_val = self.font.render(f"{self.high_score:02d}", True, COLOR_WHITE)
        self.screen.blit(txt_hs, (TILE_SIZE * 11, TILE_SIZE * 1))
        self.screen.blit(hs_val, (TILE_SIZE * 13, TILE_SIZE * 2))

        # Bottom Lives Footer
        # Draw small yellow circles to represent lives
        for i in range(self.lives - 1):
            lx = TILE_SIZE * (2 + i * 2)
            ly = TILE_SIZE * 34 + TILE_SIZE // 2
            pygame.draw.circle(self.screen, COLOR_PACMAN, (lx, ly), TILE_SIZE // 2 - 2)
            # Wedge cutout facing right
            pygame.draw.polygon(self.screen, COLOR_BLACK, [(lx, ly), (lx + TILE_SIZE, ly - TILE_SIZE // 2), (lx + TILE_SIZE, ly + TILE_SIZE // 2)])

        # Draw level indicator (Fruit space, simplified to text for retro styling)
        level_txt = self.font.render(f"L{self.level}", True, COLOR_WHITE)
        self.screen.blit(level_txt, (TILE_SIZE * 24, TILE_SIZE * 34))

        # 4. State Texts Overlay
        if self.state == STATE_START:
            # Retro Arcade Start Screen
            title_txt = self.large_font.render("ANTIGRAVITY PAC-MAN", True, COLOR_PACMAN)
            prompt_txt = self.font.render("PRESS ANY KEY TO PLAY", True, COLOR_CYAN)
            
            show_maze = (self.game_ticks // 300) % 2 == 1
            if not show_maze:
                self.screen.blit(title_txt, (SCREEN_WIDTH // 2 - title_txt.get_width() // 2, TILE_SIZE * 6))
                # Display colors and names of ghosts as retro list
                self._draw_menu_ghost_info()
            
            # Flash text "PRESS ANY KEY TO PLAY" at the same height as the "READY!" text (row 20) in both states
            if (self.game_ticks // 30) % 2 == 0:
                txt_w = prompt_txt.get_width()
                txt_h = prompt_txt.get_height()
                tx = SCREEN_WIDTH // 2 - txt_w // 2
                ty = TILE_SIZE * 20
                # Clear background walls behind the text using a black rectangle
                pygame.draw.rect(self.screen, COLOR_BLACK, (tx - 10, ty - 4, txt_w + 20, txt_h + 8))
                self.screen.blit(prompt_txt, (tx, ty))

        elif self.state == STATE_READY:
            ready_txt = self.large_font.render("READY!", True, COLOR_PACMAN)
            self.screen.blit(ready_txt, (SCREEN_WIDTH // 2 - ready_txt.get_width() // 2, TILE_SIZE * 20))

        elif self.state == STATE_GAME_OVER:
            go_txt = self.large_font.render("GAME  OVER", True, COLOR_RED)
            self.screen.blit(go_txt, (SCREEN_WIDTH // 2 - go_txt.get_width() // 2, TILE_SIZE * 20))

        elif self.state == STATE_PAUSED:
            pause_txt = self.large_font.render("PAUSED", True, COLOR_WHITE)
            self.screen.blit(pause_txt, (SCREEN_WIDTH // 2 - pause_txt.get_width() // 2, TILE_SIZE * 20))

        # Update display buffer
        pygame.display.flip()

    def _draw_menu_ghost_info(self) -> None:
        """Draw the classic character introduction list on the menu screen."""
        ghosts_meta = [
            ("blinky", "red", "SHADOW", COLOR_RED),
            ("pinky", "pink", "SPEEDY", COLOR_PINK),
            ("inky", "cyan", "BASHFUL", COLOR_CYAN),
            ("clyde", "orange", "POKEY", COLOR_ORANGE)
        ]

        y_start = TILE_SIZE * 10
        for name, col_name, desc, color in ghosts_meta:
            # Draw pixel-art ghost representation looking right
            gx = TILE_SIZE * 4
            gy = y_start
            sprite = self.sprites.get_ghost_sprite(name, 1, 0, 0, "chase", 0)
            self.screen.blit(sprite, (gx + TILE_SIZE // 2 - 24, gy + TILE_SIZE // 2 - 24))

            # Character info text
            char_txt = self.font.render(f"- {desc.upper()} \"{name.upper()}\"", True, color)
            self.screen.blit(char_txt, (TILE_SIZE * 7, y_start))
            y_start += TILE_SIZE * 2

if __name__ == "__main__":
    game = Game()
    game.run()
