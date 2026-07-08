"""
Pocket Option API interaction using Selenium
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import logging

logger = logging.getLogger("TradingBot")


class PocketOptionAPI:
    """Interface for Pocket Option trading platform"""
    
    def __init__(self, email, password, demo_mode=True, chromedriver_path="./chromedriver"):
        """
        Initialize Pocket Option API
        
        Args:
            email: Pocket Option email
            password: Pocket Option password
            demo_mode: Use demo account
            chromedriver_path: Path to chromedriver
        """
        self.email = email
        self.password = password
        self.demo_mode = demo_mode
        self.chromedriver_path = chromedriver_path
        self.driver = None
        self.is_logged_in = False
    
    def start_driver(self):
        """Start Chrome driver"""
        try:
            service = Service(self.chromedriver_path)
            options = webdriver.ChromeOptions()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            
            self.driver = webdriver.Chrome(service=service, options=options)
            logger.info("Chrome driver started")
            return True
        except Exception as e:
            logger.error(f"Failed to start Chrome driver: {str(e)}")
            return False
    
    def login(self):
        """Login to Pocket Option"""
        try:
            self.driver.get("https://pocketoption.com")
            time.sleep(3)
            
            # Wait for login form
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            # Enter credentials
            email_field.send_keys(self.email)
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_button.click()
            
            time.sleep(5)
            
            # Check if demo mode should be used
            if self.demo_mode:
                self.switch_to_demo()
            
            self.is_logged_in = True
            logger.info("Successfully logged in to Pocket Option")
            return True
        
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def switch_to_demo(self):
        """Switch to demo account"""
        try:
            time.sleep(2)
            # Find and click demo mode toggle
            demo_toggle = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Demo')]")
            demo_toggle.click()
            time.sleep(2)
            logger.info("Switched to demo account")
            return True
        except Exception as e:
            logger.warning(f"Could not switch to demo mode: {str(e)}")
            return False
    
    def select_asset(self, asset_name):
        """
        Select trading asset
        
        Args:
            asset_name: Asset name (e.g., "BTCUSD")
        """
        try:
            # Find and click asset selector
            asset_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Search assets']")
            asset_field.clear()
            asset_field.send_keys(asset_name)
            
            time.sleep(1)
            
            # Click on the asset from dropdown
            asset_option = self.driver.find_element(By.XPATH, f"//span[contains(text(), '{asset_name}')]")
            asset_option.click()
            
            time.sleep(1)
            logger.info(f"Selected asset: {asset_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to select asset {asset_name}: {str(e)}")
            return False
    
    def place_trade(self, direction, amount, expiry_time):
        """
        Place a trade
        
        Args:
            direction: "UP" or "DOWN"
            amount: Trade amount in USD
            expiry_time: Expiry time in seconds (5, 10, 15, or 30)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Set trade amount
            amount_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Amount']")
            amount_field.clear()
            amount_field.send_keys(str(amount))
            
            time.sleep(0.5)
            
            # Set expiry time
            expiry_field = self.driver.find_element(By.XPATH, "//input[@placeholder='Expiry']")
            expiry_field.clear()
            expiry_field.send_keys(str(expiry_time))
            
            time.sleep(0.5)
            
            # Click trade button (UP or DOWN)
            trade_button = self.driver.find_element(By.XPATH, f"//button[contains(text(), '{direction}')]")
            trade_button.click()
            
            time.sleep(1)
            logger.info(f"Trade placed: {direction} ${amount} ({expiry_time}s)")
            return True
        
        except Exception as e:
            logger.error(f"Failed to place trade: {str(e)}")
            return False
    
    def get_current_price(self):
        """Get current asset price"""
        try:
            price_element = self.driver.find_element(By.XPATH, "//span[@class='current-price']")
            price = float(price_element.text)
            return price
        except Exception as e:
            logger.warning(f"Could not get current price: {str(e)}")
            return None
    
    def get_balance(self):
        """Get account balance"""
        try:
            balance_element = self.driver.find_element(By.XPATH, "//span[@class='balance']")
            balance = float(balance_element.text.replace("$", ""))
            return balance
        except Exception as e:
            logger.warning(f"Could not get balance: {str(e)}")
            return None
    
    def close(self):
        """Close browser and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Chrome driver closed")
            self.is_logged_in = False
        except Exception as e:
            logger.error(f"Error closing driver: {str(e)}")
