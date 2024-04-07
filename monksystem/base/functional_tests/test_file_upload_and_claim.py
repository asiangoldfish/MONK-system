from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time
import os
import tempfile
from .test_user_registration import register_user

class TestUserRegistrationAndFileClaim(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)  # seconds

    def tearDown(self):
        self.browser.quit()

    def test_user_registration_and_file_upload_and_claim(self):
        # Register a new user
        register_user(self.browser, self.live_server_url)
        time.sleep(2)
        # Navigate to the file upload page and submit a file
        file_path = self.upload_file()
        # Navigate to the files list, claim the file, and then view its details
        self.claim_and_view_file()
        # Cleanup
        os.unlink(file_path)

    def upload_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"Test file content")
            tmp_path = tmp_file.name
        self.browser.get(f"{self.live_server_url}/importFile/")
        self.browser.find_element(By.NAME, "title").send_keys("Test File")
        self.browser.find_element(By.NAME, "file").send_keys(tmp_path)
        self.browser.find_element(By.CSS_SELECTOR, "form").submit()
        time.sleep(2)
        return tmp_path

    def claim_and_view_file(self):
        self.browser.get(f"{self.live_server_url}/viewFile/")
        claim_buttons = self.browser.find_elements(By.LINK_TEXT, "Claim")
        if claim_buttons:
            claim_buttons[0].click()
        time.sleep(2)
