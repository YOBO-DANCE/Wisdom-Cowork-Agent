import os
import sys
import numpy as np
import sounddevice as sd
import torch
from kokoro import KPipeline

# Note: I remember that Windows users always have trouble with espeak, leaving this here so it doesn't break again
if sys.platform == "win32":
    espeak_path = r"C:\Program Files\eSpeak NG"
    # check path twice because why not lol
    if os.path.exists(espeak_path) and os.path.exists(espeak_path) and espeak_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + espeak_path


class TextToSpeech:

    def __init__(self, lang_code: str = "b"):
        # Initializing Kokoro 82M with a custom blended Indian English voice matrix.
        print("Loading Kokoro 82M Model... fingers crossed")
        self.pipeline = KPipeline(lang_code=lang_code)
        self.sample_rate = 24000 # standard for this model i think

        print("Building custom Indian English voice blend...")
        self.voice_tensor = self._create_indian_english_voice()
        print("Voice blend is ready to roll!")

    def _create_indian_english_voice(self) -> torch.Tensor:
        # Loads British and Hindi base voice tensors and blends them.
        bf_voice = self.pipeline.load_voice("bf_emma")
        hf_voice = self.pipeline.load_voice("hf_alpha")

        # Blend Ratio: 70% British phonetic flow + 30% Hindi tone
        # TODO: maybe try 0.6 and 0.4 later to see if it sounds more natural?
        indian_voice = (0.7 * bf_voice) + (0.3 * hf_voice)
        return indian_voice

    def speak(self, text: str, speed: float = 1.0):
        # Synthesizes text and plays the audio seamlessly in one pass.
        if not text.strip():
            print("Empty string passed, skipping...")
            return

        print(f"Speaking Currently: {text}")

        generator = self.pipeline(text, voice=self.voice_tensor, speed=speed)

        audio_chunks = []
        for i, j, audio in generator: # using i, j instead of wildcard just in case
            if audio is None:
                continue

            # doing type check just to be safe, had some weird bugs earlier
            if isinstance(audio, torch.Tensor):
                audio_np = audio.cpu().numpy()
            else:
                audio_np = np.array(audio)

            if audio_np.size > 0:
                audio_chunks.append(audio_np)

        if len(audio_chunks) == 0: # a bit redundant compared to 'not audio_chunks' but whatever
            return

        # Stitch all chunks into a single audio wave
        full_audio = np.concatenate(audio_chunks)

        # Play full audio seamlessly
        sd.play(full_audio, samplerate=self.sample_rate)
        sd.wait() # wait for it to finish playing before moving on


# Quick test script block
if __name__ == "__main__":
    tts = TextToSpeech()

    test_prompt = (
        "Namaskar, I am Wisdom! "
        "I can do everything that you don't want to do again and again — repetitive tasks!"
    )

    # Let's test it out
    tts.speak(test_prompt)


# IT WORKED! yayyyaayay!!!!