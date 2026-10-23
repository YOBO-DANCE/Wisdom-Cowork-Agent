import os
import sys
import queue
import threading
import numpy as np
import sounddevice as sd
import torch
from kokoro import KPipeline

if sys.platform == "win32":
    espeak_path = r"C:\Program Files\eSpeak NG"
    if os.path.exists(espeak_path) and os.path.exists(espeak_path) and espeak_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + espeak_path


class TextToSpeech:

    def __init__(self, lang_code: str = "b", voice_cache_path: str = "indian_english_voice.pt"):
        self.lang_code = lang_code
        self.voice_cache_path = voice_cache_path
        self.sample_rate = 24000
        
        # Defer pipeline loading so class instantiation is instantaneous
        self.pipeline = None
        self.voice_tensor = None

    def _initialize_model(self):
        """Lazy-loads the pipeline and voice tensor only when needed."""
        if self.pipeline is not None:
            return

        print("Loading Kokoro 82M Model...")
        self.pipeline = KPipeline(lang_code=self.lang_code)

        # Check if we have a pre-saved voice tensor to skip blending time on startup
        if os.path.exists(self.voice_cache_path):
            print("Loading cached custom voice blend...")
            self.voice_tensor = torch.load(self.voice_cache_path)
        else:
            print("Building custom Indian English voice blend for the first time...")
            bf_voice = self.pipeline.load_voice("bf_emma")
            hf_voice = self.pipeline.load_voice("hf_alpha")
            
            # Blend Ratio: 50% British phonetic flow + 50% Hindi tone
            self.voice_tensor = (0.5 * bf_voice) + (0.5 * hf_voice)
            
            # Cache it for future lightning-fast startups
            torch.save(self.voice_tensor, self.voice_cache_path)
            print(f"Voice blend cached to {self.voice_cache_path}!")

        print("Model and voice are ready!")

    def speak(self, text: str, speed: float = 1.0):
        """Synthesizes text and streams audio instantly using a background worker thread."""
        if not text.strip():
            print("Empty string passed, skipping...")
            return

        # Ensure model is loaded right before speaking
        self._initialize_model()

        print(f"Speaking Currently: {text}")

        audio_queue = queue.Queue()

        # Open a live, non-blocking audio output stream
        stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        stream.start()

        # Background worker thread that feeds audio chunks into the stream buffer
        def playback_worker():
            while True:
                chunk = audio_queue.get()
                if chunk is None:  # Sentinel value to exit worker loop
                    audio_queue.task_done()
                    break
                stream.write(chunk)
                audio_queue.task_done()

        worker_thread = threading.Thread(target=playback_worker, daemon=True)
        worker_thread.start()

        try:
            generator = self.pipeline(text, voice=self.voice_tensor, speed=speed)

            for _, _, audio in generator:
                if audio is None:
                    continue

                if isinstance(audio, torch.Tensor):
                    audio_np = audio.cpu().numpy().astype(np.float32)
                else:
                    audio_np = np.array(audio, dtype=np.float32)

                if audio_np.size > 0:
                    audio_np = np.squeeze(audio_np)
                    # Push instantly to queue so audio plays while the model generates the rest
                    audio_queue.put(audio_np)

        finally:
            # Signal worker to finish up and clean resources
            audio_queue.put(None)
            audio_queue.join()
            worker_thread.join()

            stream.stop()
            stream.close()


# Quick test script block
if __name__ == "__main__":
    # Initialization is now instantaneous!
    tts = TextToSpeech()

    test_prompt = (
        "Namaskar, I am Wisdom! "
        "I can do everything that you don't want to do again and again — repetitive tasks!"
    )

    tts.speak(test_prompt)