"""
Centralized logging configuration for the application.
"""
import sys
import os
from loguru import logger
from pathlib import Path

from config import DEBUG, OUTPUT_DIR

# Create logs directory
LOGS_DIR = OUTPUT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logger
logger.remove()  # Remove default handler

# Add console handler
log_level = "DEBUG" if DEBUG else "INFO"
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=log_level
)

# Add file handler for errors
logger.add(
    LOGS_DIR / "error_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="1 day",
    retention="7 days"
)

# Add file handler for all logs
logger.add(
    LOGS_DIR / "app_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=log_level,
    rotation="1 day",
    retention="3 days"
)

# Export the configured logger
def get_logger(name):
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Name of the logger, typically __name__
        
    Returns:
        logger: Configured logger instance
    """
    return logger.bind(name=name)
