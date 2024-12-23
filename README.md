
# Automated Document Scraper

## Overview

This project is a Python-based web scraper that automates the process of extracting metadata and downloading document files from a specified website. It leverages Selenium WebDriver for browser automation and integrates with Browserbase for handling browser sessions.

---

## Features

- **Web Scraping**: Automates navigation, input handling, and document extraction from a target website.
- **Metadata Generation**: Captures metadata (e.g., grantors, grantees, document type, filing date) and stores it as JSON.
- **File Download**: Combines multiple images into PDF documents.
- **Dynamic Browser Management**: Uses Browserbase for scalable browser session handling.

---

## Requirements

### Dependencies

Install required Python packages:

```bash
pip install selenium webdriver-manager pillow browserbase python-dotenv requests
```

### Environment Variables

Create a `.env` file with the following variables:

```env
BROWSERBASE_API_KEY=your_browserbase_api_key
BROWSERBASE_PROJECT_ID=your_browserbase_project_id
```

---

## File Structure

- `main.py`: Entry point for the scraper.
- `config.py`: Configuration file containing constants (e.g., base URL, browser type, timeouts).
- `browserbase_driver.py`: Handles connection to Browserbase.
- `document_types.py`: Contains logic for handling specific document types.
- `download_manager.py`: Handles downloading and processing of files.
- `metadata_generator.py`: Generates and saves metadata in JSON format.
- `web_scraper.py`: Core scraping functions for navigation and data extraction.

---

## Configuration

Update the `config.py` file with:

```python
BASE_URL = "https://atascosatx-clerk-aumentum.aumentumtech.com/RealEstate/SearchEntry.aspx"
BROWSER = 'chrome'
HEADLESS = False
INITIAL_DATE = '11/19/2024'  # mm/dd/yyyy
FINAL_DATE = '11/19/2024'  # mm/dd/yyyy
TIMEOUT = 5
```

---

## How to Run

### Step 1: Initialize the Main Script

Run the `main.py` file:

```bash
python main.py
```

This script will:
1. Open the target website.
2. Navigate through date intervals to locate documents.
3. Extract metadata and download associated files.

### Step 2: Customizing Date Ranges

You can adjust the date ranges in `config.py` or directly in the `date_interval` function in `web_scraper.py`:

```python
initial_date = 'mm/dd/yyyy'
final_date = 'mm/dd/yyyy'
```

### Step 3: Managing Browser Sessions

Browser sessions are automatically handled via Browserbase. Ensure the correct API key and project ID are set in the `.env` file.

---

## Key Functions

### 1. `main_page()`
- Navigates to the website’s main page.
- Clicks the "Agree" button to proceed.

### 2. `date_interval(driver, initial_date, final_date)`
- Inputs date ranges to filter document results.
- Initiates the search process.

### 3. `instrument_book_page_links(driver)`
- Extracts document links from paginated tables.

### 4. `generate_metadata(link, driver)`
- Collects metadata fields like grantors, grantees, and filing date.
- Saves metadata as a JSON file.

### 5. `download_files(driver, image_urls, filename)`
- Downloads document images and combines them into a PDF.

---

## Output

### Metadata
- Saved as JSON files in the `metadata/` directory.

### Documents
- Saved as PDF files in the `documents/` directory.

---

## Error Handling

- **Invalid Sessions**: Automatically reconnects to Browserbase.
- **Missing Elements**: Waits dynamically for elements to load.
- **Download Failures**: Logs errors and retries.

---

## Future Enhancements

- Add support for additional document types.
- Improve pagination handling.
- Enhance error recovery mechanisms.

---

## License

This project is open-source and free to use under the MIT License.
