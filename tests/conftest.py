import os
from urllib.parse import urlparse

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


@pytest.fixture
def browser():
    driver = webdriver.Remote(
        command_executor=os.environ.get("SELENIUM_URL", "http://selenium:4444/wd/hub"),
        options=Options(),
    )
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


@pytest.fixture
def site_url(live_server):
    """URL of the live test server as the Chrome container sees it."""
    configured_url = os.environ.get("TEST_SITE_URL")
    if configured_url:
        return configured_url

    return f"http://web:{urlparse(live_server.url).port}"