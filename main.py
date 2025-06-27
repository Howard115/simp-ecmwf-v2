import os
import urllib.request
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


driver = webdriver.Chrome()
driver.get(
    "https://charts.ecmwf.int/products/aifs_single_medium-mslp-wind850?projection=opencharts_south_east_asia_and_indonesia"
)

wait = WebDriverWait(driver, 10)

# wait for the element to be clickable
try:
    # Wait for the button to be clickable and then click it
    button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/main/div/div/div[2]/div/div/div[3]/div/div[1]/div/div/button/span[1]",
            )
        )
    )
    print("Button is clickable")
except Exception as e:
    print(f"Error waiting for button: {e}")
# hit btn
try:
    # Wait for the button to be clickable and then click it
    button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "/html/body/main/div/div/div[2]/div/div/div[3]/div/div[1]/div/div/button/span[1]",
            )
        )
    )
    button.click()
    print("Button clicked successfully")
except Exception as e:
    print(f"Error clicking button: {e}")

# Wait for the second button to be clickable
try:
    # Wait for the second button to be clickable and then click it
    second_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[2]/div[3]/div/div[2]/div/div/div[2]/div/a")
        )
    )
    print("Second button is clickable")
except Exception as e:
    print(f"Error waiting for second button: {e}")

# Click the second button
try:
    # Wait for the second button to be clickable and then click it
    second_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "/html/body/div[2]/div[3]/div/div[2]/div/div/div[2]/div/a")
        )
    )
    second_button.click()
    print("Second button clicked successfully")
except Exception as e:
    print(f"Error clicking second button: {e}")


# Create a directory to save the images if it doesn't exist
if not os.path.exists("weather_img"):
    os.makedirs("weather_img")
    print("Created 'weather_img' directory")

# Wait for the page to load completely
time.sleep(5)  # Give some time for the page to load after clicking the buttons


# Function to download an image
def download_image(img_element, file_path):
    try:
        src = img_element.get_attribute("src")
        if src:
            urllib.request.urlretrieve(src, file_path)
            print(f"Downloaded: {file_path}")
            return True
        else:
            print(f"No src attribute found for image")
            return False
    except Exception as e:
        print(f"Error downloading image: {e}")
        return False


# Wait for all images to be present
print("Waiting for all images to be available...")
all_images_present = False
max_retries = 10
retry_count = 0

while not all_images_present and retry_count < max_retries:
    try:
        # Check if the last image (61) is present, which suggests all images are loaded
        last_image = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="root"]/div[2]/div/div[3]/div[61]/div/a/img')
            )
        )
        all_images_present = True
        print("All images appear to be loaded")
    except TimeoutException:
        retry_count += 1
        print(f"Not all images are loaded yet. Retry {retry_count}/{max_retries}")
        time.sleep(2)  # Wait before retrying

if not all_images_present:
    print("Warning: Could not confirm all images are loaded")

# Download all 61 images
print("Starting to download images...")
successful_downloads = 0

for i in range(1, 62):  # 1 to 61
    try:
        # Find the image element
        img_xpath = f'//*[@id="root"]/div[2]/div/div[3]/div[{i}]/div/a/img'
        img_element = wait.until(EC.presence_of_element_located((By.XPATH, img_xpath)))

        # Download the image
        file_path = os.path.join("weather_img", f"weather_image_{i}.png")
        if download_image(img_element, file_path):
            successful_downloads += 1

        # Small delay between downloads to avoid overwhelming the server
        time.sleep(0.5)
    except Exception as e:
        print(f"Error processing image {i}: {e}")

print(
    f"Download complete. Successfully downloaded {successful_downloads} out of 61 images."
)


time.sleep(500)
