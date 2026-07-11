import math
import pygame
from typing import Tuple
from src.settings import TILE_SIZE, COLOR_PACMAN, COLOR_BLACK, COLS, ROWS, PACMAN_SPEED_NORMAL

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
        self.angle_offset = 0.0  # mouth animation angle
        self.chomping = True

    @property
    def grid_pos(self) -> Tuple[int, int]:
        """Return current grid (col, row) position."""
        return self.x // TILE_SIZE, self.y // TILE_SIZE

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
            # Fluctuates between 0.0 (closed) and 0.8 (wide open)
            ticks = pygame.time.get_ticks()
            self.angle_offset = 0.4 * (1.0 + math.sin(ticks * 0.025))
        else:
            self.angle_offset = 0.2

        # 2. Movement logic - only check turn decisions at grid boundaries
        is_aligned_x = (self.x % TILE_SIZE == 0)
        is_aligned_y = (self.y % TILE_SIZE == 0)

        if is_aligned_x and is_aligned_y:
            # Currently aligned with a tile. Check if we can apply the queued next direction
            current_col, current_row = self.grid_pos
            target_next_col = current_col + self.next_dir_x
            target_next_row = current_row + self.next_dir_y

            # Tunnel wrapping checks for target check
            if target_next_col < 0:
                target_next_col = COLS - 1
            elif target_next_col >= COLS:
                target_next_col = 0

            # If the queued direction has no wall, make the turn!
            if not board.is_wall(target_next_col, target_next_row, is_ghost=False):
                self.dir_x = self.next_dir_x
                self.dir_y = self.next_dir_y
            
            # If the current direction faces a wall, stop moving
            target_curr_col = current_col + self.dir_x
            target_curr_row = current_row + self.dir_y
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

    def draw(self, surface: pygame.Surface) -> None:
        """Render Pacman with a dynamic vector-drawn chomping mouth."""
        # Calculate center and radius of circle
        cx = self.x + TILE_SIZE // 2
        cy = self.y + TILE_SIZE // 2
        r = TILE_SIZE // 2

        # Draw the yellow base circle
        pygame.draw.circle(surface, COLOR_PACMAN, (cx, cy), r)

        # Draw the mouth cutout (black triangle) if moving and mouth is open
        if self.dir_x != 0 or self.dir_y != 0:
            # Determine base angle of movement direction in radians
            if self.dir_x == 1:
                base_angle = 0.0
            elif self.dir_x == -1:
                base_angle = math.pi
            elif self.dir_y == 1:
                base_angle = math.pi / 2
            else:  # self.dir_y == -1
                base_angle = -math.pi / 2

            # Calculate mouth wedge boundary coordinates
            theta = self.angle_offset
            p1_x = cx + r * math.cos(base_angle - theta)
            p1_y = cy + r * math.sin(base_angle - theta)
            p2_x = cx + r * math.cos(base_angle + theta)
            p2_y = cy + r * math.sin(base_angle + theta)

            # Draw the wedge in black to slice out the mouth
            pygame.draw.polygon(surface, COLOR_BLACK, [(cx, cy), (p1_x, p1_y), (p2_x, p2_y)])
        else:
            # Just draw a closed mouth slice (small black line) pointing left (default spawn look)
            pygame.draw.line(surface, COLOR_BLACK, (cx, cy), (cx - r, cy), 1)
