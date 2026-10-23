import os
import sys
import warnings 
import queue
import threading
import numpy as np
import sounddevice as sd
import torch
import dotenv
from kokoro import KPipeline

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
        
        # # Initializing Kokoro 82M with a custom blended Indian English voice matrix.
        # print("Loading Kokoro 82M Model... fingers crossed")
        # self.pipeline = KPipeline(lang_code=lang_code)
        # self.sample_rate = 24000 # standard for this model i think
        # self.audio_queue = queue.Queue()

        # print("Building custom Indian English voice blend...")
        # self.voice_tensor = self._create_indian_english_voice()
        # print("Voice blend is ready to roll!")

    def _initialize_model(self):
        if self.pipeline is not None:
            return

        print("Loading Kokoro Model, fingers crossed...")
        self.pipeline = KPipeline(lang_code=self.lang_code)

        if torch.cuda.is_available():
            print("Found an Nvidia GPU!")
            self.pipeline.model.to("cuda")

        else:
            print("No Nvida GPU found! Running on CPU.")

        # Checking if we have a saved copy of voice tensor, so we can skip blending time on startup
        if os.path.exists(self.voice_cache_path):
            print("Loading Cached voice blend...")
            self.voice_tensor = torch.load(
                self.voice_cache_path, 
                map_location="cuda" if torch.cuda.is_available() else "cpu"
                )

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