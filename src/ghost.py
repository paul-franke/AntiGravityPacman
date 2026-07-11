import math
import random
import pygame
from typing import Tuple, List, TYPE_CHECKING
if TYPE_CHECKING:
    from src.board import Board
    from src.pacman import Pacman
    from src.sprites import SpriteLoader
from src.settings import (
    TILE_SIZE, COLOR_RED, COLOR_PINK, COLOR_CYAN, COLOR_ORANGE, COLOR_BLACK,
    COLOR_BLUE_FRIGHTENED, COLOR_WHITE_FRIGHTENED, COLS, ROWS,
    GHOST_SPEED_NORMAL, GHOST_SPEED_FRIGHTENED, GHOST_SPEED_EATEN
)

# Directions in priority order: UP, LEFT, DOWN, RIGHT (Arcade standard tie-breaker)
DIRECTIONS = [
    (0, -1),  # UP
    (-1, 0),  # LEFT
    (0, 1),   # DOWN
    (1, 0)    # RIGHT
]

# Scatter Target Coordinates for each ghost (Corners)
SCATTER_TARGETS = {
    "blinky": (25, -2),   # Top Right
    "pinky": (2, -2),     # Top Left
    "inky": (27, 34),     # Bottom Right
    "clyde": (0, 34)      # Bottom Left
}

