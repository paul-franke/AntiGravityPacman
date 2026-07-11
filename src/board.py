import pygame
from typing import Tuple
from src.settings import TILE_SIZE, COLOR_WALL, COLOR_PELLET, COLOR_WHITE, COLS, ROWS

# Classic Pacman Maze representation (31 rows x 28 columns)
# '#' = Wall
# '.' = Normal Pellet
# 'o' = Power Pellet
# ' ' = Empty / Walkable path
# '=' = Ghost House Gate (only walkable for ghosts)
# 'g' = Ghost House inside
MAZE_LAYOUT = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "%%%%%#.##### ## #####.#%%%%%",
    "%%%%%#.##    gg    ##.#%%%%%",
    "%%%%%#.## ###==### ##.#%%%%%",
    "######.## #gggggg# ##.######",
    "      .   #gggggg#   .      ",
    "######.## #gggggg# ##.######",
    "%%%%%#.## ######## ##.#%%%%%",
    "%%%%%#.##    gg    ##.#%%%%%",
    "%%%%%#.## ######## ##.#%%%%%",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################"
]

# The maze is drawn offset by 3 tiles from the top to accommodate the HUD
ROW_OFFSET = 3

class Board:
    """Manages the maze grid, wall collisions, pellet tracking, and drawing."""

    def __init__(self) -> None:
        # Create a mutable copy of the maze layout to track eaten pellets
        self.grid = [list(row) for row in MAZE_LAYOUT]
        self.initial_pellet_count = self._count_pellets()
        self.pellets_left = self.initial_pellet_count

    def reset(self) -> None:
        """Reset the board layout back to initial state (restore pellets)."""
        self.grid = [list(row) for row in MAZE_LAYOUT]
        self.pellets_left = self.initial_pellet_count

    def _count_pellets(self) -> int:
        count = 0
        for r in range(len(self.grid)):
            for c in range(len(self.grid[r])):
                if self.grid[r][c] in ('.', 'o'):
                    count += 1
        return count

    def get_tile(self, col: int, row: int) -> str:
        """Return the grid character at the specified col and row (relative to screen)."""
        maze_row = row - ROW_OFFSET
        if 0 <= maze_row < len(self.grid) and 0 <= col < COLS:
            return self.grid[maze_row][col]
        return '#'

    def is_wall(self, col: int, row: int, is_ghost: bool = False, is_eaten: bool = False) -> bool:
        """Check if the tile at col, row is a wall."""
        tile = self.get_tile(col, row)
        if tile in ('#', '%'):
            return True
        if tile == '=':
            # Ghost house gate: wall for Pacman, and wall for normal ghosts (unless eaten)
            if is_ghost:
                return not is_eaten
            return True
        return False

    def check_pellet(self, col: int, row: int) -> Tuple[int, str]:
        """Check if there is a pellet at the tile. If yes, eat it and return score value."""
        maze_row = row - ROW_OFFSET
        if 0 <= maze_row < len(self.grid) and 0 <= col < COLS:
            tile = self.grid[maze_row][col]
            if tile == '.':
                self.grid[maze_row][col] = ' '
                self.pellets_left -= 1
                return 10, 'normal'
            elif tile == 'o':
                self.grid[maze_row][col] = ' '
                self.pellets_left -= 1
                return 50, 'power'
        return 0, 'none'

    def draw(self, surface: pygame.Surface, flash_walls: bool = False) -> None:
        """Draw the maze walls, pellets, and power pellets."""
        wall_color = COLOR_WHITE if flash_walls else COLOR_WALL

        for r in range(len(self.grid)):
            screen_row = r + ROW_OFFSET
            for c in range(COLS):
                tile = self.grid[r][c]
                x = c * TILE_SIZE
                y = screen_row * TILE_SIZE

                if tile == '#':
                    # Draw a nice arcade style wall border
                    # Draw a solid dark block, outline with neon blue double lines
                    pygame.draw.rect(surface, (10, 10, 30), (x, y, TILE_SIZE, TILE_SIZE))
                    
                    # Double-lined effect using outer and inner border rectangles
                    pygame.draw.rect(surface, wall_color, (x, y, TILE_SIZE, TILE_SIZE), 1)
                    pygame.draw.rect(surface, wall_color, (x + 3, y + 3, TILE_SIZE - 6, TILE_SIZE - 6), 1)
                elif tile == '=':
                    # Draw ghost gate line
                    pygame.draw.line(surface, COLOR_WHITE, (x, y + TILE_SIZE // 2), 
                                     (x + TILE_SIZE, y + TILE_SIZE // 2), 3)
                elif tile == '.':
                    # Normal Pellet: centered small square or circle
                    px = x + TILE_SIZE // 2
                    py = y + TILE_SIZE // 2
                    pygame.draw.circle(surface, COLOR_PELLET, (px, py), TILE_SIZE // 8)
                elif tile == 'o':
                    # Power Pellet: larger pulsing circle (alternating frames)
                    # Pulsing logic handled by main tick count
                    px = x + TILE_SIZE // 2
                    py = y + TILE_SIZE // 2
                    ticks = pygame.time.get_ticks() // 200
                    if ticks % 2 == 0:
                        pygame.draw.circle(surface, COLOR_PELLET, (px, py), TILE_SIZE // 3)
