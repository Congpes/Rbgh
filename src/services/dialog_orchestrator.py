from typing import Optional

from .tts_piper import PiperTTS
from .stt_vosk import VoskSTT


class DialogOrchestrator:
    def __init__(self, stt: Optional[VoskSTT] = None, tts: Optional[PiperTTS] = None) -> None:
        self.stt = stt or VoskSTT()
        self.tts = tts or PiperTTS()

    def stt_then_tts(self, wav_path: str) -> str:
        text = self.stt.transcribe_wav(wav_path)
        if not text:
            text = "Xin lỗi, tôi chưa nghe rõ. Bạn có thể nói lại không?"
        self.tts.synthesize(text)
        return text


