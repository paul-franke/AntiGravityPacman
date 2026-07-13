import pygame
from typing import Tuple, TYPE_CHECKING
if TYPE_CHECKING:
    from src.sprites import SpriteLoader
from src.settings import TILE_SIZE, COLS, ROWS, PACMAN_SPEED_NORMAL

class Pacman(pygame.sprite.Sprite):
    """Represents the player-controlled Pacman entity."""

    def __init__(self, col: int, row: int) -> None:
        super().__init__()
        # Initial positions
        self.spawn_col = col
        self.spawn_row = row
        self.reset()
        
        # Sprite rect and image dummy (needed for sprite groups, though we draw manually)
        self.rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)

    def reset(self) -> None:
        """Reset Pacman position and state back to spawn defaults."""
        self.x = self.spawn_col * TILE_SIZE
        self.y = self.spawn_row * TILE_SIZE
        self.dir_x = -1  # Classic Pacman starts moving Left
        self.dir_y = 0
        self.next_dir_x = -1
        self.next_dir_y = 0
        self.speed = PACMAN_SPEED_NORMAL
        self.anim_tick = 0
        self.chomping = True

    @property
    def grid_pos(self) -> Tuple[int, int]:
        """Return current grid (col, row) position."""
        return int(self.x // TILE_SIZE), int(self.y // TILE_SIZE)

    def set_direction(self, dx: int, dy: int) -> None:
        """Queue the next direction. If reverse, change direction immediately."""
        self.next_dir_x = dx
        self.next_dir_y = dy

        # Quick reverse: allows immediate turning back without grid alignment
        if (dx != 0 and dx == -self.dir_x) or (dy != 0 and dy == -self.dir_y):
            self.dir_x = dx
            self.dir_y = dy

    def update(self, board) -> None:
        """Update Pacman's position and animation synced to 60Hz clock."""
        # 1. Animation tick
        if self.chomping and (self.dir_x != 0 or self.dir_y != 0):
            self.anim_tick = (self.anim_tick + 1) % 16
        else:
            self.anim_tick = 0

        # 2. Movement logic - Cornering & Turn checking
        center_x = round(self.x / TILE_SIZE) * TILE_SIZE
        center_y = round(self.y / TILE_SIZE) * TILE_SIZE

        # Check if player is trying to make a turn (perpendicular or change)
        is_turning = (self.next_dir_x != self.dir_x or self.next_dir_y != self.dir_y)
        
        if is_turning:
            # Check if within cornering range (4 pixels) of the nearest center
            if self.dir_x != 0:
                can_turn = (abs(self.x - center_x) <= 4)
            elif self.dir_y != 0:
                can_turn = (abs(self.y - center_y) <= 4)
            else:
                can_turn = True

            if can_turn:
                target_col = int(center_x // TILE_SIZE) + self.next_dir_x
                target_row = int(center_y // TILE_SIZE) + self.next_dir_y
                if target_col < 0:
                    target_col = COLS - 1
                elif target_col >= COLS:
                    target_col = 0

                if not board.is_wall(target_col, target_row, is_ghost=False):
                    self.dir_x = self.next_dir_x
                    self.dir_y = self.next_dir_y
                    # Snap to corner center on turn execution (arcade cutting corners)
                    self.x = center_x
                    self.y = center_y

        # If aligned with a tile center, check if current path hits a wall
        is_aligned_x = (abs(self.x - center_x) < 0.01)
        is_aligned_y = (abs(self.y - center_y) < 0.01)
        if is_aligned_x and is_aligned_y:
            self.x = center_x
            self.y = center_y
            
            target_curr_col = int(center_x // TILE_SIZE) + self.dir_x
            target_curr_row = int(center_y // TILE_SIZE) + self.dir_y
            if target_curr_col < 0:
                target_curr_col = COLS - 1
            elif target_curr_col >= COLS:
                target_curr_col = 0

            if board.is_wall(target_curr_col, target_curr_row, is_ghost=False):
                self.dir_x = 0
                self.dir_y = 0

        # 3. Apply movement
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed

        # 4. Tunnel Wrap-around
        if self.x < -TILE_SIZE // 2:
            self.x = COLS * TILE_SIZE - TILE_SIZE // 2
        elif self.x > COLS * TILE_SIZE - TILE_SIZE // 2:
            self.x = -TILE_SIZE // 2

        # Update sprite rect
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface: pygame.Surface, sprites: "SpriteLoader") -> None:
        """Render Pacman with a dynamic pixel-art sprite sheet tile bitmap."""
        # Calculate center coordinates of the tile
        cx = self.x + TILE_SIZE // 2
        cy = self.y + TILE_SIZE // 2

        # Cycle: 0 (closed) -> 1 (semi) -> 2 (open) -> 3 (semi)
        frame_idx = self.anim_tick // 4
        sprite = sprites.get_pacman_sprite(self.dir_x, self.dir_y, frame_idx)
        
        # Blit the 48x48 sprite centered on the tile (centered offset is 24)
        surface.blit(sprite, (cx - 24, cy - 24))
