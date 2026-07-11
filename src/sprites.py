import os
import pygame
from typing import Dict, Tuple
from src.settings import TILE_SIZE

# Directions mapping to filenames
DIR_MAP = {
    (0, -1): "up",
    (0, 1): "down",
    (-1, 0): "left",
    (1, 0): "right",
    (0, 0): "left"  # Default when stopped
}

# Ghost names mapping to spritesheet color groups
GHOST_COLOR_MAP = {
    "blinky": "red",
    "pinky": "pink",
    "inky": "cyan",
    "clyde": "orange"
}

class SpriteLoader:
    """Loads, scales (to 48x48), and caches all retro pixel-art tile bitmaps from disk."""

    def __init__(self, asset_dir: str = "assets/images") -> None:
        self.asset_dir = asset_dir
        self.cache: Dict[str, pygame.Surface] = {}
        self.target_size = TILE_SIZE * 2  # 48x48 pixels (2:1 scale ratio relative to 24x24 tiles)

    def load_sprites(self) -> None:
        """Load and cache all sprites. Must be called after pygame display is initialized."""
        # A. Load Pacman Sprites
        self._load_and_scale("pacman_closed.png", "pacman_closed")
        for dir_name in ["up", "down", "left", "right"]:
            for frame in [1, 2]:
                name = f"pacman_{dir_name}_{frame}"
                self._load_and_scale(f"{name}.png", name)

        # B. Load Normal Ghost Sprites
        for color_name in ["red", "pink", "cyan", "orange"]:
            for dir_name in ["up", "down", "left", "right"]:
                for frame in [0, 1]:
                    name = f"ghost_{color_name}_{dir_name}_{frame}"
                    self._load_and_scale(f"{name}.png", name)

        # C. Load Scared Ghosts
        for frame in [0, 1]:
            self._load_and_scale(f"ghost_frightened_blue_{frame}.png", f"ghost_frightened_blue_{frame}")
            self._load_and_scale(f"ghost_frightened_white_{frame}.png", f"ghost_frightened_white_{frame}")

        # D. Load Eaten Eyes
        for dir_name in ["up", "down", "left", "right"]:
            name = f"ghost_eyes_{dir_name}"
            self._load_and_scale(f"{name}.png", name)

        # E. Load Pacman Dying Sprites
        for frame in range(11):
            name = f"pacman_dying_{frame}"
            self._load_and_scale(f"{name}.png", name)

        # F. Load Maze Background
        self._load_maze_background()

    def _load_maze_background(self) -> None:
        path = os.path.join(self.asset_dir, "maze_background.png")
        try:
            surf = pygame.image.load(path).convert()
            # Scale from 224x248 to 672x744 (3x scale factor)
            self.maze_background = pygame.transform.scale(surf, (672, 744))
            
            # Create flashed version (replace blue (33, 33, 255) and (0, 0, 255) with white)
            self.maze_background_flash = self.maze_background.copy()
            arr = pygame.PixelArray(self.maze_background_flash)
            arr.replace((33, 33, 255), (222, 222, 255))
            arr.replace((0, 0, 255), (222, 222, 255))
            del arr
        except Exception as e:
            print(f"Error loading maze background: {e}")
            # Fallback
            self.maze_background = pygame.Surface((672, 744))
            self.maze_background.fill((0, 0, 0))
            self.maze_background_flash = pygame.Surface((672, 744))
            self.maze_background_flash.fill((255, 255, 255))

    def get_maze_background(self, flash: bool) -> pygame.Surface:
        """Retrieve the scaled maze background Surface."""
        return self.maze_background_flash if flash else self.maze_background

    def _load_and_scale(self, filename: str, cache_key: str) -> None:
        path = os.path.join(self.asset_dir, filename)
        try:
            # Load with transparency
            sprite = pygame.image.load(path).convert_alpha()
            # Scale up to 48x48 using nearest-neighbor scaling to keep pixels crisp
            scaled_sprite = pygame.transform.scale(sprite, (self.target_size, self.target_size))
            self.cache[cache_key] = scaled_sprite
        except Exception as e:
            print(f"Error loading sprite {path}: {e}")
            # Create a fallback colored block in case of missing files to prevent crashing
            fallback = pygame.Surface((self.target_size, self.target_size), pygame.SRCALPHA)
            fallback.fill((255, 0, 255, 128))  # Magenta placeholder
            self.cache[cache_key] = fallback

    def get_pacman_sprite(self, dir_x: int, dir_y: int, frame_idx: int) -> pygame.Surface:
        """Retrieve Pacman sprite based on direction and frame index (0-3)."""
        # Frame index cycle: 0 -> closed, 1 -> semi-open, 2 -> wide-open, 3 -> semi-open
        if frame_idx == 0:
            return self.cache["pacman_closed"]
        
        dir_name = DIR_MAP.get((dir_x, dir_y), "left")
        frame_val = 1 if frame_idx in (1, 3) else 2
        
        key = f"pacman_{dir_name}_{frame_val}"
        return self.cache.get(key, self.cache["pacman_closed"])

    def get_pacman_dying_sprite(self, frame_idx: int) -> pygame.Surface:
        """Retrieve Pacman dying animation sprite based on frame index (0-10)."""
        key = f"pacman_dying_{frame_idx}"
        return self.cache.get(key, self.cache["pacman_closed"])

    def get_ghost_sprite(self, name: str, dir_x: int, dir_y: int, frame_idx: int, 
                         state: str, frightened_timer: int) -> pygame.Surface:
        """Retrieve Ghost sprite based on color, direction, frame index, and state."""
        # 1. Eaten state (just eyes)
        if state == "eaten":
            dir_name = DIR_MAP.get((dir_x, dir_y), "up")
            return self.cache.get(f"ghost_eyes_{dir_name}", self.cache["pacman_closed"])

        # 2. Frightened state (blue or white flashing)
        if state == "frightened":
            # Flash between blue and white if timer is low (< 2 seconds) and triggers flashing
            # Frightened timer is in frames (60Hz)
            if frightened_timer < 120 and (frightened_timer // 15) % 2 == 0:
                key = f"ghost_frightened_white_{frame_idx}"
            else:
                key = f"ghost_frightened_blue_{frame_idx}"
            return self.cache.get(key, self.cache["pacman_closed"])

        # 3. Normal states (chase or scatter)
        dir_name = DIR_MAP.get((dir_x, dir_y), "up")
        color_name = GHOST_COLOR_MAP.get(name.lower(), "red")
        key = f"ghost_{color_name}_{dir_name}_{frame_idx}"
        return self.cache.get(key, self.cache["pacman_closed"])
