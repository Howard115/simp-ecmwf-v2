from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()
driver.get("https://charts.ecmwf.int/products/aifs_single_medium-mslp-wind850?projection=opencharts_south_east_asia_and_indonesia")

wait = WebDriverWait(driver, 10)

# wait for the element to be clickable
try:
    # Wait for the button to be clickable and then click it
    button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div[2]/div/div/div[3]/div/div[1]/div/div/button/span[1]")))
    print("Button is clickable")
except Exception as e:
    print(f"Error waiting for button: {e}")
# hit btn
try:
    # Wait for the button to be clickable and then click it
    button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div/div/div[2]/div/div/div[3]/div/div[1]/div/div/button/span[1]")))
    button.click()
    print("Button clicked successfully")
except Exception as e:
    print(f"Error clicking button: {e}")

# Wait for the second button to be clickable
try:
    # Wait for the second button to be clickable and then click it
    second_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div/div[2]/div/div/div[2]/div/a")))
    print("Second button is clickable")
except Exception as e:
    print(f"Error waiting for second button: {e}")

# Click the second button
try:
    # Wait for the second button to be clickable and then click it
    second_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/div[3]/div/div[2]/div/div/div[2]/div/a")))
    second_button.click()
    print("Second button clicked successfully")
except Exception as e:
    print(f"Error clicking second button: {e}")






time.sleep(500)

