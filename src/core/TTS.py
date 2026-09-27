import os
import sys
import re
import numpy as np
import torch
import sounddevice as sd
from kokoro import KPipeline

class TexttoSpeech:

    def __init__(self, langcode: str = "b", default_voice: str = "bf_emma"):
        print("[TTS] Loading Kokoro 82M model...")
        self.pipeline = KPipeline(lang_code=langcode)
        self.sample_rate = 24000

        print("[TTS] Building custom Indian English voice blend...")
        self.voice_tensor = self.create_indian_english_voice()
        print("[TTS] Voice blend ready.")

    def create_indian_english_voice(self) -> torch.Tensor:
        # Adds necessary voices for the module to use
        bf_voice = self.pipeline.load_voice("bf_emma")
        hf_voice = self.pipeline.load_voice("hf_alpha")

        # Creates the indian (70% british english + 30% indian english)
        indian_voice = (bf_voice * 0.7) + (hf_voice * 0.3)
        return indian_voice

    def speak(self, text: str, speed: float = 1.0):
        if not text.strip():
            return

        print(f"[TTS] Synthesizing: '{text}'")

        generator = self.pipeline(
            text, voice=self.voice_tensor, speed=speed
        )

        audio_chunks = []

        for _, _, audio in generator:
            for _, _, audio in generator:
                if audio is not None:
                    audio_chunks.append(audio)

            if not audio_chunks:
                print(f"[TTS] WARNING: No audio chunk generated.")
                return

            full_audio = np.concatenate(audio_chunks)

            sd.play(full_audio, samplerate=self.sample_rate)
            sd.wait()


# Quick Independent Test
if __name__ in "__main__":
    tts = TexttoSpeech()

    test_prompt = "Namaskar, I am Wisdom! I can do everything that you don't want to do again and again — Repetative Tasks!"

    tts.speak(test_prompt)