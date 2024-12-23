from typing import Dict
from selenium.webdriver.remote.remote_connection import RemoteConnection, ClientConfig
from selenium import webdriver
from browserbase import Browserbase
from dotenv import load_dotenv
import os

load_dotenv()

BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")

bb = Browserbase(api_key=BROWSERBASE_API_KEY)


class BrowserbaseConnection(RemoteConnection):
    """
    Manage a single session with Browserbase.
    """

    session_id: str

    def __init__(self, session_id: str, remote_server_url: str, *args, **kwargs):  # type: ignore
        # Use ClientConfig for the connection
        config = ClientConfig(remote_server_addr=remote_server_url)
        super().__init__(client_config=config, *args, **kwargs)
        self.session_id = session_id

    def get_remote_connection_headers(self, parsed_url: str, keep_alive: bool = False) -> Dict[str, str]:
        headers = super().get_remote_connection_headers(parsed_url, keep_alive)
        headers["x-bb-api-key"] = BROWSERBASE_API_KEY
        headers["session-id"] = self.session_id
        return headers


def browser():
    session = bb.sessions.create(project_id=BROWSERBASE_PROJECT_ID)
    connection = BrowserbaseConnection(session.id, remote_server_url=session.selenium_remote_url)
    driver = webdriver.Remote(
        command_executor=connection, options=webdriver.ChromeOptions()
    )

    print(
        "Connected to Browserbase",
        f"{driver.name} version {driver.caps['browserVersion']}",
    )
    return driver
