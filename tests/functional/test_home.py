import pytest
from selenium.webdriver.common.by import By

pytestmark = pytest.mark.functional


def test_home_page_loads(browser, site_url):
    browser.get(site_url)
    assert browser.find_element(By.TAG_NAME, "h1").is_displayed()