import queue
import threading

import keyboard
import pyperclip
import numpy as np
from .config import DynSettings, dyn_settings
from .logs import logger
from .display_client import DisplayUnixClient
from .model import BasePhoneModel, GigaPhoneModel
from .recorder import MicroRecorder

__all__ = ["PhoneApp", "speech_grap_app"]


def queue_to_np_data(q: queue.Queue):
    tmp_arr = []
    while not q.empty():
        tmp_arr.append(q.get_nowait())
    return np.concatenate(tmp_arr)


class PhoneApp:

    def __init__(
        self,
        ds: DynSettings,
        mc: MicroRecorder,
        model: BasePhoneModel,
        displayer: DisplayUnixClient,
    ):
        self.ds = ds
        self.mc = mc
        self.model = model
        self.displayer = displayer
        self._record_flag = False
        self._stoped = threading.Event()

        keyboard.add_hotkey(self.ds.hotkey.value, self.on_activate)
        self.displayer.connect()

    def cb_model_result(self, text: str):
        logger.info('Recorded text: "%s"', text)
        pyperclip.copy(text)

    def on_activate(self):
        self._record_flag = not self._record_flag
        if self._record_flag:
            logger.debug("Recording...")
            self.displayer.send_command("PhoneGiga", "Recording...")
            self.mc.start()
            self.model.start_recording()
        else:
            logger.debug("Recording done")
            d1 = queue_to_np_data(self.mc.qdata)
            self.mc.stop()
            model_result = self.model.calc_recorded(d1, self.mc.samplerate)
            self.cb_model_result(model_result)
            logger.debug(f"Recording done in {self.mc.rec_time:.1f}s")
            self.displayer.send_command(
                "PhoneGiga", f"Recording done in {self.mc.rec_time:.1f}s"
            )

    def start(self):
        self._stoped.clear()
        self.displayer.send_command("PhoneGiga", "Service Started")

        try:
            self._stoped.wait()
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            self.stop()

    def stop(self):
        self.mc.stop()

    def __del__(self):
        self.stop()


def speech_grap_app():
    ds = dyn_settings()
    displayer = DisplayUnixClient(ds)
    recorder = MicroRecorder(ds)
    model = GigaPhoneModel(ds.model.value, ds.model_path.value)
    app = PhoneApp(ds, recorder, model, displayer)
    return app
