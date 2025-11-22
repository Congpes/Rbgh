import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.services.tts_piper import PiperTTS


def main():
    text = "Xin chào, đây là kiểm tra Piper và phát âm thanh."
    tts = PiperTTS()
    wav = tts.synthesize(text)
    print("TTS OK:", wav)
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(wav)
        pygame.mixer.music.play()
        import time
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        print("Playback OK")
    except Exception as e:
        print("Playback error:", e)


if __name__ == "__main__":
    main()


