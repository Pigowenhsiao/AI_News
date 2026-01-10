import sys
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def _configure_output_encoding() -> None:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


_configure_output_encoding()


def setup_logger(log_dir: Path, log_filename: str) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    logger_instance = logging.getLogger("AI_News分析系統")
    logger_instance.setLevel(logging.DEBUG)
    if logger_instance.hasHandlers():
        logger_instance.handlers.clear()
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    log_file_path = log_dir / log_filename
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger_instance.addHandler(console_handler)
    logger_instance.addHandler(file_handler)
    return logger_instance
