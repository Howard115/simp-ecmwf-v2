# AI 氣象圖 - API Documentation

## Overview

The AI 氣象圖 (AI Weather Chart) application is a FastAPI-based web service that automatically scrapes and displays weather forecast images from the European Centre for Medium-Range Weather Forecasts (ECMWF). The application provides a web interface for browsing weather charts and includes scheduled data collection capabilities.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Core Components](#core-components)
4. [API Endpoints](#api-endpoints)
5. [Background Tasks](#background-tasks)
6. [Usage Examples](#usage-examples)
7. [Error Handling](#error-handling)

## Installation

### Prerequisites

- Python >= 3.11.7
- Google Chrome browser (for Selenium WebDriver)
- ChromeDriver

### Dependencies

```bash
pip install selenium fastapi uvicorn[standard] python-multipart apscheduler
```

Or using the provided `pyproject.toml`:

```bash
pip install -e .
```

### Running the Application

```bash
python app.py
```

The application will start on `http://localhost:8000`.

## Configuration

### Environment Setup

The application expects Google Chrome to be installed at `/usr/bin/google-chrome` for containerized environments. For local development, modify the `options.binary_location` in the `download_weather_images()` function.

### Directory Structure

```
project_root/
├── app.py                 # Main application file
├── pyproject.toml        # Project configuration
├── weather_img/          # Directory for downloaded images (auto-created)
└── API_DOCUMENTATION.md  # This documentation file
```

## Core Components

### WeatherChartController Class

The main controller class that handles image file operations and metadata extraction.

#### Methods

##### `__init__(self)`

**Description**: Initializes the controller and loads sorted image files.

**Parameters**: None

**Returns**: None

**Example**:
```python
controller = WeatherChartController()
```

##### `get_t_value(filename: str) -> int` (Static Method)

**Description**: Extracts the T+ value from weather image filenames for sorting purposes.

**Parameters**:
- `filename` (str): The filename to extract T+ value from

**Returns**: 
- `int`: The T+ value, or 0 if not found

**Example**:
```python
t_value = WeatherChartController.get_t_value("weather_image_(T+24).png")
# Returns: 24
```

##### `get_sorted_image_files(self) -> List[str]`

**Description**: Retrieves and sorts all PNG images in the weather_img directory by T+ value.

**Parameters**: None

**Returns**: 
- `List[str]`: Sorted list of image file paths

**Example**:
```python
controller = WeatherChartController()
images = controller.get_sorted_image_files()
# Returns: ['weather_img/image_T+0.png', 'weather_img/image_T+6.png', ...]
```

##### `get_image_info(self, current_index: int) -> Optional[Dict]`

**Description**: Retrieves comprehensive information about a specific image including metadata, navigation state, and loading progress.

**Parameters**:
- `current_index` (int): Zero-based index of the image in the sorted list

**Returns**: 
- `Optional[Dict]`: Dictionary containing image information or None if invalid index

**Return Dictionary Structure**:
```python
{
    "image_path": str,          # Web-accessible path to the image
    "formatted_time": str,      # Formatted time string (Taiwan timezone)
    "current_number": int,      # 1-based image number for display
    "total_images": int,        # Total number of images available
    "has_previous": bool,       # Whether previous navigation is available
    "has_next": bool,          # Whether next navigation is available
    "progress": float,         # Loading progress (0.0 to 1.0)
    "is_loading": bool         # Whether images are still being downloaded
}
```

**Example**:
```python
controller = WeatherChartController()
info = controller.get_image_info(0)
# Returns: {
#     "image_path": "/weather_img/Mon_25_Nov_2024_00_UTC_(T+0).png",
#     "formatted_time": "2024-11-25-08:00",
#     "current_number": 1,
#     "total_images": 45,
#     "has_previous": False,
#     "has_next": True,
#     "progress": 0.738,
#     "is_loading": True
# }
```

## API Endpoints

### Web Interface Endpoints

#### GET `/`

**Description**: Main page displaying the first weather chart image.

**Parameters**: None

**Returns**: HTML response with the weather chart interface

**Response Type**: `HTMLResponse`

**Example**:
```bash
curl http://localhost:8000/
```

#### POST `/previous`

**Description**: Navigate to the previous weather chart image.

**Parameters**:
- `current_index` (form field, int): Current image index

**Returns**: HTML response with the previous image

**Response Type**: `HTMLResponse`

**Example**:
```bash
curl -X POST http://localhost:8000/previous \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "current_index=5"
```

#### POST `/next`

**Description**: Navigate to the next weather chart image.

**Parameters**:
- `current_index` (form field, int): Current image index

**Returns**: HTML response with the next image

**Response Type**: `HTMLResponse`

**Example**:
```bash
curl -X POST http://localhost:8000/next \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "current_index=3"
```

#### POST `/reset`

**Description**: Reset navigation to the first image.

**Parameters**: None

**Returns**: Redirect response to the main page

**Response Type**: `RedirectResponse`

**Example**:
```bash
curl -X POST http://localhost:8000/reset
```

### API Endpoints

#### GET `/api/status`

**Description**: Get current application status and loading progress.

**Parameters**: None

**Returns**: JSON object with status information

**Response Type**: `application/json`

**Response Schema**:
```json
{
  "total_images": "integer",
  "target_images": "integer",
  "progress": "float",
  "is_complete": "boolean"
}
```

**Example**:
```bash
curl http://localhost:8000/api/status
```

**Example Response**:
```json
{
  "total_images": 45,
  "target_images": 61,
  "progress": 0.737,
  "is_complete": false
}
```

#### POST `/api/trigger-crawl`

**Description**: Manually trigger the weather image crawling process.

**Parameters**: None

**Returns**: JSON confirmation message

**Response Type**: `application/json`

**Response Schema**:
```json
{
  "message": "string"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/trigger-crawl
```

**Example Response**:
```json
{
  "message": "Crawling started in background."
}
```

## Background Tasks

### Scheduled Image Crawling

The application includes automated weather image downloading using APScheduler.

#### Schedule Configuration

- **Frequency**: 4 times daily
- **Times**: 02:00, 06:00, 12:00, 18:00 (server time)
- **Function**: `download_weather_images()`

#### Manual Triggering

Images can be manually downloaded using the `/api/trigger-crawl` endpoint.

### Image Download Process

The `download_weather_images()` function performs the following operations:

1. **Cleanup**: Removes all existing files in the `weather_img` directory
2. **Web Scraping**: Uses Selenium WebDriver to navigate to ECMWF charts
3. **Image Collection**: Downloads up to 61 weather forecast images
4. **File Naming**: Saves images with descriptive filenames including date and forecast time

#### Technical Details

- **Browser**: Headless Chrome with optimized flags for server environments
- **Target URL**: ECMWF AIFS charts for South East Asia and Indonesia
- **Image Format**: PNG
- **Timeout**: 10 seconds per operation
- **Error Handling**: Graceful degradation with logging

## Usage Examples

### Basic Web Interface Usage

1. **Access the main page**:
   ```
   http://localhost:8000/
   ```

2. **Navigate through images**:
   - Use "← 上一張" (Previous) and "下一張 →" (Next) buttons
   - Click "回到第一張" (Return to First) to reset

3. **Monitor loading progress**:
   - Progress bar shows crawling status
   - Page auto-refreshes every 30 seconds during loading

### API Integration Examples

#### Python Example

```python
import requests
import time

# Check status
response = requests.get('http://localhost:8000/api/status')
status = response.json()
print(f"Progress: {status['progress']:.2%}")

# Trigger manual crawl
if not status['is_complete']:
    requests.post('http://localhost:8000/api/trigger-crawl')
    print("Crawling triggered")
    
    # Wait for completion
    while True:
        time.sleep(30)
        status = requests.get('http://localhost:8000/api/status').json()
        if status['is_complete']:
            break
        print(f"Still loading... {status['progress']:.2%}")
```

#### JavaScript Example

```javascript
// Check status and update UI
async function checkStatus() {
    const response = await fetch('/api/status');
    const status = await response.json();
    
    console.log(`Images: ${status.total_images}/${status.target_images}`);
    
    if (!status.is_complete) {
        setTimeout(checkStatus, 30000); // Check again in 30 seconds
    }
}

// Trigger manual crawl
async function triggerCrawl() {
    const response = await fetch('/api/trigger-crawl', {
        method: 'POST'
    });
    const result = await response.json();
    console.log(result.message);
}
```

## Error Handling

### Common Error Scenarios

1. **No Images Available**:
   - Display: "目錄中找不到氣象圖" (No weather charts found in directory)
   - Solution: Trigger manual crawl or wait for scheduled download

2. **Chrome/ChromeDriver Issues**:
   - Error: WebDriver initialization failures
   - Solution: Ensure Chrome and ChromeDriver are properly installed

3. **Network Connectivity**:
   - Error: Download failures or timeouts
   - Solution: Check internet connection and ECMWF website availability

4. **File System Permissions**:
   - Error: Unable to create/write files
   - Solution: Ensure proper permissions for the `weather_img` directory

### Error Response Format

API endpoints return standard HTTP status codes:

- `200`: Success
- `303`: Redirect (for navigation endpoints)
- `500`: Internal server error

### Logging

The application includes console logging for:
- Image download progress
- File operations
- Error conditions
- Scheduler activities

## Security Considerations

1. **File Access**: Static files are served only from the `weather_img` directory
2. **Form Validation**: Input validation on navigation parameters
3. **Selenium Security**: Headless browser runs with security flags (`--no-sandbox`, `--disable-dev-shm-usage`)

## Performance Notes

1. **Image Loading**: Up to 61 images are downloaded per session
2. **Caching**: Images are cached locally until next scheduled update
3. **Auto-refresh**: Web interface refreshes every 30 seconds during loading
4. **Background Processing**: Image downloads run in background threads

## Troubleshooting

### Common Issues

1. **Images not displaying**:
   - Check if `weather_img` directory exists and contains PNG files
   - Verify file permissions

2. **Crawling failures**:
   - Check Chrome installation
   - Verify network connectivity to ECMWF
   - Review console logs for specific error messages

3. **Scheduler not running**:
   - Ensure application is running continuously
   - Check system time zone settings

### Debug Mode

For development debugging, you can run with increased verbosity:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --log-level debug
```

---

*This documentation covers all public APIs, functions, and components of the AI 氣象圖 application. For additional support or feature requests, please refer to the project repository.*