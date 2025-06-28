import os
import urllib.request
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def initialize_driver():
    """Initializes the Selenium WebDriver."""
    print("Initializing WebDriver...")
    driver = webdriver.Chrome()
    return driver


def navigate_to_url(driver, url):
    """Navigates the driver to the specified URL."""
    print(f"Navigating to {url}")
    driver.get(url)


def click_element(wait, by_method, value, description="element"):
    """Waits for and clicks an element."""
    try:
        print(f"Waiting for {description} to be clickable...")
        element = wait.until(EC.element_to_be_clickable((by_method, value)))
        element.click()
        print(f"{description} clicked successfully")
        return True
    except TimeoutException:
        print(f"Timeout waiting for {description} to be clickable.")
        return False
    except Exception as e:
        print(f"Error clicking {description}: {e}")
        return False


def create_image_directory(directory_path):
    """Creates a directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created '{directory_path}' directory")
    else:
        print(f"Directory '{directory_path}' already exists")


def download_image(img_element, file_path):
    """Downloads an image from a given element."""
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


def wait_for_images_to_load(wait, last_image_xpath, max_retries=10, delay=2):
    """Waits for a specific element (assumed to be the last image) to be present."""
    print("Waiting for images to be available...")
    retry_count = 0
    while retry_count < max_retries:
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, last_image_xpath)))
            print("All images appear to be loaded")
            return True
        except TimeoutException:
            retry_count += 1
            print(f"Not all images are loaded yet. Retry {retry_count}/{max_retries}")
            time.sleep(delay)
    print("Warning: Could not confirm all images are loaded within the retry limit.")
    return False


def download_all_images(driver, wait, num_images, directory_path):
    """Downloads a sequence of images based on their index."""
    print("Starting to download images...")
    successful_downloads = 0

    for i in range(1, num_images + 1):
        try:
            img_xpath = f'//*[@id="root"]/div[2]/div/div[3]/div[{i}]/div/a/img'
            # Use presence_of_element_located as images might be present but not visible
            img_element = wait.until(
                EC.presence_of_element_located((By.XPATH, img_xpath))
            )

            # Get the alt attribute for the filename
            alt_text = img_element.get_attribute("alt")
            if alt_text:
                # Replace spaces with underscores and append .png
                filename = alt_text.replace(" ", "_") + ".png"
            else:
                # Fallback filename if alt text is not found
                print(
                    f"Warning: Alt text not found for image {i}. Using default filename."
                )
                filename = f"weather_image_{i}.png"

            file_path = os.path.join(directory_path, filename)

            if download_image(img_element, file_path):
                successful_downloads += 1

            # Small delay between downloads
            time.sleep(0.5)
        except TimeoutException:
            print(f"Timeout waiting for image {i} element.")
        except NoSuchElementException:
            print(f"Image {i} element not found.")
        except Exception as e:
            print(f"Error processing image {i}: {e}")

    print(
        f"Download complete. Successfully downloaded {successful_downloads} out of {num_images} images."
    )
    return successful_downloads


def main():
    """Main function to orchestrate the web scraping and downloading process."""
    driver = None
    try:
        driver = initialize_driver()
        wait = WebDriverWait(driver, 10)
        url = "https://charts.ecmwf.int/products/aifs_single_medium-mslp-wind850?projection=opencharts_south_east_asia_and_indonesia"
        image_directory = "weather_img"
        num_images_to_download = 61
        last_image_xpath = '//*[@id="root"]/div[2]/div/div[3]/div[61]/div/a/img'  # XPath for the last image

        navigate_to_url(driver, url)

        # Click the first button
        first_button_xpath = "/html/body/main/div/div/div[2]/div/div/div[3]/div/div[1]/div/div/button/span[1]"
        if not click_element(wait, By.XPATH, first_button_xpath, "first button"):
            print("Failed to click the first button. Exiting.")
            return

        # Wait a moment for potential pop-up/modal
        time.sleep(2)

        # Click the second button (assuming it appears after clicking the first)
        second_button_xpath = "/html/body/div[2]/div[3]/div/div[2]/div/div/div[2]/div/a"
        if not click_element(wait, By.XPATH, second_button_xpath, "second button"):
            print("Failed to click the second button. Exiting.")
            return

        # Wait for the page content/images to load after clicking buttons
        time.sleep(5)

        create_image_directory(image_directory)

        # Wait for images to be present
        wait_for_images_to_load(wait, last_image_xpath)

        # Download images
        download_all_images(driver, wait, num_images_to_download, image_directory)

    except Exception as e:
        print(f"An error occurred during the process: {e}")
    finally:
        if driver:
            print("Closing WebDriver...")
            driver.quit()


if __name__ == "__main__":
    main()