class Ghost(pygame.sprite.Sprite):
    """Base class for Pacman ghost entities with individual AI routines."""

    def __init__(self, name: str, color: Tuple[int, int, int], spawn_col: float, spawn_row: float) -> None:
        super().__init__()
        self.name = name.lower()
        self.color = color
        self.spawn_col = spawn_col
        self.spawn_row = spawn_row
        
        self.rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        self.reset()

    def reset(self) -> None:
        """Reset ghost back to starting position and normal state."""
        self.x = self.spawn_col * TILE_SIZE
        self.y = self.spawn_row * TILE_SIZE
        self.dir_x = 0
        self.dir_y = -1  # Spawn direction is UP
        self.state = "scatter"  # states: chase, scatter, frightened, eaten
        self.speed = GHOST_SPEED_NORMAL
        self.frightened_timer = 0
        self.target_tile = (0, 0)
        self.rect.x = self.x
        self.rect.y = self.y
        self.in_house = True
        
        # Guide exit delays
        if self.name == "blinky":
            self.in_house = False
            self.exit_delay = 0
        elif self.name == "pinky":
            self.exit_delay = 0
        elif self.name == "inky":
            self.exit_delay = 180  # 3 seconds delay
        else:  # clyde
            self.exit_delay = 360  # 6 seconds delay
        self.anim_tick = 0

    @property
    def grid_pos(self) -> Tuple[int, int]:
        return self.x // TILE_SIZE, self.y // TILE_SIZE

    def snap_to_grid(self) -> None:
        """Snap the ghost's pixel coordinates to the nearest grid tile center."""
        col = round(self.x / TILE_SIZE)
        row = round(self.y / TILE_SIZE)
        self.x = col * TILE_SIZE
        self.y = row * TILE_SIZE
        self.rect.x = self.x
        self.rect.y = self.y

    def set_state(self, state: str, duration_frames: int = 0) -> None:
        """Change the ghost state and adjust speed parameters."""
        # Eaten ghosts cannot become frightened
        if self.state == "eaten" and state == "frightened":
            return

        self.state = state
        if state == "frightened":
            self.speed = GHOST_SPEED_FRIGHTENED
            self.frightened_timer = duration_frames
            # Reverse direction immediately when frightened (arcade behavior)
            self.dir_x, self.dir_y = -self.dir_x, -self.dir_y
        elif state == "eaten":
            self.speed = GHOST_SPEED_EATEN
        elif state in ("chase", "scatter"):
            self.speed = GHOST_SPEED_NORMAL
            self.frightened_timer = 0

        # Always snap to grid on state change to ensure alignment at new speeds
        self.snap_to_grid()

    def update(self, board: "Board", pacman: "Pacman", blinky: "Ghost") -> None:
        """Calculate AI decisions at grid boundaries and update coordinates."""
        # 1. Handle house exit logic
        if self.in_house:
            if self.exit_delay > 0:
                self.exit_delay -= 1
                # Bounce up and down visually
                ticks = pygame.time.get_ticks()
                self.y = self.spawn_row * TILE_SIZE + int(6 * math.sin(ticks * 0.015))
                self.rect.x = self.x
                self.rect.y = self.y
                return

            # Exiting: guide horizontally first, then vertically out of the gate
            gate_col = 13
            gate_row = 14
            target_x = gate_col * TILE_SIZE
            target_y = gate_row * TILE_SIZE
            
            # Step 1: Move horizontally to column 13
            if abs(self.x - target_x) > 1:
                if self.x < target_x:
                    self.x += self.speed
                else:
                    self.x -= self.speed
            # Step 2: Move vertically up to row 14
            else:
                self.x = target_x  # Snap to center column
                if self.y > target_y:
                    self.y -= self.speed
                else:
                    # Reached outside the gate!
                    self.y = target_y
                    self.in_house = False
                    self.dir_x = -1 if self.name in ("blinky", "inky") else 1
                    self.dir_y = 0
            
            self.rect.x = self.x
            self.rect.y = self.y
            return

        # 2. Check Frightened Timer expiration
        if self.state == "frightened":
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.set_state("chase")

        # 3. Target calculation (if aligned with grid, choose next direction)
        is_aligned_x = (self.x % TILE_SIZE == 0)
        is_aligned_y = (self.y % TILE_SIZE == 0)

        if is_aligned_x and is_aligned_y:
            # Reached a tile boundary. Choose next direction
            self._update_target(pacman, blinky)
            self._make_turn_decision(board)

        # 4. Apply movement
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed

        # 5. Handle eaten ghost returning home completion
        if self.state == "eaten":
            home_col, home_row = 13, 14
            curr_col, curr_row = self.grid_pos
            if abs(self.x - home_col * TILE_SIZE) < TILE_SIZE and abs(self.y - home_row * TILE_SIZE) < TILE_SIZE:
                # Returned home, revive!
                self.x = home_col * TILE_SIZE
                self.y = home_row * TILE_SIZE
                self.in_house = True
                self.exit_delay = 60  # Bounce in house for 1 second before reviving
                self.set_state("chase")

        # 6. Tunnel wrap-around
        if self.x < -TILE_SIZE // 2:
            self.x = COLS * TILE_SIZE - TILE_SIZE // 2
        elif self.x > COLS * TILE_SIZE - TILE_SIZE // 2:
            self.x = -TILE_SIZE // 2

        self.rect.x = self.x
        self.rect.y = self.y
        self.anim_tick = (self.anim_tick + 1) % 20

    def _update_target(self, pacman: "Pacman", blinky: "Ghost") -> None:
        """Calculate the target tile coordinate depending on state and individual AI."""
        if self.state == "eaten":
            # Return target is the ghost house gate
            self.target_tile = (13, 14)
            return

        if self.state == "scatter":
            self.target_tile = SCATTER_TARGETS[self.name]
            return

        if self.state == "frightened":
            # Target is not used in frightened, decisions are random
            return

        # Chase state targets
        p_col, p_row = pacman.grid_pos
        p_dx, p_dy = pacman.dir_x, pacman.dir_y

        if self.name == "blinky":
            # Red targets Pacman directly
            self.target_tile = (p_col, p_row)

        elif self.name == "pinky":
            # Pink targets 4 tiles ahead of Pacman
            self.target_tile = (p_col + p_dx * 4, p_row + p_dy * 4)

        elif self.name == "inky":
            # Cyan: Vector from Blinky to 2 tiles ahead of Pacman, doubled.
            pivot_col = p_col + p_dx * 2
            pivot_row = p_row + p_dy * 2
            b_col, b_row = blinky.grid_pos
            
            vec_col = pivot_col - b_col
            vec_row = pivot_row - b_row
            
            self.target_tile = (pivot_col + vec_col, pivot_row + vec_row)

        elif self.name == "clyde":
            # Orange: Chases if far, scatters if close
            c_col, c_row = self.grid_pos
            dist_sq = (c_col - p_col) ** 2 + (c_row - p_row) ** 2
            if dist_sq >= 64:  # 8 tiles away
                self.target_tile = (p_col, p_row)
            else:
                self.target_tile = SCATTER_TARGETS["clyde"]

    def _make_turn_decision(self, board: "Board") -> None:
        """Choose the next tile direction that minimizes straight-line distance to target."""
        curr_col, curr_row = self.grid_pos
        
        # Collect valid directions
        valid_moves = []
        for dx, dy in DIRECTIONS:
            # Cannot reverse direction immediately in standard movements
            if dx == -self.dir_x and dy == -self.dir_y:
                continue

            target_col = curr_col + dx
            target_row = curr_row + dy

            # Tunnel wrapping wrap-around check for wall collision
            if target_col < 0:
                target_col = COLS - 1
            elif target_col >= COLS:
                target_col = 0

            # Check if wall or gate
            # Ghosts can pass gate '=' only if they are returning home (eaten)
            is_returning_home = (self.state == "eaten")
            if not board.is_wall(target_col, target_row, is_ghost=True, is_eaten=is_returning_home):
                valid_moves.append((dx, dy, target_col, target_row))

        if not valid_moves:
            # Fallback: allow reverse if completely stuck
            self.dir_x, self.dir_y = -self.dir_x, -self.dir_y
            return

        if self.state == "frightened":
            # Frightened ghosts choose random moves
            dx, dy, _, _ = random.choice(valid_moves)
            self.dir_x = dx
            self.dir_y = dy
            return

        # Find move with minimum Euclidean distance to target
        tx, ty = self.target_tile
        best_move = None
        min_dist_sq = float("inf")

        for dx, dy, target_col, target_row in valid_moves:
            dist_sq = (target_col - tx) ** 2 + (target_row - ty) ** 2
            
            # Tie breaker is implicit by priority order of DIRECTIONS (UP, LEFT, DOWN, RIGHT)
            # If dist_sq is smaller, or if equal and higher priority in DIRECTIONS array
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_move = (dx, dy)

        if best_move:
            self.dir_x, self.dir_y = best_move

    def draw(self, surface: pygame.Surface, sprites: "SpriteLoader") -> None:
        """Render the ghost entity using pixel-art tile bitmaps with wiggle animation."""
        cx = self.x + TILE_SIZE // 2
        cy = self.y + TILE_SIZE // 2

        # Skirt animation toggles between 0 and 1 every 10 frames
        frame_idx = self.anim_tick // 10
        sprite = sprites.get_ghost_sprite(self.name, self.dir_x, self.dir_y, frame_idx, self.state, self.frightened_timer)

        # Blit 48x48 sprite centered on the tile (centered offset is 24)
        surface.blit(sprite, (cx - 24, cy - 24))
