import os
import shutil
import urllib3
from concurrent.futures import ThreadPoolExecutor

import requests
from PIL import Image
from selenium.webdriver.common.by import By

# Suppress the warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_image(url, i, temp_dir):
    """Downloads a single image from a URL."""
    try:
        response = requests.get(url, stream=True, verify=False)
        if response.status_code == 200:
            file_name = os.path.join(temp_dir, f"downloaded_file{i + 1}.png")
            with open(file_name, "wb") as file:
                for chunk in response.iter_content(8192):  # Optimized chunk size
                    file.write(chunk)
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading file from {url}: {e}")

def download_files(image_urls, filename):
    download_dir = os.path.abspath("documents")
    os.makedirs(download_dir, exist_ok=True)
    temp_dir = os.path.join(download_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    # Download images concurrently
    with ThreadPoolExecutor() as executor:
        executor.map(lambda args: download_image(*args), [(url, i, temp_dir) for i, url in enumerate(image_urls)])

    try:
        image_files = sorted(
            [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) if f.endswith(".png")]
        )
        if image_files:
            images = [Image.open(img).convert("RGB") for img in image_files]
            pdf_path = os.path.join(download_dir, filename)
            images[0].save(pdf_path, save_all=True, append_images=images[1:])
            print(f"PDF created successfully: {pdf_path}")
        else:
            print("No images found to combine.")
    except Exception as e:
        print(f"Error combining images into PDF: {e}")
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error deleting temporary folder: {e}")