import os
from typing import Generator, Optional, List

try:
    from vosk import Model, KaldiRecognizer
except Exception as e:
    raise ImportError("Cần cài đặt 'vosk' (pip install vosk)") from e

import wave
import json


class VoskSTT:
    def __init__(self, model_dir: str = os.path.join("data", "models", "vosk", "vosk-model-vn-0.4")) -> None:
        if not os.path.isdir(model_dir):
            raise FileNotFoundError(f"Không tìm thấy thư mục model Vosk: {model_dir}")
        self.model_dir = model_dir
        self.model = Model(self.model_dir)

    def transcribe_wav(self, wav_path: str, grammar_phrases: Optional[List[str]] = None) -> str:
        if not os.path.isfile(wav_path):
            raise FileNotFoundError(f"Không tìm thấy file wav: {wav_path}")

        with wave.open(wav_path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in (16000, 8000):
                raise ValueError("WAV phải mono, 16-bit, 8k/16kHz")

            # Nếu có grammar, dùng nhận dạng ràng buộc cụm từ để tăng độ chính xác
            if grammar_phrases:
                try:
                    grammar_json = json.dumps(grammar_phrases, ensure_ascii=False)
                    rec = KaldiRecognizer(self.model, wf.getframerate(), grammar_json)
                except Exception:
                    rec = KaldiRecognizer(self.model, wf.getframerate())
            else:
                rec = KaldiRecognizer(self.model, wf.getframerate())
            rec.SetWords(True)

            result_text = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    # Nhận kết quả từng phần (có thể bỏ qua nếu chỉ cần final)
                    pass
            # Lấy kết quả cuối
            final = rec.FinalResult()
            try:
                obj = json.loads(final)
                text = obj.get("text", "").strip()
            except Exception:
                text = ""
            return text


