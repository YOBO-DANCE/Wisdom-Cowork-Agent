import os
import sys
import warnings 
import queue
import threading
import gc
import numpy as np
import sounddevice as sd
import torch
from dotenv import load_dotenv
from kokoro import KPipeline

load_dotenv()

# Note: I remember that Windows users always have trouble with espeak, leaving this here so it doesn't break again
if sys.platform == "win32":
    espeak_path = r"C:\Program Files\eSpeak NG"
    # check path twice because why not lol
    if os.path.exists(espeak_path) and os.path.exists(espeak_path) and espeak_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + espeak_path

# I don't want clutter in the Command line so, I will use this
warnings.filterwarnings("ignore", category=UserWarning, module="torch.nn.modules.rnn")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.nn.utils.weight_norm")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.jit._script")

class TextToSpeech:

    def __init__(self, lang_code: str = "b", voice_cache_path: str = "indian_english_voice.pt"):
        self.lang_code = lang_code
        self.voice_cache_path = voice_cache_path
        self.sample_rate = 24000

        self.pipeline = None
        self.voice_tensor = None

    def _initialize_model(self):
        if self.pipeline is not None:
            return

        use_cuda = torch.cuda.is_available()
        gc.collect()

        if use_cuda:
            print("Found an Nvidia GPU! Loading directly to VRAM...")
            torch.set_default_device("cuda")
        else:
            print("No Nvidia GPU found! Initializing on CPU (please ensure background apps are closed if RAM is low)...")

        try:
            self.pipeline = KPipeline(lang_code=self.lang_code, repo_id='hexgrad/Kokoro-82M')
            if use_cuda:
                self.pipeline.model.to(torch.float16)
        finally:
            if use_cuda:
                torch.set_default_device("cpu")

        # Checking if we have a saved copy of voice tensor, so we can skip blending time on startup
        if os.path.exists(self.voice_cache_path):
            print("Loading Cached voice blend...")
            self.voice_tensor = torch.load(
                self.voice_cache_path, 
                map_location="cuda" if use_cuda else "cpu"
                )
            
            if use_cuda:
                self.voice_tensor = self.voice_tensor.to(torch.float16)

        else:
            print("Building Voice Blend, be patient please(This is a first time setup)...")
            bf_voice = self.pipeline.load_voice("bf_emma")
            hf_voice = self.pipeline.load_voice("hf_alpha")

            # I am going for a 70% british phonetic flow + 30% Hindi Tone, so change as you wish!
            self.voice_tensor = (0.7 * bf_voice) + (0.3 * hf_voice)

            # Saving it
            torch.save(self.voice_tensor, self.voice_cache_path)
            print(f"Voice Blend saved to {self.voice_cache_path}")

        print("Model and voice are ready to use!")

    def speak(self, text: str, speed: float = 1.0):
        # Synthesizes text and plays the audio seamlessly in one pass.
        if not text.strip():
            print("Empty string passed, skipping...")
            return

        self._initialize_model()

        print(f"Speaking Currently: {text}")

        audio_queue = queue.Queue()

        # Lets stream the audio now
        stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype='float32'
        )
        stream.start()

        # This Background worker will feed audio chunks into our stream buffer. It is powered by American Dream LOL
        def playback_worker():
            while True:
                chunk = audio_queue.get()

                if chunk is None:
                    audio_queue.task_done()
                    break

                stream.write(chunk)
                audio_queue.task_done()
        
        worker_thread = threading.Thread(target=playback_worker, daemon=True)
        worker_thread.start()

        try:
            with torch.inference_mode():
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

                        # Instant push to queue so the audio plays while our model is working hard to generate the rest
                        audio_queue.put(audio_np)

        finally:
            # Clean up time
            audio_queue.put(None)
            audio_queue.join()
            worker_thread.join()

            stream.stop()
            stream.close()

            gc.collect()

            if torch.cuda.is_available():
                torch.cuda.empty_cache()


# Quick test script block
if __name__ == "__main__":
    tts = TextToSpeech()

    test_prompt = str(input("Write what you want to say: "))

    tts.speak(test_prompt)