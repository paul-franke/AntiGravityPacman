import os
import pygame
from typing import Dict

# Audio constants
SAMPLE_RATE = 44100

class ArcadeSoundManager:
    """Handles loading and playing Namco WSG wavelets generated under 60Hz VBLANK interrupts."""

    def __init__(self) -> None:
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.initialized = False
        self.current_siren_channel: pygame.mixer.Channel = None

    def initialize_sounds(self) -> None:
        """Load all emulated WSG sound wavelets. Must be called after pygame.mixer.init()."""
        if self.initialized:
            return
        
        try:
            # Try initializing pygame mixer if not already done
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2)

            audio_dir = os.path.join("assets", "audio")
            sound_files = {
                "intro": "intro.wav",
                "waka": "waka.wav",
                "frightened": "frightened.wav",
                "death": "death.wav",
                "eat_ghost": "eat_ghost.wav",
                "siren1": "siren1.wav",
                "siren2": "siren2.wav",
                "siren3": "siren3.wav",
                "siren4": "siren4.wav",
                "siren5": "siren5.wav"
            }

            for name, filename in sound_files.items():
                path = os.path.join(audio_dir, filename)
                self.sounds[name] = pygame.mixer.Sound(path)
                
            self.initialized = True
        except Exception as e:
            print(f"Warning: Could not initialize sound system ({e}). Running in silent mode.")

    def play(self, name: str, loops: int = 0) -> None:
        """Play a loaded sound wavelet."""
        if not self.initialized or name not in self.sounds:
            return
            
        # If it's a siren or frightened loop, play on channel 0 to avoid overlapping
        if name in ("siren1", "siren2", "siren3", "siren4", "siren5", "frightened"):
            self.stop_siren()
            chan = pygame.mixer.Channel(0)
            chan.play(self.sounds[name], loops=loops)
            self.current_siren_channel = chan
        else:
            # Play short sound effects (waka, eat_ghost, death) on other channels
            self.sounds[name].play(loops=loops)

    def stop_siren(self) -> None:
        """Stop any playing background loop (siren or frightened)."""
        if self.current_siren_channel:
            self.current_siren_channel.stop()

    def stop_all(self) -> None:
        """Stop all currently playing sounds."""
        if not self.initialized:
            return
        pygame.mixer.stop()
