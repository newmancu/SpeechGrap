import queue
from time import time

import numpy as np
import sounddevice as sd

from .config import DynSettings


class MicroRecorder:

    def __init__(self, ds: DynSettings):
        self.ds = ds
        self.qdata = queue.Queue()
        self.phone_stream: sd.RawInputStream | None = None
        self._end_time = self._start_time = time()

    @property
    def rec_time(self) -> float:
        return self._end_time - self._start_time

    def phone_callback(self, indata, frames, cb_time, status):
        self._end_time = time()
        self.qdata.put(
            np.frombuffer(indata, dtype=self.ds.dtype.value).reshape(
                -1, copy=True
            )
        )

    def start(self):
        self._end_time = self._start_time = time()

        self.device_info = sd.query_devices(self.ds.device.value, "input")
        self.samplerate = int(self.device_info["default_samplerate"])

        self.phone_stream = sd.RawInputStream(
            samplerate=self.samplerate,
            blocksize=8000,
            device=self.ds.device.value,
            dtype=self.ds.dtype.value,
            channels=1,
            callback=self.phone_callback,
        )
        self.phone_stream.start()

    def stop(self):
        if self.phone_stream:
            self.phone_stream.stop()
            self.phone_stream.close()

    def __del__(self):
        self.stop()
