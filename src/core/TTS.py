import subprocess
import threading
import queue
import numpy as np
import sounddevice as sd
from piper import PiperVoice
import os

# I added these because I was getting memory allocation errors. Hopefully doesn't happen to you
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Also if it still happens, paste this in your terminal
""" Windows(Powershell)
$env:OPENBLAS_NUM_THREADS="1"
$env:OMP_NUM_THREADS="1"
$env:MKL_NUM_THREADS="1"
$env:VECLIB_MAXIMUM_THREADS="1"
$env:NUMEXPR_NUM_THREADS="1"
"""

""" Mac/Linux
export OPENBLAS_NUM_THREADS="1"
export OMP_NUM_THREADS="1"
export MKL_NUM_THREADS="1"
export VECLIB_MAXIMUM_THREADS="1"
export NUMEXPR_NUM_THREADS="1"
"""
# Or run this one-liner

# export OPENBLAS_NUM_THREADS="1"; export OMP_NUM_THREADS="1"; export MKL_NUM_THREADS="1"; export VECLIB_MAXIMUM_THREADS="1"; export NUMEXPR_NUM_THREADS="1"

class Wisdom_cowork_TTS:
    def __init__(self, model_path="en_US-amy-medium.onnx"): # if you want to change voice, you can just go to https://huggingface.co/rhasspy/piper-voices/tree/main and download the voice u want to use, just change the path for if you downloaded it somewhere else
        self.model_path = model_path
        self.voice = None
        self.sample_rate = 22050

    def initialize_model(self):
        # check if already loaded, don't want to load twice lol
        if self.voice is not None:
            return

        print(f"Loading Piper model ({self.model_path})...")

        try:
            self.voice = PiperVoice.load(self.model_path)
            self.sample_rate = self.voice.config.sample_rate
            print("Yay, model loaded sucessfully!")

        except Exception as e:
            print(f"Model load error: {str(e)}. Check your path or internet connection if downloading.")
            raise

    def speak(self, text):
        if not text.strip():
            print("Empty string, skipping...") # added log jic
            return

        self.initialize_model()
        print(f"Speaking: {text}")

        audio_queue = queue.Queue()

        def synthesis_worker():
            try:
                for chunk in self.voice.synthesize(text):
                    audio_bytes = chunk.audio_int16_bytes
                    audio_chunk = np.frombuffer(audio_bytes, dtype=np.int16)
                    audio_queue.put(audio_chunk)

            except Exception as e:
                print(f"Oops, synthesis error: {str(e)}")

            finally:
                audio_queue.put(None) # Signal end of stream


        worker = threading.Thread(target=synthesis_worker, daemon=True)
        worker.start()

        try:
            # open sounddevice stream
            stream = sd.OutputStream(samplerate=self.sample_rate, channels=1, dtype='int16')
            stream.start()

            while True:
                chunk = audio_queue.get()
                if chunk is None:
                    break

                stream.write(chunk)

            stream.stop()
            stream.close()

        except Exception as e:
            print(f"Audio playback error happened: {str(e)}")

        finally:
            worker.join()

# Lets test the script
if __name__ == "__main__":
    tts = Wisdom_cowork_TTS()

    # testing out a hardcoded string first, then user input
    # tts.speak("Hello world, testing the TTS system.")

    user_text = input("Enter text for TTS to speak: ")
    tts.speak(user_text)