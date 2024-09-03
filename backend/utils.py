import os
import logging


def log_errors(log: str):
    log_path = "log"
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_file = f"{log_path}/logfile.log"
    previous_log = f"{log_path}/previous_logfile.log"

    if os.path.exists(previous_log):
        os.remove(previous_log)

    if os.path.exists(log_file):
        os.rename(log_file, previous_log)

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.error(log)
