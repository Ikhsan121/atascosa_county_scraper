from time import sleep
from typing import final
from scraper.web_scraper import instrument_book_page_links
from scraper.metadata_generator import generate_metadata
from pprint import pprint


if __name__=="__main__":
    links = instrument_book_page_links()
    for link in links:
        # generate json metadata and pdf files
        generate_metadata(link=link)
