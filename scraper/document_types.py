import re
from time import sleep
from scraper.download_manager import download_files
from config import TIMEOUT
import json
from selenium.common import NoSuchElementException
import urllib3
import os
import requests
from PIL import Image
import shutil
# Suppress the warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from scraper.metadata_generator import generate_metadata
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import config
from selenium.webdriver.support.ui import Select
from scraper.web_scraper import selenium_driver, go_to_main_page

"""
check if the scraper work for each document type. run this module to check each document type can 
be downloaded using download_manager and metadata_generator module
"""

def docs_type_page(opt_dropdown=config.OPTIONS_DROPDOWN, initial_date = config.INITIAL_DATE, final_date=config.FINAL_DATE):
    driver = selenium_driver()
    for opt in opt_dropdown:
        driver = go_to_main_page(driver)
        # Wait for the date input field to appear and input initial date
        initial_date_dropdown = WebDriverWait(driver, config.TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#cphNoMargin_f_ddcDateFiledFrom input"))
        )
        initial_date_dropdown.click()
        initial_date_dropdown.send_keys(initial_date)

        # Wait for the date input field to appear and input final date
        final_date_dropdown = WebDriverWait(driver, config.TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#cphNoMargin_f_ddcDateFiledTo input"))
        )

        final_date_dropdown.click()
        final_date_dropdown.send_keys(final_date)

        # select document type in dropdown
        dropdown_menu = driver.find_element(By.XPATH, "//select[@id='cphNoMargin_f_DataListBox1']")

        # Create a Select object
        select = Select(dropdown_menu)

        # Select an option by value attribute
        select.select_by_value(opt)
        print(f"option: ", opt)
        # click search button
        search_button = driver.find_element(By.CSS_SELECTOR, "table#cphNoMargin_SearchButtons1_btnSearch__2")
        search_button.click()

        # full count of document
        full_count = driver.find_element(By.ID, 'cphNoMargin_cphNoMargin_SearchCriteriaTop_FullCount1')
        full_count.click()

        # download document and metadata
        download_document(driver=driver, opt=opt)

    driver.quit()


def download_document(driver, opt):
    try:
        # Locate the table
        table = driver.find_element(By.XPATH, "//div[@id='ctl00_ctl00_cphNoMargin_cphNoMargin_g_G1_ctl00']")

        links = []
        # Get links of documents
        faux_detail_links = table.find_elements(By.XPATH, "//td[contains(@class, 'igede12b8d')]/a")
        for faux in faux_detail_links:
            links.append(faux.get_attribute('href'))
        print('link: ', links[0])
        # generate metadata and document
        generate_metadata(driver, links[0])

    except NoSuchElementException:
        print(f"No file of {opt}")


def generate_metadata(driver, link):
    """Generate metadata as a JSON file."""
    # driver = date_interval()
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
    driver.quit()


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


def download_files(driver, image_urls, filename):
    # Create the main documents directory
    download_dir = os.path.abspath("documents")
    os.makedirs(download_dir, exist_ok=True)

    # Create a temporary folder for downloaded images
    temp_dir = os.path.join(download_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Download images
    for i, url in enumerate(image_urls):
        driver.get(url)
        try:
            # Locate the element displaying the image
            file_element = driver.find_element(By.TAG_NAME, "img")
            file_url = file_element.get_attribute("src")  # Extract the file URL

            # Download the file using requests
            response = requests.get(file_url, stream=True, verify=False)
            if response.status_code == 200:
                file_name = os.path.join(temp_dir, f"downloaded_file{i+1}.png")
                with open(file_name, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
            else:
                print(f"Failed to download file. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error downloading file from {url}: {e}")

    # Combine PNGs into a single PDF
    try:
        # Get all PNG files in the temp directory
        image_files = sorted(
            [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".png")]
        )

        if image_files:
            # Open images and convert to RGB
            images = [Image.open(img).convert("RGB") for img in image_files]

            # Save combined PDF in the main documents directory
            pdf_path = os.path.join(download_dir, filename)
            images[0].save(pdf_path, save_all=True, append_images=images[1:])
            print(f"PDF created successfully: {pdf_path}")
        else:
            print("No images found to combine.")
    except Exception as e:
        print(f"Error combining images into PDF: {e}")

    # Delete the temporary folder
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error deleting temporary folder: {e}")

if __name__ == "__main__":
    docs_type_page()