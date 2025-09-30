import logging
import sys

__all__ = ["logger"]
logger = logging.getLogger("rust_display")
logger.setLevel(logging.DEBUG)
COLORS = {
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[95m",  # Magenta
    "RESET": "\033[0m",  # Reset
}
formatter = logging.Formatter(
    f"%(asctime)s | {COLORS['CRITICAL']}%(name)s{COLORS['RESET']} |"
    " %(levelname)s | %(process)d |"
    f" {COLORS['DEBUG']}%(module)s{COLORS['WARNING']}:%(funcName)s"
    f"{COLORS['RESET']}:%(lineno)d %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
