import array
import math
import pygame
from typing import Dict, List, Tuple

# Audio constants
SAMPLE_RATE = 22050
FRAMES_PER_SEC = 60
SAMPLES_PER_FRAME = SAMPLE_RATE // FRAMES_PER_SEC  # ~367 samples

class ArcadeSoundManager:
    """Handles programmatic retro synthesis of Pacman sound effects, synced to 60Hz logic."""

    def __init__(self) -> None:
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.initialized = False
        self.current_siren_channel: pygame.mixer.Channel = None

    def initialize_sounds(self) -> None:
        """Synthesize all retro sounds. Must be called after pygame.mixer.init()."""
        if self.initialized:
            return
        
        try:
            # Try initializing pygame mixer if not already done
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)

            # Generate sounds
            self.sounds["intro"] = self._synthesize_intro()
            self.sounds["waka"] = self._synthesize_waka()
            self.sounds["siren"] = self._synthesize_siren()
            self.sounds["frightened"] = self._synthesize_frightened()
            self.sounds["death"] = self._synthesize_death()
            self.sounds["eat_ghost"] = self._synthesize_eat_ghost()
            
            self.initialized = True
        except Exception as e:
            print(f"Warning: Could not initialize sound system ({e}). Running in silent mode.")

    def play(self, name: str, loops: int = 0) -> None:
        """Play a synthesized sound by name."""
        if not self.initialized or name not in self.sounds:
            return
        # If it's a siren or frightened loop, play on channel 0 to avoid overlapping
        if name == "siren":
            self.stop_siren()
            chan = pygame.mixer.Channel(0)
            chan.play(self.sounds[name], loops=loops)
            self.current_siren_channel = chan
        elif name == "frightened":
            self.stop_siren()
            chan = pygame.mixer.Channel(0)
            chan.play(self.sounds[name], loops=loops)
            self.current_siren_channel = chan
        else:
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

    def _create_sound_from_samples(self, samples: array.array) -> pygame.mixer.Sound:
        """Convert a 16-bit signed audio array into a pygame Sound object."""
        # Convert array of signed shorts to bytes
        sound_bytes = samples.tobytes()
        return pygame.mixer.Sound(buffer=sound_bytes)

    def _generate_tone(self, freq: float, length_frames: int, wave_type: str = "square", volume: float = 0.2) -> array.array:
        """Generate raw PCM sample array for a given wave type and frequency."""
        arr = array.array("h")  # signed 16-bit integers
        num_samples = length_frames * SAMPLES_PER_FRAME
        
        # Max positive value for 16-bit signed audio
        max_amplitude = int(32767 * volume)

        for i in range(num_samples):
            t = i / SAMPLE_RATE
            val = 0
            if wave_type == "square":
                # Square wave: positive amplitude if sin >= 0, else negative
                val = max_amplitude if math.sin(2.0 * math.pi * freq * t) >= 0 else -max_amplitude
            elif wave_type == "triangle":
                # Triangle wave: linear rise and fall
                period = 1.0 / freq
                pos_in_period = t % period
                if pos_in_period < period / 2.0:
                    val = int(-max_amplitude + (4.0 * max_amplitude * pos_in_period / period))
                else:
                    val = int(3.0 * max_amplitude - (4.0 * max_amplitude * pos_in_period / period))
            elif wave_type == "sine":
                val = int(max_amplitude * math.sin(2.0 * math.pi * freq * t))
            arr.append(val)
        return arr

    def _synthesize_intro(self) -> pygame.mixer.Sound:
        """Synthesize the iconic retro intro theme using square waves."""
        # Note frequencies (Hz)
        B4 = 494.0
        B5 = 988.0
        FS5 = 740.0
        DS5 = 622.0
        C5 = 523.0
        C6 = 1047.0
        G5 = 784.0
        E5 = 659.0
        F5 = 698.0
        G5_ = 831.0
        A5 = 880.0
        AS5 = 932.0

        # Note sequence: (frequency, duration in frames)
        melody: List[Tuple[float, int]] = [
            (B4, 5), (B5, 5), (FS5, 5), (DS5, 5), (B5, 3), (FS5, 7), (DS5, 10),
            (C5, 5), (C6, 5), (G5, 5), (E5, 5), (C6, 3), (G5, 7), (E5, 10),
            (B4, 5), (B5, 5), (FS5, 5), (DS5, 5), (B5, 3), (FS5, 7), (DS5, 10),
            (DS5, 3), (E5, 3), (F5, 3), (FS5, 3), (G5, 3), (G5_, 3), (A5, 3), (AS5, 3), (B5, 8)
        ]

        full_arr = array.array("h")
        for freq, duration in melody:
            full_arr.extend(self._generate_tone(freq, duration, wave_type="square", volume=0.15))
        return self._create_sound_from_samples(full_arr)

    def _synthesize_waka(self) -> pygame.mixer.Sound:
        """Synthesize the 'waka waka' pellet munch sound (modulating triangular/square wave)."""
        # Duration: ~6 frames (0.1s)
        duration_frames = 6
        num_samples = duration_frames * SAMPLES_PER_FRAME
        arr = array.array("h")
        
        # Linearly sweep frequency up and down to simulate mouth opening/closing
        max_amplitude = int(32767 * 0.12)
        for i in range(num_samples):
            t = i / SAMPLE_RATE
            # Modulate frequency from 250Hz to 600Hz
            progress = i / num_samples
            freq = 250.0 + (350.0 * math.sin(math.pi * progress))
            
            # Custom square/pulse wave
            val = max_amplitude if math.sin(2.0 * math.pi * freq * t) >= 0.2 else -max_amplitude
            arr.append(val)
        return self._create_sound_from_samples(arr)

    def _synthesize_siren(self) -> pygame.mixer.Sound:
        """Synthesize the repeating background siren."""
        # Duration: 30 frames (0.5s)
        duration_frames = 30
        num_samples = duration_frames * SAMPLES_PER_FRAME
        arr = array.array("h")
        max_amplitude = int(32767 * 0.08)

        for i in range(num_samples):
            t = i / SAMPLE_RATE
            # Modulate frequency from 300Hz to 400Hz and back
            progress = i / num_samples
            freq = 300.0 + (100.0 * math.sin(2.0 * math.pi * progress))
            
            # Triangle wave for a smoother arcade feel
            period = 1.0 / freq
            pos = t % period
            if pos < period / 2.0:
                val = int(-max_amplitude + (4.0 * max_amplitude * pos / period))
            else:
                val = int(3.0 * max_amplitude - (4.0 * max_amplitude * pos / period))
            arr.append(val)
        return self._create_sound_from_samples(arr)

    def _synthesize_frightened(self) -> pygame.mixer.Sound:
        """Synthesize the frightened ghost ticking/warning sound."""
        # Duration: 24 frames (0.4s)
        duration_frames = 24
        num_samples = duration_frames * SAMPLES_PER_FRAME
        arr = array.array("h")
        max_amplitude = int(32767 * 0.1)

        for i in range(num_samples):
            t = i / SAMPLE_RATE
            # Stepped frequency shifts: alternates between 150Hz and 250Hz
            freq = 150.0 if (i // (num_samples // 4)) % 2 == 0 else 250.0
            
            # Simple square wave
            val = max_amplitude if math.sin(2.0 * math.pi * freq * t) >= 0 else -max_amplitude
            arr.append(val)
        return self._create_sound_from_samples(arr)

    def _synthesize_death(self) -> pygame.mixer.Sound:
        """Synthesize the Pacman death sound (cascading descending sweeps)."""
        duration_frames = 72  # 1.2 seconds
        num_samples = duration_frames * SAMPLES_PER_FRAME
        arr = array.array("h")
        max_amplitude = int(32767 * 0.15)

        for i in range(num_samples):
            t = i / SAMPLE_RATE
            progress = i / num_samples
            
            # Modulate frequency to go down, with sharp periodic resets
            phase = (progress * 12) % 1.0  # 12 steps
            freq = 800.0 * (1.0 - phase) + 100.0
            
            # Apply volume envelope (fading out)
            volume_envelope = max_amplitude * (1.0 - progress)
            
            val = int(volume_envelope if math.sin(2.0 * math.pi * freq * t) >= 0 else -volume_envelope)
            arr.append(val)
        return self._create_sound_from_samples(arr)

    def _synthesize_eat_ghost(self) -> pygame.mixer.Sound:
        """Synthesize the sound when Pacman eats a ghost."""
        duration_frames = 18  # 0.3s
        num_samples = duration_frames * SAMPLES_PER_FRAME
        arr = array.array("h")
        max_amplitude = int(32767 * 0.15)

        for i in range(num_samples):
            t = i / SAMPLE_RATE
            progress = i / num_samples
            
            # Rapid upward slide
            freq = 150.0 + (1000.0 * progress)
            
            val = int(max_amplitude if math.sin(2.0 * math.pi * freq * t) >= 0 else -max_amplitude)
            arr.append(val)
        return self._create_sound_from_samples(arr)
