import os
import uuid
from typing import Optional

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write as wav_write


class AudioRecorder:
    def __init__(self, sample_rate: int = 16000, channels: int = 1, dtype: str = "int16") -> None:
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self._stream = None
        self._frames = []

    def record(self, seconds: float, out_wav_path: Optional[str] = None) -> str:
        if seconds <= 0:
            raise ValueError("seconds phải > 0")
        if out_wav_path is None:
            out_wav_path = os.path.join("data", "samples", f"mic_{uuid.uuid4().hex}.wav")

        os.makedirs(os.path.dirname(out_wav_path), exist_ok=True)

        num_frames = int(self.sample_rate * seconds)
        audio = sd.rec(frames=num_frames, samplerate=self.sample_rate, channels=self.channels, dtype=self.dtype)
        sd.wait()

        # Đảm bảo là mảng numpy (N, channels)
        arr = np.asarray(audio)
        if self.channels == 1 and arr.ndim == 2:
            arr = arr.reshape(-1)

        # scipy cần sample_rate và mảng numpy
        wav_write(out_wav_path, self.sample_rate, arr)
        return out_wav_path

    # Press-to-talk API
    def start(self) -> None:
        if self._stream is not None:
            return
        self._frames = []

        def callback(indata, frames, time, status):  # type: ignore
            if status:
                # Có thể log status nếu cần
                pass
            self._frames.append(indata.copy())

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=self.dtype,
            callback=callback,
        )
        self._stream.start()

    def stop(self, out_wav_path: Optional[str] = None) -> str:
        if self._stream is None:
            raise RuntimeError("Chưa start ghi âm")
        self._stream.stop()
        self._stream.close()
        self._stream = None

        if not self._frames:
            raise RuntimeError("Không có dữ liệu ghi âm")

        import numpy as np
        data = np.concatenate(self._frames, axis=0)
        if self.channels == 1 and data.ndim == 2:
            data = data.reshape(-1)

        if out_wav_path is None:
            out_wav_path = os.path.join("data", "samples", f"mic_{uuid.uuid4().hex}.wav")
        os.makedirs(os.path.dirname(out_wav_path), exist_ok=True)
        wav_write(out_wav_path, self.sample_rate, data)
        self._frames = []
        return out_wav_path


