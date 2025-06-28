from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
import glob
import re
import datetime
from typing import Optional
import urllib.request
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import BackgroundTasks

app = FastAPI(title="AI 氣象圖")

# Mount static files directory
app.mount("/weather_img", StaticFiles(directory="weather_img"), name="weather_img")


class WeatherChartController:
    def __init__(self):
        self.image_files = self.get_sorted_image_files()

    @staticmethod
    def get_t_value(filename):
        match = re.search(r"\(T\+(\d+)\)", filename)
        return int(match.group(1)) if match else 0

    def get_sorted_image_files(self):
        image_files = glob.glob("weather_img/*.png")
        return sorted(image_files, key=self.get_t_value)

    def get_image_info(self, current_index: int):
        """Get image information for display"""
        if not self.image_files or current_index >= len(self.image_files):
            return None

        current_image = self.image_files[current_index]
        filename = os.path.basename(current_image)

        # Extract date and time from filename
        date_match = re.match(
            r"([A-Za-z]+)_(\d+)_([A-Za-z]+)_(\d+)_(\d+)_UTC", filename
        )

        if date_match:
            weekday, day, month, year, utc_hour = date_match.groups()
            # Convert UTC to UTC+8
            utc_time = datetime.datetime(
                int(year),
                datetime.datetime.strptime(month, "%b").month,
                int(day),
                int(utc_hour),
            )
            local_time = utc_time + datetime.timedelta(hours=8)
            formatted_time = local_time.strftime("%Y-%m-%d-%H:00")
        else:
            formatted_time = "時間解析失敗"

        return {
            "image_path": f"/{current_image}",
            "formatted_time": formatted_time,
            "current_number": current_index + 1,
            "total_images": len(self.image_files),
            "has_previous": current_index > 0,
            "has_next": current_index < len(self.image_files) - 1,
            "progress": (
                len(self.image_files) / 61 if len(self.image_files) < 61 else 1.0
            ),
            "is_loading": len(self.image_files) < 61,
        }


# Initialize controller
controller = WeatherChartController()


