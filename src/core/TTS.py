import os
import sys
import re
import numpy as np
import torch

# Audio Output Library
import sounddevice as sd

# Kokoro 82M Pipeline
from kokoro import KPipeline

class TexttoSpeech:

    def __init__(self, langcode: str = "b", default_voice: str = "bf_emma"):
        print("[TTS] Loading Kokoro 82M model...")
        self.pipeline = KPipeline(lang_code=langcode)
        self.sample_rate = 24000

        print("[TTS] Building custom Indian English voice blend...")
        self.voice_tensor = self._create_indian_english_voice()
        print("[TTS] Voice blend ready.")