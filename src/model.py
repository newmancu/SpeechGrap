import onnx_asr
from onnx_asr.loader import ModelNames, ModelTypes


class BasePhoneModel:

    def start_recording(self):
        pass

    def calc_recorded(self, data, samplerate: int) -> str:
        pass


class GigaPhoneModel(BasePhoneModel):
    def __init__(
        self,
        model: str | ModelNames | ModelTypes = "gigaam-v2-rnnt",
        model_path: str | None = None,
    ):
        super().__init__()
        self.model = onnx_asr.load_model(model, path=model_path)

    def start_recording(self):
        pass

    def calc_recorded(self, data, samplerate: int) -> str:
        all_words = self.model.recognize(data, sample_rate=samplerate)
        if isinstance(all_words, list):
            ret = " ".join(all_words)
        else:
            ret = all_words
        return ret
