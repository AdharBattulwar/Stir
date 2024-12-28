from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Initialize WebDriver
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode (no browser UI)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    return driver

# Search product on Amazon
def get_amazon_price(driver, product_name):
    driver.get("https://www.amazon.in")
    search_box = driver.find_element(By.ID, "twotabsearchtextbox")
    search_box.send_keys(product_name + Keys.RETURN)
    time.sleep(2)
    try:
        price = driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
        return f"Amazon: ₹{price}"
    except Exception as e:
        return "Amazon: Price not found"

# Search product on Flipkart
def get_flipkart_price(driver, product_name):
    driver.get("https://www.flipkart.com")
    try:
        close_popup = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
        close_popup.click()
    except:
        pass  # If the popup doesn't exist, proceed
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(product_name + Keys.RETURN)
    time.sleep(2)
    try:
        price = driver.find_element(By.CSS_SELECTOR, "._30jeq3._16Jk6d").text
        return f"Flipkart: {price}"
    except Exception as e:
        return "Flipkart: Price not found"

# Add more platforms as needed

def main():
    product_name = "Samsung 385 L 2 Star Convertible 5-in-1 Digital Inverter Refrigerator"
    driver = init_driver()

    try:
        amazon_price = get_amazon_price(driver, product_name)
        flipkart_price = get_flipkart_price(driver, product_name)
        
        print(amazon_price)
        print(flipkart_price)
        # Add calls to other platform functions here

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
