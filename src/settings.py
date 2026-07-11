"""Game settings and constants for AntiGravityPacman."""

# Screen and Tile size
ARCADE_TILE_SIZE = 8
SCALE = 3
TILE_SIZE = ARCADE_TILE_SIZE * SCALE  # 24 pixels

COLS = 28
ROWS = 36
SCREEN_WIDTH = COLS * TILE_SIZE    # 672 pixels
SCREEN_HEIGHT = ROWS * TILE_SIZE  # 864 pixels

FPS = 60

# Game Speeds (in pixels per frame)
# Since TILE_SIZE = 24, choosing speeds that divide 24 ensures perfect grid alignment.
PACMAN_SPEED_NORMAL = 2
PACMAN_SPEED_FRIGHTENED = 2
GHOST_SPEED_NORMAL = 2
GHOST_SPEED_FRIGHTENED = 1
GHOST_SPEED_EATEN = 4  # Return to ghost house quickly

# Colors (Standard arcade hex colors converted to RGB)
COLOR_BLACK = (0, 0, 0)
COLOR_WALL = (33, 33, 255)         # Neon Blue
COLOR_PACMAN = (255, 255, 0)       # Yellow
COLOR_WHITE = (222, 222, 255)       # Pellet color / text
COLOR_PELLET = (255, 183, 174)     # Warm peach/pinkish pellet color
COLOR_RED = (255, 0, 0)            # Blinky
COLOR_PINK = (255, 184, 255)       # Pinky
COLOR_CYAN = (0, 255, 255)         # Inky
COLOR_ORANGE = (255, 184, 82)      # Clyde
COLOR_BLUE_FRIGHTENED = (33, 33, 255)  # Dark Blue
COLOR_WHITE_FRIGHTENED = (222, 222, 255) # Flashing state

# Game States
STATE_START = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_READY = 3
STATE_GAME_OVER = 4
STATE_VICTORY = 5
STATE_DYING = 6
