from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
import logging
import random

# --- Configuration and Setup ---

# Load environment variables
load_dotenv()

# MongoDB setup
MongoDbURI = os.getenv("MONGODB_URI")
client = MongoClient(MongoDbURI)
db = client['Stir']
collection = db['trends']

# X (Twitter) login credentials
x_username = os.getenv("X_USERNAME")
x_email = os.getenv("X_EMAIL")
x_password = os.getenv("X_PASSWORD")

# Load proxies from environment and select a random one
proxies = os.getenv("PROXIES").split(',')
print(proxies)
random_proxy = random.choice(proxies)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_selenium_script():
    # Selenium Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--proxy-server={random_proxy}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Optional: avoid detection
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging


    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Navigate to X login page
        driver.get("https://x.com/i/flow/login?lang=en")
        logging.info("Navigated to X login page.")

        wait = WebDriverWait(driver, 50)

        # Enter Username
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
        username_field.send_keys(x_username)
        logging.info("Entered username.")

        # Click Next
        next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@role='button' and contains(., 'Next')]")))
        next_button.click()
        logging.info("Clicked Next after username.")

        # Check if email input appears
        try:
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "text")))
            email_field.send_keys(x_email)
            logging.info("Entered email.")

            # Click Next after email
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@role='button' and contains(., 'Next')]")))
            next_button.click()
            logging.info("Clicked Next after email.")
        except Exception as e:
            logging.info("Email field not found or already provided.")

        # Enter Password
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "password")))
        password_field.send_keys(x_password)
        logging.info("Entered password.")

        # Click Log in
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@role='button' and contains(., 'Log in')]")))
        login_button.click()
        logging.info("Clicked Log in.")

        # Wait for login to complete, e.g., by checking the presence of the home element
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[@href='/home' and @aria-label='Home']")
        ))
        logging.info("Logged in successfully.")

        # Navigate to Trending page
        driver.get("https://x.com/explore/tabs/trending")
        logging.info("Navigated to Trending page.")

        # Wait for trending topics to load
        wait_trends = WebDriverWait(driver, 20)
        trends = wait_trends.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[@data-testid='trend']//span[contains(text(), '#')]")
        ))
        logging.info(f"Found {len(trends)} trending topics.")

        # Extract trend names
        trending_topics = []
        for trend in trends:
            try:
                trend_name = trend.text.strip()
                if trend_name.startswith("#") and trend_name not in trending_topics:
                    trending_topics.append(trend_name)
            except Exception as e:
                logging.warning(f"Could not extract trend name: {e}")

        # Store results in MongoDB
        record = {
            "trend_names": trending_topics,
            "date_time": datetime.utcnow(),
            "ip_address": random_proxy.split(":")[0]
        }
        result = collection.insert_one(record)
        logging.info("Inserted trending topics into MongoDB.")

        # Return the record with the ObjectId as a string
        record['_id'] = str(result.inserted_id)
        return record

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

    finally:
        driver.quit()
        logging.info("Closed the WebDriver.")