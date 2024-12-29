from scraper.web_scraper import instrument_book_page_links, date_interval, selenium_driver
from scraper.metadata_generator import generate_metadata
from scraper.browserbase_driver import browser


if __name__=="__main__":
    driver = browser() # using browserbase. Change to selenium_driver for testing
    date_interval(driver)
    link_dict = instrument_book_page_links(driver)
    for key in link_dict:
        links = link_dict[key]
        for link in links:
            date_interval(driver)
            # generate json metadata and pdf files
            generate_metadata(page=key, link=link, driver=driver)
    driver.quit()