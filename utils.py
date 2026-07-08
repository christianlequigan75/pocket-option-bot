"""
Utility functions for the trading bot
"""

import os
import csv
from datetime import datetime


def create_directories():
    """Create necessary directories"""
    directories = ["data", "logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def save_trade_record(trade_data, filename="data/trades.csv"):
    """
    Save trade record to CSV
    
    Args:
        trade_data: Dictionary with trade information
        filename: CSV file path
    """
    file_exists = os.path.isfile(filename)
    
    try:
        with open(filename, "a", newline="") as csvfile:
            fieldnames = ["timestamp", "asset", "direction", "amount", "expiry", "strategy", "signal"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(trade_data)
    except Exception as e:
        print(f"Error saving trade record: {str(e)}")


def load_env_file(filename=".env"):
    """
    Load environment variables from .env file
    
    Args:
        filename: Path to .env file
    
    Returns:
        Dictionary of environment variables
    """
    env_vars = {}
    
    if not os.path.isfile(filename):
        return env_vars
    
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error reading .env file: {str(e)}")
    
    return env_vars


def format_price(price, decimals=2):
    """Format price for display"""
    return f"${price:.{decimals}f}"


def get_timestamp():
    """Get current timestamp"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate_profit_loss(entry_price, exit_price, amount, is_call=True):
    """
    Calculate profit/loss for a trade
    
    Args:
        entry_price: Entry price
        exit_price: Exit price
        amount: Trade amount
        is_call: True for call (up), False for put (down)
    
    Returns:
        Profit/loss amount
    """
    if is_call:
        if exit_price > entry_price:
            return amount * 0.8  # Typical 80% payout
        else:
            return -amount
    else:
        if exit_price < entry_price:
            return amount * 0.8
        else:
            return -amount


def check_time_range(current_hour, start_hour=9, end_hour=17):
    """
    Check if current time is within trading hours
    
    Args:
        current_hour: Current hour (0-23)
        start_hour: Trading start hour
        end_hour: Trading end hour
    
    Returns:
        True if within trading hours
    """
    return start_hour <= current_hour < end_hour


def validate_config(config):
    """
    Validate trading configuration
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    errors = []
    
    if not config.get("POCKET_OPTION_EMAIL"):
        errors.append("Email is required")
    
    if not config.get("POCKET_OPTION_PASSWORD"):
        errors.append("Password is required")
    
    if config.get("TRADE_AMOUNT", 0) <= 0:
        errors.append("Trade amount must be positive")
    
    if config.get("STRATEGY") not in ["RSI", "MA_CROSSOVER", "MOMENTUM", "MACD"]:
        errors.append("Invalid strategy selected")
    
    if not config.get("ASSET"):
        errors.append("Asset must be specified")
    
    if config.get("CURRENT_EXPIRY") not in config.get("EXPIRY_TIMES", []):
        errors.append("Current expiry not in expiry times list")
    
    return len(errors) == 0, ", ".join(errors)
