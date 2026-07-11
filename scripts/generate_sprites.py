import os
import urllib.request
import pygame

# Initialize pygame for offscreen surface loading
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

OUTPUT_DIR = "assets/images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

SOURCE_IMG_PATH = os.path.join(OUTPUT_DIR, "spritesheet_source.png")
SOURCE_URL = "https://raw.githubusercontent.com/SteveDunn/Pacman-TypeScript/master/img/spritesheet.png"

# Step 1: Ensure source spritesheet is downloaded
if not os.path.exists(SOURCE_IMG_PATH):
    print(f"Downloading source spritesheet from {SOURCE_URL}...")
    try:
        urllib.request.urlretrieve(SOURCE_URL, SOURCE_IMG_PATH)
        print("Source spritesheet successfully downloaded.")
    except Exception as e:
        print(f"Failed to download spritesheet: {e}")
        # Fallback to the scratch directory version if available
        scratch_path = r"C:\Users\paulf\.gemini\antigravity\brain\10fef084-bf07-4b29-b844-c2f0514bf2e6\scratch\sprites_stevedunn_master.png"
        if os.path.exists(scratch_path):
            import shutil
            shutil.copy(scratch_path, SOURCE_IMG_PATH)
            print("Copied source spritesheet from local scratch cache.")
        else:
            raise FileNotFoundError("Could not download or find source spritesheet.")

# Load the source spritesheet
sheet = pygame.image.load(SOURCE_IMG_PATH).convert_alpha()

def crop_and_save(rect: tuple, filename: str) -> None:
    x, y, w, h = rect
    sprite = sheet.subsurface((x, y, w, h))
    dest_path = os.path.join(OUTPUT_DIR, filename)
    pygame.image.save(sprite, dest_path)
    print(f"Saved sprite: {dest_path}")

# ==========================================
# 0. CROP MAZE BACKGROUND
# ==========================================
# Original arcade maze starts at x=1 in the spritesheet (shifted to align correctly)
crop_and_save((1, 0, 224, 248), "maze_background.png")

# ==========================================
# 1. CROP PACMAN SPRITES
# ==========================================
# Closed mouth (shared frame in index 488, 0)
crop_and_save((488, 0, 16, 16), "pacman_closed.png")

# Directions and open frame columns
pacman_coords = {
    "right": [(456, 0), (472, 0)],
    "left": [(456, 16), (472, 16)],
    "up": [(456, 32), (472, 32)],
    "down": [(456, 48), (472, 48)]
}

for dir_name, frames in pacman_coords.items():
    for idx, (x, y) in enumerate(frames):
        crop_and_save((x, y, 16, 16), f"pacman_{dir_name}_{idx + 1}.png")

# Dying frames (11 frames) starting at X=504, Y=0
for idx in range(11):
    x_pos = 504 + idx * 16
    crop_and_save((x_pos, 0, 16, 16), f"pacman_dying_{idx}.png")

# ==========================================
# 2. CROP GHOST SPRITES
# ==========================================
# Ghost color row offsets
ghost_rows = {
    "red": 64,
    "pink": 80,
    "cyan": 96,
    "orange": 112
}

for name, y_offset in ghost_rows.items():
    # Columns map to: Right (2 frames), Left (2 frames), Up (2 frames), Down (2 frames)
    coords = [
        ("right", 0, 456), ("right", 1, 472),
        ("left", 0, 488), ("left", 1, 504),
        ("up", 0, 520), ("up", 1, 536),
        ("down", 0, 552), ("down", 1, 568)
    ]
    for dir_name, frame, x in coords:
        crop_and_save((x, y_offset, 16, 16), f"ghost_{name}_{dir_name}_{frame}.png")

# ==========================================
# 3. CROP SCARED & FLASHING GHOSTS
# ==========================================
crop_and_save((584, 64, 16, 16), "ghost_frightened_blue_0.png")
crop_and_save((600, 64, 16, 16), "ghost_frightened_blue_1.png")
crop_and_save((616, 64, 16, 16), "ghost_frightened_white_0.png")
crop_and_save((632, 64, 16, 16), "ghost_frightened_white_1.png")

# ==========================================
# 4. CROP EATEN EYES
# ==========================================
crop_and_save((584, 80, 16, 16), "ghost_eyes_right.png")
crop_and_save((600, 80, 16, 16), "ghost_eyes_left.png")
crop_and_save((616, 80, 16, 16), "ghost_eyes_up.png")
crop_and_save((632, 80, 16, 16), "ghost_eyes_down.png")

print("All arcade-perfect sprites successfully cropped and saved!")
pygame.quit()
