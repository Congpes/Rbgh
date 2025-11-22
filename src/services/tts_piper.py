import os
import shutil
import subprocess
import uuid
from typing import Optional


class PiperTTS:
    def __init__(
        self,
        piper_dir: str = os.path.join("data", "models", "piper", "piper"),
        model_filename: Optional[str] = None,
        output_dir: str = os.path.join("data", "samples"),
        length_scale: float = 1.15,  # Tốc độ: 1.0 = bình thường, >1.0 = chậm hơn, <1.0 = nhanh hơn
    ) -> None:
        self.piper_dir = piper_dir
        self.output_dir = output_dir
        self.length_scale = length_scale
        self.piper_dir = os.path.abspath(self.piper_dir)
        self.piper_exe = os.path.join(self.piper_dir, "piper.exe")
        if not os.path.isfile(self.piper_exe):
            raise FileNotFoundError(f"Không tìm thấy piper.exe tại: {self.piper_exe}")

        if model_filename is None:
            candidates = [f for f in os.listdir(self.piper_dir) if f.startswith("vi_VN-") and f.endswith((".onnx", ".pt"))]
            if not candidates:
                raise FileNotFoundError("Không tìm thấy model Piper vi_VN (*.onnx|*.pt) trong thư mục piper.")
            # ưu tiên .onnx
            candidates.sort(key=lambda n: (0 if n.endswith(".onnx") else 1, n))
            self.model_path = os.path.join(self.piper_dir, candidates[0])
        else:
            self.model_path = os.path.join(self.piper_dir, model_filename)

        if not os.path.isfile(self.model_path):
            raise FileNotFoundError(f"Không tìm thấy model Piper: {self.model_path}")

        os.makedirs(self.output_dir, exist_ok=True)

    def synthesize(self, text: str, out_wav_path: Optional[str] = None) -> str:
        if not text or not text.strip():
            raise ValueError("Text đầu vào rỗng")

        if out_wav_path is None:
            out_wav_path = os.path.join(self.output_dir, f"tts_{uuid.uuid4().hex}.wav")

        # Dùng đường dẫn tuyệt đối để đảm bảo ghi đúng nơi
        out_wav_path_abs = os.path.abspath(out_wav_path)
        out_dir = os.path.dirname(out_wav_path_abs)
        os.makedirs(out_dir, exist_ok=True)

        model_path_abs = os.path.abspath(self.model_path)

        # Piper đọc text từ stdin, không phải từ file
        # -f là output file (cần đường dẫn tuyệt đối)
        cmd = [
            self.piper_exe,
            "-m",
            model_path_abs,
            "-f",
            out_wav_path_abs,  # Output file với đường dẫn tuyệt đối
            "--length_scale",
            str(self.length_scale),  # Điều chỉnh tốc độ giọng nói
        ]

        try:
            # Tăng timeout cho text dài (ước tính ~1s cho mỗi 10 ký tự)
            estimated_time = max(30, len(text) // 10)
            # Truyền text qua stdin
            input_text = text.strip() + "\n"
            completed = subprocess.run(
                cmd,
                input=input_text,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                cwd=self.piper_dir,
                timeout=estimated_time,
            )
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"Piper timeout sau {estimated_time}s. Lệnh: {' '.join(cmd)} | Thư mục: {self.piper_dir}") from e
        if completed.returncode != 0:
            raise RuntimeError(f"Piper lỗi: {completed.stderr}\nSTDOUT: {completed.stdout}\nLệnh: {' '.join(cmd)}\nThư mục: {self.piper_dir}")

        if not os.path.isfile(out_wav_path_abs):
            raise RuntimeError("Piper không tạo được file âm thanh đầu ra")

        return out_wav_path_abs

    @staticmethod
    def is_available(piper_dir: str) -> bool:
        exe = os.path.join(piper_dir, "piper.exe")
        return os.path.isfile(exe)


