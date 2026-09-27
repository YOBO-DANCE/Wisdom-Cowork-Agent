import os
import sys
import time
import keyboard
import numpy as np
import pyaudio
from faster_whisper import WhisperModel

# TODO: Clean up this DLL hack later, but it works for now on windows 
if sys.platform == "win32":
    venv_path = sys.prefix
    # paths to cuda libs for ctranslate2 
    nvidia_bin_dirs = [
        os.path.join(venv_path, "Lib", "site-packages", "nvidia", "cublas", "bin"),
        os.path.join(venv_path, "Lib", "site-packages", "nvidia", "cudnn", "bin"),
    ]
    for d in nvidia_bin_dirs:
        if os.path.exists(d):
            os.add_dll_directory(d)
            os.environ["PATH"] = d + os.pathsep + os.environ["PATH"]

# Global Audio Settings - Don't change these unless you know what you're doing
AUDIO_FORMAT = pyaudio.paInt16
NUM_CHANNELS = 1
SAMPLE_RATE = 16000
BUFFER_SIZE = 1024


class PushToTalkSTT:
    def __init__(self, model_size="base.en", device="cuda", compute_type="float16", hotkey="space"):
        # init faster whisper 
        print(f"Loading model {model_size} on {device}...")
        
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            print("Loaded fine on GPU!")
        except Exception as err:
            print(f"Oops, GPU load failed: {err}. Falling back to CPU.")
            # fallback to cpu if cuda acts up
            self.model = WhisperModel("base.en", device="cpu", compute_type="int8")

        self.pyaud = pyaudio.PyAudio() # need to call terminate later!!
        self.hotkey = hotkey

    def listen_hold_to_talk(self):
        # Records audio while holding key down
        print(f"\nReady. Hold down [{self.hotkey}] and speak...")

        keyboard.wait(self.hotkey)
        print("Recording... keep holding...")

        # open stream
        stream = self.pyaud.open(
            format=AUDIO_FORMAT,
            channels=NUM_CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=BUFFER_SIZE,
        )

        audio_chunks = []

        while keyboard.is_pressed(self.hotkey):
            try:
                chunk_data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
                audio_chunks.append(chunk_data)
            except Exception as e:
                print(f"error reading stream: {e}")
                break

        print("Key released, transcribing...")

        stream.stop_stream()
        stream.close()

        return self._transcribe_frames(audio_chunks)

    def listen_toggle_to_talk(self):
        print(f"\nPress [{self.hotkey}] once to start, once to stop.")

        while not keyboard.is_pressed(self.hotkey):
            time.sleep(0.05)

        # wait for release so it doesn't immediately toggle off
        while keyboard.is_pressed(self.hotkey):
            time.sleep(0.05)

        print("Recording started! Talk away...")

        stream = self.pyaud.open(
            format=AUDIO_FORMAT,
            channels=NUM_CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=BUFFER_SIZE,
        )

        audio_chunks = []

        while True:
            data = stream.read(BUFFER_SIZE, exception_on_overflow=False)
            audio_chunks.append(data)

            if keyboard.is_pressed(self.hotkey):
                # debounce a bit
                while keyboard.is_pressed(self.hotkey):
                    time.sleep(0.05)
                break

        print("Stopped recording. Processing...")

        stream.stop_stream()
        stream.close()

        return self._transcribe_frames(audio_chunks)

    def _transcribe_frames(self, frames):
        if len(frames) == 0:
            return ""

        # join all bytes and convert to numpy array 
        raw_data = b"".join(frames)
        audio_arr = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32) / 32768.0

        # run whisper model
        segments, info = self.model.transcribe(
            audio_arr, 
            beam_size=5, 
            language="en", 
            vad_filter=False
        )

        # combine segments into single string
        text = ""
        for seg in segments:
            text += seg.text + " "
            
        return text.strip()

    def close(self):
        # cleanup pyaudio instance
        self.pyaud.terminate()


if __name__ == "__main__":
    # testing out right ctrl since spacebar gets triggered by other stuff sometimes
    stt = PushToTalkSTT(model_size="base.en", device="cuda", hotkey="right ctrl")

    try:
        while True:
            # remember you can use listen_toggle_to_talk too
            result_text = stt.listen_hold_to_talk()
            
            if result_text != "":
                print(f'\nGot text: "{result_text}"\n')
                
                if "exit" in result_text.lower() or "stop" in result_text.lower():
                    print("Exiting loop...")
                    break
    except KeyboardInterrupt:
        print("Interrupted by user, cleaning up.")
    finally:
        stt.close()