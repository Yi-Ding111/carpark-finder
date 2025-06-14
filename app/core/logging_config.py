import logging
import os
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(log_level=logging.INFO):
    """
    Setup logging for the application.

    Parameters:
        log_level (int): The logging level
    """

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Create formatters
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    # File handler (rotating log files)
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "carpark_finder.log"),
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)

    # Add handlers to root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
