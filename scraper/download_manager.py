import urllib3
import os
import requests
from PIL import Image
from selenium.webdriver.common.by import By
import shutil
# Suppress the warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
