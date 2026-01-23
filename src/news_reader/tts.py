import time
import os
from typing import Optional
import soundfile as sf
try:
    from kokoro import KPipeline
    import torch
except ImportError:
    KPipeline = None

class KokoroTTS:
    def __init__(self, lang_code: str = 'a', default_voice: str = 'af_heart'):
        if KPipeline is None:
            raise ImportError("kokoro library is not installed. Please install it with 'pip install kokoro torch soundfile'")
        
        self.pipeline = KPipeline(lang_code=lang_code)
        self.default_voice = default_voice

    def generate_wav(self, text: str, output_path: str, voice: Optional[str] = None) -> float:
        """
        Generates a .wav file from text and returns the time taken in seconds.
        """
        voice = voice or self.default_voice
        start_time = time.time()
        
        # Kokoro's pipeline returns a generator of (graphemes, phonemes, audio)
        generator = self.pipeline(text, voice=voice)
        
        # For simplicity, we'll collect all audio chunks and concatenate if needed
        # but usually for a single news article, we might just take the first if it's short
        # or combine them. Kokoro handles splitting long text.
        
        all_audio = []
        for i, (gs, ps, audio) in enumerate(generator):
            all_audio.append(audio)
        
        if not all_audio:
            raise ValueError("No audio was generated.")
        
        # If there's more than one chunk, concatenate them
        if len(all_audio) > 1:
            import numpy as np
            combined_audio = np.concatenate(all_audio)
        else:
            combined_audio = all_audio[0]
            
        sf.write(output_path, combined_audio, 24000)
        
        end_time = time.time()
        return end_time - start_time
