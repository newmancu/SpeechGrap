#!python3 main.py
from src.logs import logger
from src.app import speech_grap_app


def main():
    app = speech_grap_app()
    logger.info("SpeechGrab started")
    app.start()


if __name__ == "__main__":
    main()
