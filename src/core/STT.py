import os
import queue
import sys
import numpy as np
import pyaudio
from faster_whisper import WhisperModel

# Audio Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000  # Faster-Whisper expects 16kHz audio
CHUNK = 1024  # Buffer read size

# Voice Activity Detection (VAD) Tuning
ENERGY_THRESHOLD = 500  # Audio volume cutoff to trigger recording
SILENCE_DURATION = 1.2  # Seconds of silence required to mark "end of speech"


class SpeechToText:

    def __init__(
        self, model_size: str = "base.en", device: str = "cuda", compute_type: str = "float16"
    ):
        """Initializes Faster-Whisper on CUDA with an automatic CPU fallback."""
        print(f"[STT] Loading Faster-Whisper ({model_size}) on {device.upper()}...")

        try:
            self.model = WhisperModel(
                model_size, device=device, compute_type=compute_type
            )
            print("[STT] Model successfully loaded on CUDA GPU.")
        except Exception as e:
            print(f"[STT] CUDA initialization failed ({e}). Falling back to CPU...")
            self.model = WhisperModel("base.en", device="cpu", compute_type="int8")
            print("[STT] Model successfully loaded on CPU.")

        self.audio = pyaudio.PyAudio()

    def listen_and_transcribe(self) -> str:
        """Monitors microphone stream, records when speech is detected,

        and returns the transcribed text once silence is reached.
        """
        stream = self.audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )

        print("\n[STT] Listening... (Speak into your microphone)")

        frames = []
        is_speaking = False
        silent_chunks = 0
        max_silent_chunks = int((RATE / CHUNK) * SILENCE_DURATION)

        while True:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                audio_chunk = np.frombuffer(data, dtype=np.int16)

                # Calculate root-mean-square (RMS) energy level
                energy = np.sqrt(np.mean(audio_chunk.astype(np.float32) ** 2))

                # Check if speech threshold is breached
                if energy > ENERGY_THRESHOLD:
                    if not is_speaking:
                        print("[STT] Speech detected! Recording...")
                        is_speaking = True

                    frames.append(data)
                    silent_chunks = 0  # Reset silence counter

                elif is_speaking:
                    # User was speaking, but current chunk is quiet
                    frames.append(data)
                    silent_chunks += 1

                    # Stop recording when silence duration threshold is reached
                    if silent_chunks >= max_silent_chunks:
                        print("[STT] Speech ended. Processing audio...")
                        break

            except KeyboardInterrupt:
                print("\n[STT] Listening interrupted.")
                stream.stop_stream()
                stream.close()
                return ""

        stream.stop_stream()
        stream.close()

        if not frames:
            return ""

        # Convert raw binary PCM audio bytes into a normalized Float32 numpy array
        raw_audio_bytes = b"".join(frames)
        audio_data = (
            np.frombuffer(raw_audio_bytes, dtype=np.int16).astype(np.float32)
            / 32768.0
        )

        # Transcribe with Faster-Whisper
        segments, _ = self.model.transcribe(
            audio_data,
            beam_size=5,
            language="en",
            vad_filter=True,  # Built-in Whisper VAD filtering
        )

        # Combine text segments
        transcription = " ".join(
            [segment.text.strip() for segment in segments]
        )
        return transcription.strip()

    def close(self):
        """Cleanly releases microphone resource."""
        self.audio.terminate()


# --- Quick Independent Test ---
if __name__ == "__main__":
    stt = SpeechToText(
        model_size="base.en", device="cuda", compute_type="float16"
    )

    try:
        while True:
            text = stt.listen_and_transcribe()
            if text:
                print(f'\n>>> Recognized Text: "{text}"')
                if "exit" in text.lower() or "quit" in text.lower():
                    print("Exiting STT test...")
                    break
    finally:
        stt.close()