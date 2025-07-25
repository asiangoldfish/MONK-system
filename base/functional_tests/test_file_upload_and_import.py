from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time
import os
import tempfile
from .test_user_registration import register_user

class TestUserRegistrationAndFileImport(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)  # seconds

    def tearDown(self):
        self.browser.quit()

    def test_user_registration_and_file_upload_and_import(self):
        # Register a new user
        register_user(self.browser, self.live_server_url)
        time.sleep(2)
        # Attempt to upload a text file as .mwf and check for an error
        file_path = self.upload_invalid_mwf_file()
        # Cleanup
        time.sleep(2)
        os.unlink(file_path)

    def upload_invalid_mwf_file(self):
        # Create a temporary text file with .mwf extension. We are testing invalid upload of file
        with tempfile.NamedTemporaryFile(suffix=".mwf", delete=False, mode='w') as tmp_file:
            tmp_file.write("This is not a valid content")
            tmp_path = tmp_file.name
        self.browser.get(f"{self.live_server_url}/import_file/")
        self.browser.find_element(By.NAME, "title").send_keys("Invalid MWF File")
        self.browser.find_element(By.NAME, "file").send_keys(tmp_path)
        self.browser.find_element(By.CSS_SELECTOR, "form").submit()
        return tmp_path



