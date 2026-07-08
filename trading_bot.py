"""
Main trading bot implementation
"""

import time
import logging
from datetime import datetime
from strategies import get_strategy
from pocket_option_api import PocketOptionAPI
from utils import save_trade_record, get_timestamp, validate_config
import config as cfg


class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, config):
        """
        Initialize trading bot
        
        Args:
            config: Configuration module
        """
        self.config = config
        self.logger = logging.getLogger("TradingBot")
        self.api = None
        self.strategy = None
        self.last_trade_time = 0
        self.daily_loss = 0
        self.trades_today = 0
        self.running = False
        
        # Validate configuration
        is_valid, error_msg = validate_config(vars(config))
        if not is_valid:
            self.logger.error(f"Configuration error: {error_msg}")
            raise ValueError(error_msg)
    
    def initialize(self):
        """Initialize bot components"""
        try:
            # Initialize API
            self.api = PocketOptionAPI(
                email=self.config.POCKET_OPTION_EMAIL,
                password=self.config.POCKET_OPTION_PASSWORD,
                demo_mode=self.config.DEMO_MODE,
                chromedriver_path=self.config.CHROMEDRIVER_PATH
            )
            
            # Start browser
            if not self.api.start_driver():
                raise Exception("Failed to start browser")
            
            # Login
            if not self.api.login():
                raise Exception("Failed to login")
            
            # Initialize strategy
            self.strategy = get_strategy(self.config.STRATEGY)
            
            self.logger.info("Bot initialized successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Initialization failed: {str(e)}")
            return False
    
    def get_market_data(self):
        """
        Get current market data
        
        Returns:
            List of recent prices or None
        """
        try:
            # In a real implementation, you would fetch live price data
            # This is a placeholder
            price = self.api.get_current_price()
            
            if price:
                # Simulate historical data (in production, fetch real historical data)
                return [price * 0.98, price * 0.99, price * 1.0]
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to get market data: {str(e)}")
            return None
    
    def analyze_market(self):
        """
        Analyze market and get trading signal
        
        Returns:
            Tuple of (signal, signal_value)
        """
        try:
            prices = self.get_market_data()
            
            if prices is None:
                return None, None
            
            signal = self.strategy.analyze(prices)
            signal_value = self.strategy.get_signal_value(prices)
            
            return signal, signal_value
        except Exception as e:
            self.logger.error(f"Market analysis failed: {str(e)}")
            return None, None
    
    def check_risk_limits(self):
        """Check if trading is allowed based on risk limits"""
        if self.daily_loss >= self.config.MAX_DAILY_LOSS:
            self.logger.warning("Daily loss limit reached")
            return False
        
        if self.trades_today >= self.config.MAX_CONCURRENT_TRADES:
            self.logger.warning("Max concurrent trades reached")
            return False
        
        return True
    
    def execute_trade(self, signal):
        """
        Execute trade based on signal
        
        Args:
            signal: "BUY" or "SELL"
        
        Returns:
            True if trade executed, False otherwise
        """
        try:
            # Check cooldown
            current_time = time.time()
            if current_time - self.last_trade_time < self.config.TRADE_COOLDOWN:
                return False
            
            # Check risk limits
            if not self.check_risk_limits():
                return False
            
            # Determine direction
            direction = "UP" if signal == "BUY" else "DOWN"
            
            # Place trade
            success = self.api.place_trade(
                direction=direction,
                amount=self.config.TRADE_AMOUNT,
                expiry_time=self.config.CURRENT_EXPIRY
            )
            
            if success:
                self.last_trade_time = current_time
                self.trades_today += 1
                
                # Record trade
                trade_data = {
                    "timestamp": get_timestamp(),
                    "asset": self.config.ASSET,
                    "direction": direction,
                    "amount": self.config.TRADE_AMOUNT,
                    "expiry": self.config.CURRENT_EXPIRY,
                    "strategy": self.config.STRATEGY,
                    "signal": signal
                }
                save_trade_record(trade_data)
            
            return success
        
        except Exception as e:
            self.logger.error(f"Trade execution failed: {str(e)}")
            return False
    
    def run(self):
        """Main bot loop"""
        if not self.initialize():
            return
        
        self.running = True
        self.logger.info("Bot started")
        
        try:
            while self.running:
                try:
                    # Analyze market
                    signal, signal_value = self.analyze_market()
                    
                    if signal and signal != "HOLD":
                        self.logger.info(f"Signal: {signal} (Value: {signal_value})")
                        self.execute_trade(signal)
                    
                    # Check interval
                    time.sleep(self.config.CHECK_INTERVAL)
                
                except KeyboardInterrupt:
                    self.logger.info("Bot stopped by user")
                    break
                except Exception as e:
                    self.logger.error(f"Error in main loop: {str(e)}")
                    time.sleep(5)
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bot"""
        self.running = False
        
        if self.api:
            self.api.close()
        
        self.logger.info("Bot stopped")


def main():
    """Main entry point"""
    from logging_config import setup_logging
    
    # Setup logging
    logger = setup_logging(cfg.LOG_FILE, cfg.LOG_LEVEL)
    
    # Create and run bot
    bot = TradingBot(cfg)
    bot.run()


if __name__ == "__main__":
    main()
