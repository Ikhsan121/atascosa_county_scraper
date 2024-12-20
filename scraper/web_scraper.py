from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support import expected_conditions as EC
import config


def initialize_driver(browser=config.BROWSER, headless=config.HEADLESS):
    """
    Initializes a Selenium WebDriver with automatic driver management.

    Parameters:
        browser (str): The browser to use ("chrome", "firefox", or "edge"). Default is "chrome".
        headless (bool): Whether to run the browser in headless mode. Default is True.

    Returns:
        WebDriver: An initialized Selenium WebDriver instance.
    """

    if browser == "chrome":
        options = Options()
        if headless:
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

    elif browser == "firefox":
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        options = FirefoxOptions()
        if headless:
            options.add_argument("--headless")

        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)

    elif browser == "edge":
        from selenium.webdriver.edge.options import Options as EdgeOptions
        options = EdgeOptions()
        if headless:
            options.add_argument("--headless")

        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)

    else:
        raise ValueError(f"Unsupported browser: {browser}")

    try:
        # Open the website
        driver.get(config.BASE_URL)

        # Wait for the 'Agree' button to be clickable
        agree_button_selector = driver.find_element(By.ID, 'cph1_lnkAccept')
        WebDriverWait(driver, config.TIMEOUT).until(EC.element_to_be_clickable(agree_button_selector))

        # Click the 'Agree' button
        agree_button_selector.click()

        # Wait for the main page to load (adjust as needed based on main page content)
        WebDriverWait(driver, config.TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        print("Navigated to the main page.")
        return driver

    except Exception as e:
        print(f"Error: {e}")
        driver.quit()
        return None

def date_interval(initial_date = config.INITIAL_DATE, final_date=config.FINAL_DATE):
    """
    :param initial_date:format date is mm/dd/yyyy
    :param final_date:format date is mm/dd/yyyy
    :return: a page with list of files tobe downloaded
    """
    driver = initialize_driver()
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

    # click search button
    search_button = driver.find_element(By.CSS_SELECTOR, "table#cphNoMargin_SearchButtons1_btnSearch__2")
    search_button.click()

    # full count of document
    full_count = driver.find_element(By.ID, 'cphNoMargin_cphNoMargin_SearchCriteriaTop_FullCount1')
    full_count.click()
    return driver

def instrument_book_page_links():
    """
    this function return links to each pdf
    :return:
    """
    links = []
    driver = date_interval()
    # Start the loop for pagination
    while True:
        # Wait for the table to load
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_ctl00_cphNoMargin_cphNoMargin_g_G1_ctl00']"))
        )

        # Locate the table
        table = driver.find_element(By.XPATH, "//div[@id='ctl00_ctl00_cphNoMargin_cphNoMargin_g_G1_ctl00']")

        # Get links of documents
        faux_detail_links = table.find_elements(By.XPATH, "//td[@class='igede12b8d']/a")
        for faux in faux_detail_links:
            links.append(faux.get_attribute('href'))

        # Try to locate the next button
        try:
            next_button = WebDriverWait(driver, config.TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='OptionsBar1_imgNext']"))
            )
        except Exception:
            # Break the loop if the next button is not clickable
            print("No more pages to process.")
            break

        # Check if the button is disabled or not interactable
        if not next_button.is_enabled() or "disabled" in next_button.get_attribute("class"):
            print("Reached the last page.")
            break

        # Click the next button and wait for the next page to load
        next_button.click()

        # Add a short wait to allow the page to refresh
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.staleness_of(table)
        )
    driver.quit()
    return links


