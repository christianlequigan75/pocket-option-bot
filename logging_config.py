"""
Logging configuration for the trading bot
"""

import logging
import os
from datetime import datetime


def setup_logging(log_file="trading.log", log_level=logging.INFO):
    """
    Setup logging configuration
    
    Args:
        log_file: Path to log file
        log_level: Logging level
    """
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    log_path = os.path.join("logs", log_file)
    
    # Create logger
    logger = logging.getLogger("TradingBot")
    logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(log_level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_trade(logger, action, asset, amount, price, expiry_time, signal_value=None):
    """
    Log a trade execution
    
    Args:
        logger: Logger instance
        action: "BUY" or "SELL"
        asset: Trading asset
        amount: Trade amount
        price: Asset price
        expiry_time: Expiry time in seconds
        signal_value: Signal value for reference
    """
    message = f"Trade executed: {action} {asset} ${amount} @ {price} ({expiry_time}s)"
    if signal_value:
        message += f" [Signal: {signal_value}]"
    
    logger.info(message)


def log_error(logger, error_message, exception=None):
    """
    Log an error
    
    Args:
        logger: Logger instance
        error_message: Error message
        exception: Exception object (optional)
    """
    if exception:
        logger.error(f"{error_message}: {str(exception)}")
    else:
        logger.error(error_message)


def log_analysis(logger, asset, strategy, signal, signal_value):
    """
    Log market analysis
    
    Args:
        logger: Logger instance
        asset: Trading asset
        strategy: Strategy name
        signal: "BUY", "SELL", or "HOLD"
        signal_value: Indicator value
    """
    message = f"Analysis - {asset} ({strategy}): {signal} [Value: {signal_value}]"
    logger.debug(message)
