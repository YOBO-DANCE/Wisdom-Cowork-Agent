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
    if os.path.exists(espeak_path) and espeak_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + espeak_path

# I don't want clutter in the Command line so, I will use this
warnings.filterwarnings("ignore", category=UserWarning, module="torch.nn.modules.rnn")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.nn.utils.weight_norm")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch.jit._script")

class TextToSpeech:

    def __init__(self, lang_code: str = "b", voice_cache_path: str = None, blend_ratio: float = 0.7):
        self.lang_code = lang_code
        self.voice_cache_path = voice_cache_path or os.environ.get("TTS_VOICE_CACHE_PATH", "indian_english_voice.pt")
        self.sample_rate = 24000
        self.blend_ratio = max(0.0, min(1.0, blend_ratio))

        self.pipeline = None
        self.voice_tensor = None

    def _initialize_model(self):
        if self.pipeline is not None:
            return

        use_cuda = torch.cuda.is_available()
        gc.collect()

        if use_cuda:
            print("Found an Nvidia GPU! Model will be moved to VRAM after init...")
        else:
            print("No Nvidia GPU found! Initializing on CPU (please ensure background apps are closed if RAM is low)...")

        try:
            self.pipeline = KPipeline(lang_code=self.lang_code, repo_id='hexgrad/Kokoro-82M')
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize KPipeline (lang_code={self.lang_code}). "
                f"Check Hugging Face connectivity and repo 'hexgrad/Kokoro-82M'. "
                f"Original error: {e}"
            ) from e

        if use_cuda:
            self.pipeline.model.to("cuda").to(torch.float16)
            if hasattr(torch, "compile"):
                try:
                    self.pipeline.model = torch.compile(self.pipeline.model, mode="reduce-overhead")
                except Exception:
                    pass

        if os.path.exists(self.voice_cache_path):
            print("Loading Cached voice blend...")
            try:
                self.voice_tensor = torch.load(
                    self.voice_cache_path,
                    map_location="cuda" if use_cuda else "cpu",
                    weights_only=True
                )
            except Exception as e:
                print(f"Cache corrupted or unreadable ({e}), rebuilding voice blend...")
                try:
                    os.remove(self.voice_cache_path)
                except OSError:
                    pass
                self.voice_tensor = None

        if self.voice_tensor is None:
            print("Building Voice Blend, be patient please (first time setup)...")
            try:
                bf_voice = self.pipeline.load_voice("bf_emma")
                hf_voice = self.pipeline.load_voice("hf_alpha")
            except Exception as e:
                raise RuntimeError(f"Failed to load voices 'bf_emma'/'hf_alpha': {e}") from e

            self.voice_tensor = (self.blend_ratio * bf_voice) + ((1.0 - self.blend_ratio) * hf_voice)

            if use_cuda:
                self.voice_tensor = self.voice_tensor.to("cuda").to(torch.float16)

            try:
                torch.save(self.voice_tensor, self.voice_cache_path)
                print(f"Voice Blend saved to {self.voice_cache_path}")
            except Exception as e:
                print(f"Warning: Failed to cache voice blend ({e})")

        print("Model and voice are ready to use!")

        if use_cuda:
            with torch.inference_mode():
                _ = list(self.pipeline("warmup", voice=self.voice_tensor, speed=1.0))

    def speak(self, text: str, speed: float = 1.0):
        if not text.strip():
            print("Empty string passed, skipping...")
            return

        self._initialize_model()

        print(f"Speaking Currently: {text}")

        audio_queue = queue.Queue()
        stream = None
        stream_started = False
        worker_thread = None

        def playback_worker():
            while True:
                chunk = audio_queue.get()
                try:
                    if chunk is None:
                        break
                    if stream_started and stream is not None:
                        stream.write(chunk)
                except Exception as e:
                    print(f"Playback worker error: {e}")
                    break
                finally:
                    audio_queue.task_done()

        try:
            stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            )
            stream.start()
            stream_started = True

            worker_thread = threading.Thread(target=playback_worker, daemon=True)
            worker_thread.start()

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
                        audio_queue.put(audio_np)

        except KeyboardInterrupt:
            print("\nPlayback interrupted.")
        except Exception as e:
            print(f"TTS generation error: {e}")
        finally:
            audio_queue.put(None)
            audio_queue.join()

            if worker_thread and worker_thread.is_alive():
                worker_thread.join(timeout=2.0)

            if stream_started and stream is not None:
                try:
                    stream.stop()
                except Exception:
                    pass
                try:
                    stream.close()
                except Exception:
                    pass

            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


# Quick test script block
if __name__ == "__main__":
    tts = TextToSpeech()

    test_prompt = str(input("Write what you want to say: "))

    tts.speak(test_prompt)