def get_html_template(image_info: Optional[dict], current_index: int):
    """Generate HTML template with current image information"""

    # Progress bar HTML
    progress_html = ""
    if image_info and image_info.get("is_loading", False):
        progress_percentage = image_info.get("progress", 0) * 100
        progress_html = f"""
        <div style="margin-bottom: 20px;">
            <div style="width: 100%; background-color: #f0f0f0; border-radius: 10px; height: 20px;">
                <div style="width: {progress_percentage}%; background-color: #4CAF50; height: 20px; border-radius: 10px; transition: width 0.3s;"></div>
            </div>
            <p style="text-align: center; color: #666; margin-top: 10px;">正在爬取氣象圖... ({int(progress_percentage)}%)</p>
        </div>
        """

    # Image display HTML
    image_html = ""
    if image_info and "image_path" in image_info:
        image_html = f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3>{image_info.get('formatted_time', '未知時間')} (台灣時間)</h3>
        </div>
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="{image_info['image_path']}" style="max-width: 100%; max-height: 600px; border: 2px solid #ddd; border-radius: 10px;" alt="Weather Chart">
        </div>
        <div style="text-align: center; margin-bottom: 20px;">
            <p>第 {image_info.get('current_number', 0)} / 共{image_info.get('total_images', 0)}</p>
        </div>
        """
    else:
        image_html = '<div style="text-align: center;"><p>目錄中找不到氣象圖</p></div>'

    # Navigation buttons
    prev_disabled = (
        "disabled"
        if not image_info or not image_info.get("has_previous", False)
        else ""
    )
    next_disabled = (
        "disabled" if not image_info or not image_info.get("has_next", False) else ""
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI 氣象圖</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            h1 {{
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }}
            .controls {{
                display: flex;
                justify-content: center;
                gap: 20px;
                margin-bottom: 30px;
                flex-wrap: wrap;
            }}
            button {{
                padding: 12px 24px;
                font-size: 16px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: bold;
            }}
            button:not(:disabled) {{
                background-color: #4CAF50;
                color: white;
            }}
            button:not(:disabled):hover {{
                background-color: #45a049;
                transform: translateY(-2px);
            }}
            button:disabled {{
                background-color: #cccccc;
                color: #666666;
                cursor: not-allowed;
            }}
            .reset-btn {{
                background-color: #2196F3 !important;
            }}
            .reset-btn:hover {{
                background-color: #1976D2 !important;
            }}
            .nav-container {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 20px;
            }}
            .nav-button {{
                flex: 0 0 auto;
            }}
            .image-container {{
                flex: 1;
                margin: 0 20px;
            }}
            @media (max-width: 768px) {{
                .nav-container {{
                    flex-direction: column;
                    gap: 20px;
                }}
                .image-container {{
                    margin: 0;
                }}
                .controls {{
                    flex-direction: column;
                    align-items: center;
                }}
            }}
        </style>
        <script>
            // Auto refresh every 30 seconds to check for new images
            setInterval(function() {{
                if ({str(image_info.get('is_loading', False) if image_info else False).lower()}) {{
                    location.reload();
                }}
            }}, 30000);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>AI 氣象圖</h1>
            
            {progress_html}
            
            <div class="controls">
                <form method="post" action="/reset" style="display: inline;">
                    <button type="submit" class="reset-btn">回到第一張</button>
                </form>
            </div>
            
            <div class="nav-container">
                <div class="nav-button">
                    <form method="post" action="/previous" style="display: inline;">
                        <input type="hidden" name="current_index" value="{current_index}">
                        <button type="submit" {prev_disabled}>← 上一張</button>
                    </form>
                </div>
                
                <div class="image-container">
                    {image_html}
                </div>
                
                <div class="nav-button">
                    <form method="post" action="/next" style="display: inline;">
                        <input type="hidden" name="current_index" value="{current_index}">
                        <button type="submit" {next_disabled}>下一張 →</button>
                    </form>
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/", response_class=HTMLResponse)
async def home():
    """Main page showing the first image"""
    controller.__init__()  # Refresh image list
    image_info = controller.get_image_info(0)
    return get_html_template(image_info, 0)


@app.post("/previous", response_class=HTMLResponse)
async def previous_image(current_index: int = Form(...)):
    """Navigate to previous image"""
    controller.__init__()  # Refresh image list
    new_index = max(0, current_index - 1)
    image_info = controller.get_image_info(new_index)
    return get_html_template(image_info, new_index)


@app.post("/next", response_class=HTMLResponse)
async def next_image(current_index: int = Form(...)):
    """Navigate to next image"""
    controller.__init__()  # Refresh image list
    max_index = len(controller.image_files) - 1
    new_index = min(max_index, current_index + 1)
    image_info = controller.get_image_info(new_index)
    return get_html_template(image_info, new_index)


@app.post("/reset")
async def reset_to_first():
    """Reset to first image"""
    return RedirectResponse(url="/", status_code=303)


@app.get("/api/status")
async def get_status():
    """API endpoint to get current status"""
    controller.__init__()  # Refresh image list
    return {
        "total_images": len(controller.image_files),
        "target_images": 61,
        "progress": len(controller.image_files) / 61,
        "is_complete": len(controller.image_files) >= 61,
    }


def download_weather_images():
    """下載氣象圖到 weather_img 目錄"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    # Add these additional arguments for AWS environment
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.binary_location = '/usr/bin/google-chrome'  # Specify Chrome binary location
    driver = webdriver.Chrome(options=options)
    try:
        wait = WebDriverWait(driver, 10)
        url = "https://charts.ecmwf.int/products/aifs_single_medium-mslp-wind850?projection=opencharts_south_east_asia_and_indonesia"
        image_directory = "weather_img"
        num_images_to_download = 61
        last_image_xpath = '//*[@id="root"]/div[2]/div/div[3]/div[61]/div/a/img'

        driver.get(url)

        # Click the first button
        first_button_xpath = "/html/body/main/div/div/div[2]/div/div/div[3]/div/div[1]/div/div/button/span[1]"
        try:
            element = wait.until(
                EC.element_to_be_clickable((By.XPATH, first_button_xpath))
            )
            element.click()
        except Exception as e:
            print(f"Failed to click the first button: {e}")
            return False

        time.sleep(2)

        # Click the second button
        second_button_xpath = "/html/body/div[2]/div[3]/div/div[2]/div/div/div[2]/div/a"
        try:
            element = wait.until(
                EC.element_to_be_clickable((By.XPATH, second_button_xpath))
            )
            element.click()
        except Exception as e:
            print(f"Failed to click the second button: {e}")
            return False

        time.sleep(5)

        if not os.path.exists(image_directory):
            os.makedirs(image_directory)

        # Wait for images to be present
        retry_count = 0
        max_retries = 10
        while retry_count < max_retries:
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, last_image_xpath)))
                break
            except TimeoutException:
                retry_count += 1
                print(
                    f"Not all images are loaded yet. Retry {retry_count}/{max_retries}"
                )
                time.sleep(2)
        else:
            print(
                "Warning: Could not confirm all images are loaded within the retry limit."
            )

        # Download images
        for i in range(1, num_images_to_download + 1):
            try:
                img_xpath = f'//*[@id="root"]/div[2]/div/div[3]/div[{i}]/div/a/img'
                img_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, img_xpath))
                )
                alt_text = img_element.get_attribute("alt")
                if alt_text:
                    filename = alt_text.replace(" ", "_") + ".png"
                else:
                    filename = f"weather_image_{i}.png"
                file_path = os.path.join(image_directory, filename)
                src = img_element.get_attribute("src")
                if src:
                    urllib.request.urlretrieve(src, file_path)
                    print(f"Downloaded: {file_path}")
                else:
                    print(f"No src attribute found for image {i}")
                time.sleep(0.5)
            except Exception as e:
                print(f"Error processing image {i}: {e}")
        return True
    except Exception as e:
        print(f"An error occurred during the process: {e}")
        return False
    finally:
        if driver:
            driver.quit()


# 啟動APScheduler定時任務
scheduler = BackgroundScheduler()
scheduler.add_job(download_weather_images, "cron", hour="2,6,12,18", minute=0)
scheduler.start()


@app.post("/api/trigger-crawl")
async def trigger_crawl(background_tasks: BackgroundTasks):
    """手動觸發爬蟲下載氣象圖"""
    background_tasks.add_task(download_weather_images)
    return {"message": "Crawling started in background."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
