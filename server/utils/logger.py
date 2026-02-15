import logging
import sys

# Configure logging format
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logger(name: str = "Nexus", level: int = logging.INFO):
    """
    Sets up a standardized logger for the application.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Check if handlers already exist to avoid duplicate logs
    if not logger.handlers:
        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        logger.addHandler(console_handler)

        # File Handler (Optional, can be added later if needed)
        # file_handler = logging.FileHandler("server.log")
        # file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
        # logger.addHandler(file_handler)

    return logger

# Create a global logger instance
logger = setup_logger()
