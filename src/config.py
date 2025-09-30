from dataclasses import dataclass
from functools import cache
import os
from typing import Generic, TypeVar

T = TypeVar("T")


class DynField(Generic[T]):
    def __init__(self, v: T):
        self.value = v


@dataclass
class DynSettings:
    hotkey: DynField[str] = DynField("ctrl+alt+r")
    device: DynField[int] = DynField(0)
    dtype: DynField[str] = DynField("float32")
    display_socket: DynField[str] = DynField("float32")
    display_notifier_is_on: DynField[bool] = DynField(True)
    model: DynField[str] = DynField("gigaam-v2-rnnt")
    model_path: DynField[str | None] = DynField(None)


@cache
def dyn_settings() -> DynSettings:
    # hotkey
    hotkey = os.getenv("SG_HOTKEY", "ctrl+alt+r").strip()
    # Microphone
    device = int(os.getenv("SG_PHONE_DEVICE", "0").strip())
    dtype = os.getenv("SG_PHONE_DTYPE", "float32").strip()
    # display
    display_socket = os.getenv(
        "SG_DISPLAY_SOCKET", "/tmp/display_notification/socket.sock"
    ).strip()
    display_notifier_is_on = not (
        os.getenv("SG_DISPLAY_NOTIFIER_IS_ON", "1").strip().lower()
        in ("0", "no", "false", "f", "n", "")
    )
    # model
    model = os.getenv("SG_MODEL", "").strip()
    model = model if model else "gigaam-v2-rnnt"
    model_path = os.getenv("SG_MODEL_PATH", "").strip()
    model_path = model_path if model_path else None

    return DynSettings(
        hotkey=DynField(hotkey),
        device=DynField(device),
        dtype=DynField(dtype),
        display_socket=DynField(display_socket),
        display_notifier_is_on=DynField(display_notifier_is_on),
        model=DynField(model),
        model_path=DynField(model_path),
    )
