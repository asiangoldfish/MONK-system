from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time
import os
import tempfile

class TestUserRegistrationAndFileClaim(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)  # seconds

    def tearDown(self):
        self.browser.quit()

    def test_user_registration_and_file_claim(self):
        # Navigate to the registration page and register a new user
        self.register_user()


        # Navigate to the file upload page and submit a file
        file_path = self.upload_file()

        # Navigate to the files list, claim the file, and then view its details
        self.claim_and_view_file()

        # Cleanup
        os.unlink(file_path)

    def register_user(self):
        self.browser.get(f"{self.live_server_url}/register/")
        self.browser.find_element(By.NAME, "username").send_keys("testuser")
        self.browser.find_element(By.NAME, "name").send_keys("Test User")
        self.browser.find_element(By.NAME, "mobile").send_keys("1234567890")
        self.browser.find_element(By.NAME, "specialization").send_keys("Tester")
        self.browser.find_element(By.NAME, "password1").send_keys("testpassword")
        self.browser.find_element(By.NAME, "password2").send_keys("testpassword")
        self.browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        time.sleep(2)

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
        # Here, you would navigate to the details page of the claimed file and assert the details
