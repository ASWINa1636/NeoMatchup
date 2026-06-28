"""
NeoPlato Sound Effects Manager
===============================
Optional pygame.mixer integration for sound effects.
Gracefully falls back to silent mode if pygame is not installed.
"""
import os

_PYGAME_AVAILABLE = False

try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    _PYGAME_AVAILABLE = True
except (ImportError, Exception):
    pass


class SoundManager:
    """
    Manages sound effect playback using pygame.mixer.
    Falls back silently if pygame is not available.
    """
    def __init__(self, enabled: bool = True):
        self._enabled = enabled and _PYGAME_AVAILABLE
        self._sounds = {}
        self._volume = 0.5
        if self._enabled:
            self._generate_sounds()
    
    def _generate_sounds(self):
        if not _PYGAME_AVAILABLE:
            return
        try:
            import numpy as np
            sample_rate = 44100
            self._sounds["click"] = self._make_tone(freq=800, duration=0.05, volume=0.3, sample_rate=sample_rate)
            self._sounds["win"] = self._make_chord(freqs=[523, 659, 784], duration=0.4, volume=0.4, sample_rate=sample_rate)
            self._sounds["lose"] = self._make_tone(freq=200, duration=0.5, volume=0.3, sample_rate=sample_rate, fade_out=True)
            self._sounds["coin"] = self._make_tone(freq=1200, duration=0.15, volume=0.3, sample_rate=sample_rate)
            self._sounds["flip"] = self._make_tone(freq=600, duration=0.08, volume=0.2, sample_rate=sample_rate)
            self._sounds["drop"] = self._make_tone(freq=150, duration=0.2, volume=0.4, sample_rate=sample_rate)
            self._sounds["error"] = self._make_tone(freq=120, duration=0.3, volume=0.3, sample_rate=sample_rate)
            self._sounds["move"] = self._make_tone(freq=500, duration=0.04, volume=0.2, sample_rate=sample_rate)
        except ImportError:
            self._enabled = False
    
    @staticmethod
    def _make_tone(freq, duration, volume, sample_rate, fade_out=False):
        import numpy as np
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        wave = np.sin(2 * np.pi * freq * t) * volume
        if fade_out:
            fade = np.linspace(1.0, 0.0, n_samples)
            wave *= fade
        wave_int = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((wave_int, wave_int))
        return pygame.sndarray.make_sound(stereo)
    
    @staticmethod
    def _make_chord(freqs, duration, volume, sample_rate):
        import numpy as np
        n_samples = int(sample_rate * duration)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        wave = sum(np.sin(2 * np.pi * f * t) for f in freqs)
        wave = wave / len(freqs) * volume
        fade = np.linspace(1.0, 0.0, n_samples)
        wave *= fade
        wave_int = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((wave_int, wave_int))
        return pygame.sndarray.make_sound(stereo)
    
    def play(self, sound_name: str):
        if not self._enabled:
            return
        sound = self._sounds.get(sound_name)
        if sound:
            sound.set_volume(self._volume)
            sound.play()
    
    def set_volume(self, volume: float):
        self._volume = max(0.0, min(1.0, volume))
    
    def set_enabled(self, enabled: bool):
        self._enabled = enabled and _PYGAME_AVAILABLE
    
    @property
    def enabled(self) -> bool:
        return self._enabled
    
    @property
    def available(self) -> bool:
        return _PYGAME_AVAILABLE
