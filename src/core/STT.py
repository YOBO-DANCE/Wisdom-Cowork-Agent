import os
import sys
import time
import keyboard
import numpy as np
import pyaudio
from faster_whisper import WhisperModel

# Fix CUDA DLL loading on Windows for ctranslate2
if sys.platform == "win32":
    venv_base = sys.prefix
    nvidia_bin_dirs = [
        os.path.join(
            venv_base, "Lib", "site-packages", "nvidia", "cublas", "bin"
        ),
        os.path.join(
            venv_base, "Lib", "site-packages", "nvidia", "cudnn", "bin"
        ),
    ]
    for bin_dir in nvidia_bin_dirs:
        if os.path.exists(bin_dir):
            os.add_dll_directory(bin_dir)
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]

# Audio Parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024


class PushToTalkSTT:

    def __init__(
        self,
        model_size: str = "base.en",
        device: str = "cuda",
        compute_type: str = "float16",
        hotkey: str = "space",
    ):
        """Initializes Faster-Whisper on CUDA with Push-To-Talk controls."""
        print(
            f"[STT] Loading Faster-Whisper ({model_size}) on {device.upper()}..."
        )

        try:
            self.model = WhisperModel(
                model_size, device=device, compute_type=compute_type
            )
            print("[STT] Model loaded successfully on CUDA GPU.")
        except Exception as e:
            print(
                f"[STT] CUDA load failed ({e}). Falling back to CPU int8..."
            )
            self.model = WhisperModel("base.en", device="cpu", compute_type="int8")

        self.audio = pyaudio.PyAudio()
        self.hotkey = hotkey

    def listen_hold_to_talk(self) -> str:
        """Records audio while the hotkey is HELD down.

        Stops and transcribes immediately when released.
        """
        print(f"\n[STT] Ready! Press and HOLD [{self.hotkey.upper()}] to speak...")

        # Wait until user presses the key
        keyboard.wait(self.hotkey)

        print(
            f"[STT] Recording... (Keep holding [{self.hotkey.upper()}])"
        )

        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []

        # Record while the key remains held down
        while keyboard.is_pressed(self.hotkey):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except Exception as e:
                print(f"[STT] Stream read error: {e}")
                break

        print(
            f"[STT] [{self.hotkey.upper()}] released. Transcribing audio..."
        )

        stream.stop_stream()
        stream.close()

        return self._transcribe_frames(frames)

    def listen_toggle_to_talk(self) -> str:
        """Taps hotkey ONCE to start recording, taps hotkey AGAIN to stop."""
        print(
            f"\n[STT] Ready! Press [{self.hotkey.upper()}] ONCE to start recording..."
        )

        # Wait for key tap to start
        while not keyboard.is_pressed(self.hotkey):
            time.sleep(0.05)

        # Wait briefly for key release so it doesn't immediately trigger stop
        while keyboard.is_pressed(self.hotkey):
            time.sleep(0.05)

        print(
            f"[STT] Recording started! Speak freely. Press [{self.hotkey.upper()}] again when finished..."
        )

        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        frames = []

        # Keep capturing audio until the hotkey is pressed a second time
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)

            if keyboard.is_pressed(self.hotkey):
                # Debounce release
                while keyboard.is_pressed(self.hotkey):
                    time.sleep(0.05)
                break

        print("[STT] Recording stopped. Transcribing audio...")

        stream.stop_stream()
        stream.close()

        return self._transcribe_frames(frames)

    def _transcribe_frames(self, frames: list[bytes]) -> str:
        """Converts raw audio frame bytes into normalized float32 array

        and passes to Faster-Whisper.
        """
        if not frames:
            return ""

        raw_audio_bytes = b"".join(frames)
        audio_data = (
            np.frombuffer(raw_audio_bytes, dtype=np.int16).astype(np.float32)
            / 32768.0
        )

        # Transcribe full continuous audio block
        segments, _ = self.model.transcribe(
            audio_data, beam_size=5, language="en", vad_filter=False
        )

        transcription = " ".join([seg.text.strip() for seg in segments])
        return transcription.strip()

    def close(self):
        """Release audio resources."""
        self.audio.terminate()


# Quick Test Block
if __name__ == "__main__":
    # Choose your preferred hotkey (e.g., 'space', 'right ctrl', 'f8', 'alt')
    stt = PushToTalkSTT(
        model_size="base.en", device="cuda", hotkey="right ctrl"
    )

    try:
        while True:
            # Change to stt.listen_toggle_to_talk() if you prefer toggle mode!
            text = stt.listen_hold_to_talk()
            if text:
                print(f'\n>>> Recognized Prompt: "{text}"\n')
                if "exit" in text.lower() or "quit" in text.lower():
                    print("Exiting STT test...")
                    break
    finally:
        stt.close()