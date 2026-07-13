import os
import sys
import pygame

# Make sure we can import from src if needed, but not required since we're self-contained.
# Game speed and window parameters
FPS = 60
WIDTH, HEIGHT = 600, 400

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_CYAN = (0, 255, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_RED = (255, 0, 0)

def main() -> None:
    # Initialize Pygame and audio mixer
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Namco WSG Sound Test & VBLANK Validator")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Courier", 18, bold=True)

    # Locate generated WAV files
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'audio')
    
    sound_files = {
        "intro": "intro.wav",
        "waka": "waka.wav",
        "siren": "siren.wav",
        "frightened": "frightened.wav",
        "death": "death.wav",
        "eat_ghost": "eat_ghost.wav"
    }

    sounds = {}
    load_errors = {}
    for key, val in sound_files.items():
        path = os.path.join(audio_dir, val)
        if os.path.exists(path):
            try:
                sounds[key] = pygame.mixer.Sound(path)
            except Exception as e:
                load_errors[key] = str(e)
        else:
            load_errors[key] = "File not found. Run makesounds.py first."

    # Loop siren tracker
    current_loop_name = None
    loop_channel = pygame.mixer.Channel(0)

    # VBLANK hook frame ticks counter
    vblank_ticks = 0

    print("Namco WSG Sound Test window initialized at 60Hz.")
    print("Press 1-6 keys to play sounds, Space to stop loop sounds.")

    running = True
    while running:
        # 1. Lock VBLANK rate to 60Hz
        clock.tick(FPS)
        vblank_ticks += 1

        # 2. VBLANK Interrupt Input Processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1 and "intro" in sounds:
                    sounds["intro"].play()
                elif event.key == pygame.K_2 and "waka" in sounds:
                    sounds["waka"].play()
                elif event.key == pygame.K_3 and "siren" in sounds:
                    loop_channel.stop()
                    loop_channel.play(sounds["siren"], loops=-1)
                    current_loop_name = "siren"
                elif event.key == pygame.K_4 and "frightened" in sounds:
                    loop_channel.stop()
                    loop_channel.play(sounds["frightened"], loops=-1)
                    current_loop_name = "frightened"
                elif event.key == pygame.K_5 and "death" in sounds:
                    sounds["death"].play()
                elif event.key == pygame.K_6 and "eat_ghost" in sounds:
                    sounds["eat_ghost"].play()
                elif event.key == pygame.K_SPACE:
                    loop_channel.stop()
                    current_loop_name = None

        # 3. Draw Sound Test Interface
        screen.fill(COLOR_BLACK)

        title = font.render("Namco WSG Sound Test & VBLANK Hook", True, COLOR_CYAN)
        screen.blit(title, (20, 20))
        
        info = font.render(f"Simulated VBLANK Frame Count: {vblank_ticks}", True, COLOR_WHITE)
        screen.blit(info, (20, 50))

        # Render list of keys and sound states
        y_pos = 90
        instructions = [
            ("1", "intro (melodic square wave)", "intro"),
            ("2", "waka (pellet munch chirp)", "waka"),
            ("3", "siren (background loop - ch 0)", "siren"),
            ("4", "frightened (ghost ticking - ch 0)", "frightened"),
            ("5", "death (falling sweeps)", "death"),
            ("6", "eat_ghost (upward slide chirp)", "eat_ghost"),
            ("Space", "Stop Channel 0 loop", None)
        ]

        for key_str, desc, s_key in instructions:
            if s_key in load_errors:
                status_color = COLOR_RED
                status_str = f"[Error: {load_errors[s_key]}]"
            elif s_key == current_loop_name and s_key is not None:
                status_color = COLOR_YELLOW
                status_str = "[LOOPING]"
            elif s_key is not None and pygame.mixer.get_busy() and s_key in sounds and any(pygame.mixer.Channel(i).get_sound() == sounds[s_key] for i in range(1, 8)):
                status_color = COLOR_CYAN
                status_str = "[PLAYING]"
            else:
                status_color = COLOR_WHITE
                status_str = "[READY]"

            if s_key is None:
                status_str = ""
                
            line = font.render(f"[{key_str}] - {desc}", True, COLOR_WHITE)
            status = font.render(status_str, True, status_color)
            
            screen.blit(line, (40, y_pos))
            screen.blit(status, (450, y_pos))
            y_pos += 30

        footer = font.render("Esc: Quit Sound Test", True, COLOR_WHITE)
        screen.blit(footer, (20, y_pos + 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
