import os
import math
import wave
import struct
from typing import List, Tuple

# Audio parameters
SAMPLE_RATE = 44100
FPS = 60
SAMPLES_PER_FRAME = SAMPLE_RATE // FPS  # 735 samples

# Namco WSG 32-step 4-bit waveform patterns
ROM_WAVES = [
    # Wave 0 (Triangle): classic smooth tone, used for sirens and waka
    [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0],
    # Wave 1 (Square): 50% duty cycle, used for intro melody and ticking
    [15]*16 + [0]*16,
    # Wave 2 (Pulse 25%): 25% duty cycle
    [15]*8 + [0]*24,
    # Wave 3 (Pulse 12.5%): 12.5% duty cycle
    [15]*4 + [0]*28,
    # Wave 4 (Sawtooth): ramping up from 0 to 15
    [int(15 * (i / 31.0)) for i in range(32)],
    # Wave 5 (Chirp): sine-like curve
    [int(7.5 + 7.5 * math.sin(2 * math.pi * (i / 32.0))) for i in range(32)],
    # Wave 6: pulse variant
    [15]*12 + [0]*20,
    # Wave 7: pulse variant
    [15]*20 + [0]*12
]

def save_wav(filename: str, samples: List[int]) -> None:
    """Save 16-bit signed PCM samples to a mono WAV file."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setparams((1, 2, SAMPLE_RATE, len(samples), 'NONE', 'not compressed'))
        for val in samples:
            # Clamp to 16-bit signed integer limits
            val_clamp = max(-32768, min(32767, int(val)))
            wav_file.writeframes(struct.pack('<h', val_clamp))

def synthesize_wsg(frames_data: List[List[Tuple[int, float, float]]]) -> List[int]:
    """
    Synthesize WSG audio from a list of frame states.
    Each frame has voice parameters: (waveform_idx, frequency_hz, volume_0_to_15) for each of the 3 channels.
    """
    samples = []
    # Phase accumulators for the 3 WSG channels
    phases = [0.0, 0.0, 0.0]
    
    for frame in frames_data:
        # Pad channels to 3 if less
        while len(frame) < 3:
            frame.append((0, 0.0, 0.0))
            
        for _ in range(SAMPLES_PER_FRAME):
            sample_val = 0.0
            active_channels = 0
            
            for c in range(3):
                wave_idx, freq, vol = frame[c]
                if vol > 0.0 and freq > 0.0:
                    # Look up ROM wave value
                    step_idx = int(phases[c]) % 32
                    w_val = ROM_WAVES[wave_idx][step_idx]
                    
                    # Convert 4-bit amplitude (0..15) to signed PCM offset (-1.0 to 1.0)
                    offset = (w_val - 7.5) / 7.5
                    
                    # Apply multiplier: vol/15
                    sample_val += offset * 32767.0 * (vol / 15.0)
                    active_channels += 1
                    
                    # Advance phase pointer
                    phases[c] += 32.0 * freq / SAMPLE_RATE
                    
            if active_channels > 0:
                # Divide by number of active channels to prevent clipping, and apply master volume (0.35)
                samples.append(int((sample_val / active_channels) * 0.35))
            else:
                samples.append(0)
                
    return samples

def make_intro() -> List[int]:
    """Melody data for the game startup theme."""
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

    melody: List[Tuple[float, int]] = [
        (B4, 5), (B5, 5), (FS5, 5), (DS5, 5), (B5, 3), (FS5, 7), (DS5, 10),
        (C5, 5), (C6, 5), (G5, 5), (E5, 5), (C6, 3), (G5, 7), (E5, 10),
        (B4, 5), (B5, 5), (FS5, 5), (DS5, 5), (B5, 3), (FS5, 7), (DS5, 10),
        (DS5, 3), (E5, 3), (F5, 3), (FS5, 3), (G5, 3), (G5_, 3), (A5, 3), (AS5, 3), (B5, 12)
    ]

    frames = []
    for freq, duration in melody:
        for _ in range(duration):
            # Channel 0: Square wave melody
            # Channel 1: Square wave harmony (1 octave below)
            ch0 = (1, freq, 12.0)
            ch1 = (1, freq / 2.0, 8.0)
            frames.append([ch0, ch1])
    return synthesize_wsg(frames)

def make_waka() -> List[int]:
    """Waka munch sound effect (pitch chirp sweeping up and down)."""
    frames = []
    duration = 6  # 0.1 seconds
    for f in range(duration):
        progress = f / duration
        # Frequency sweeps up and down
        freq = 250.0 + (350.0 * math.sin(math.pi * progress))
        # Custom pulse wave
        ch0 = (4, freq, 12.0)
        frames.append([ch0])
    return synthesize_wsg(frames)

def make_siren(low_freq: float, high_freq: float, duration_frames: int) -> List[int]:
    """Siren background sound (looping pitch modulation)."""
    frames = []
    for f in range(duration_frames):
        progress = f / duration_frames
        freq = low_freq + (high_freq - low_freq) * math.sin(2.0 * math.pi * progress)
        # Triangle wave for smooth sound
        ch0 = (0, freq, 10.0)
        frames.append([ch0])
    return synthesize_wsg(frames)

def make_frightened() -> List[int]:
    """Frightened ghost warning siren (pulsing low sweeps)."""
    frames = []
    duration = 24  # 0.4 seconds
    frames_per_sweep = 6
    for f in range(duration):
        progress = (f % frames_per_sweep) / (frames_per_sweep - 1)
        # Sweep down from 320Hz to 180Hz
        freq = 320.0 - progress * 140.0
        ch0 = (0, freq, 11.0)  # Wave 0 (Triangle)
        frames.append([ch0])
    return synthesize_wsg(frames)

def make_death() -> List[int]:
    """Death sound (11 rapid upward sweeps descending in base pitch)."""
    frames = []
    total_sweeps = 11
    frames_per_sweep = 6
    total_frames = total_sweeps * frames_per_sweep

    for f in range(total_frames):
        sweep_idx = f // frames_per_sweep
        frame_in_sweep = f % frames_per_sweep
        progress = frame_in_sweep / (frames_per_sweep - 1) if frames_per_sweep > 1 else 0.0
        
        # Base frequency descends
        base_freq = 450.0 - sweep_idx * 35.0
        # Each chirp sweeps UP to 2.2x of the base frequency
        freq = base_freq + (base_freq * 1.2) * progress
        
        # Volume decays overall
        vol = 14.0 * (1.0 - f / total_frames)
        ch0 = (1, freq, vol)  # Wave 1 (Square)
        frames.append([ch0])
    return synthesize_wsg(frames)

def make_eat_ghost() -> List[int]:
    """Eating a ghost sound (upward slide chirp)."""
    frames = []
    duration = 18  # 0.3 seconds
    for f in range(duration):
        progress = f / duration
        freq = 150.0 + (1050.0 * progress)
        ch0 = (5, freq, 14.0)
        frames.append([ch0])
    return synthesize_wsg(frames)

def main() -> None:
    """Generate and write all sound effect WAV wavelets."""
    audio_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'audio')
    print(f"Generating sound effects into: {audio_dir}")
    
    save_wav(os.path.join(audio_dir, 'intro.wav'), make_intro())
    save_wav(os.path.join(audio_dir, 'waka.wav'), make_waka())
    save_wav(os.path.join(audio_dir, 'frightened.wav'), make_frightened())
    save_wav(os.path.join(audio_dir, 'death.wav'), make_death())
    save_wav(os.path.join(audio_dir, 'eat_ghost.wav'), make_eat_ghost())
    
    # Generate 5 sirens of increasing pitch and loop speed (Dossier-accurate escalation)
    save_wav(os.path.join(audio_dir, 'siren1.wav'), make_siren(250.0, 350.0, 30))
    save_wav(os.path.join(audio_dir, 'siren2.wav'), make_siren(280.0, 380.0, 26))
    save_wav(os.path.join(audio_dir, 'siren3.wav'), make_siren(310.0, 410.0, 22))
    save_wav(os.path.join(audio_dir, 'siren4.wav'), make_siren(340.0, 440.0, 18))
    save_wav(os.path.join(audio_dir, 'siren5.wav'), make_siren(380.0, 480.0, 14))
    
    print("All sounds generated successfully!")

if __name__ == '__main__':
    main()
