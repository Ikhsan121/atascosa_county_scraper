import os
import re
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scraper.download_manager import download_files
from config import TIMEOUT
from scraper.web_scraper import main_page
import json


def generate_metadata(link,driver):
    """Generate metadata as a JSON file."""

    driver.get(link)
    # initialize fields
    grantors = []
    grantees = []

    # scrape fields

    # grantors
    table_grantors = driver.find_element(By.XPATH, '//table[@id="ctl00_cphNoMargin_f_oprTab_tmpl0_DataList11"]')
    row_grantors = table_grantors.find_elements(By.TAG_NAME, 'tr')
    for row in row_grantors:
        # Remove the leading number and whitespace
        grantors_name = re.sub(r"^\d+\s", "", row.text.strip())
        grantors.append(grantors_name)

    # grantees
    table_grantees = driver.find_element(By.XPATH, '//table[@id="ctl00_cphNoMargin_f_oprTab_tmpl0_Datalist1"]')
    row_grantees = table_grantees.find_elements(By.TAG_NAME, 'tr')
    for row in row_grantees:
        grantees_name = re.sub(r"^\d+\s", "", row.text.strip())
        grantees.append(grantees_name)

    # document type
    document_type = driver.find_element(By.XPATH, '//span[@id="ctl00_cphNoMargin_f_oprTab_tmpl0_documentInfoList_ctl00_Datalabel2"]').text.strip()

    # date_filed
    date_filed = driver.find_element(By.XPATH, '//span[@id="ctl00_cphNoMargin_f_oprTab_tmpl0_documentInfoList_ctl00_DataLabel3"]').text.strip()

    # instrument number
    instrument_number = driver.find_element(By.XPATH, '//span[@id="ctl00_cphNoMargin_f_oprTab_tmpl0_documentInfoList_ctl00_txtInstrumentNo"]').text.strip()

    # book
    book = driver.find_element(By.XPATH, '//span[@id="ctl00_cphNoMargin_f_oprTab_tmpl0_documentInfoList_ctl00_DataLabel5"]').text.strip()

    # page
    page = driver.find_element(By.XPATH, '//span[@id="ctl00_cphNoMargin_f_oprTab_tmpl0_documentInfoList_ctl00_DataLabel6"]').text.strip()

    # url
    url = link

    filename = f"document_{instrument_number}.pdf"
    metadata = {
        "party_name": {
            'grantors': [" ".join(name.split()) for name in grantors],
            'grantees': [" ".join(name.split()) for name in grantees],
        },
        "document_type": document_type,
        "date_filed": date_filed,
        "instrument_number": instrument_number,
        "book": book,
        "page": page,
        "url": url,
        "filename": filename
    }
    # save metadata to json in metadata directory
    save_metadata(metadata, f"{metadata['filename'].split(".")[0]}.json")

    # download_file
    # Switch to the parent iframe
    parent_iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[@id='cphNoMargin_ImageViewer1_ifrLTViewer']"))
        # Replace with parent iframe ID or locator
    )
    driver.switch_to.frame(parent_iframe)

    # Now locate and switch to the nested iframe
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[@id='WTV1_mifx']"))
    )
    driver.switch_to.frame(iframe)

    # Scroll down slowly
    scroll_pause_time = 0.5  # Pause time between scrolls (in seconds)
    scroll_amount = 200  # Number of pixels to scroll at a time

    # Get the total height of the page
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down by the defined amount
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        sleep(scroll_pause_time)  # Pause to allow content to load

        # Check if we've reached the bottom
        new_height = driver.execute_script("return window.pageYOffset + window.innerHeight")
        if new_height >= last_height:
            break  # Stop scrolling when we reach the bottom

    # Locate elements inside the iframe
    row_images = WebDriverWait(driver, TIMEOUT).until(
        EC.visibility_of_all_elements_located((By.XPATH, "//input[@type='image']"))
    )

    img_urls = []
    for row in row_images:
        image_src = row.get_attribute('src')
        updated_url = re.sub(r"(Width=)\d+|(Height=)\d+",
                             lambda m: f"{m.group(1) or m.group(2)}{'900' if m.group(1) else '1200'}", image_src)
        img_urls.append(updated_url)

    # downloading file
    download_files(driver=driver, image_urls=img_urls, filename=filename)


def save_metadata(metadata, file_name):
    """Save metadata to a JSON file in the metadata directory."""
    # Create the metadata directory if it doesn't exist
    directory = "metadata"
    os.makedirs(directory, exist_ok=True)  # Ensure the directory exists

    # Construct the full file path
    file_path = os.path.join(directory, file_name)

    # Save the metadata to the JSON file
    with open(file_path, 'w') as json_file:
        json.dump(metadata, json_file, indent=4)

    print(f"Metadata saved to {file_path}")


