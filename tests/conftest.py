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







# For register view 
@pytest.fixture
def valid_data():
    return {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }


@pytest.fixture
def sent_codes(monkeypatch):
    """Replaces the email sender with a fake that records its calls."""
    calls = []
    monkeypatch.setattr(
        "profiles.views.register.send_new_verification_code_email",
        lambda email, code: calls.append((email, code)),
        raising=False,
    )
    return calls