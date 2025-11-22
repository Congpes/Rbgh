import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.services.stt_vosk import VoskSTT
from src.services.tts_piper import PiperTTS


def main():
    if len(sys.argv) < 2:
        print("Cách dùng: python scripts/example_stt_tts.py <path_to_wav_mono_16k>")
        sys.exit(1)

    wav_path = sys.argv[1]
    stt = VoskSTT()
    text = stt.transcribe_wav(wav_path)
    print("STT:", text)

    tts = PiperTTS()
    out = tts.synthesize(text if text else "Xin chào. Đây là kiểm thử Piper tiếng Việt.")
    print("TTS out:", out)


if __name__ == "__main__":
    main()


