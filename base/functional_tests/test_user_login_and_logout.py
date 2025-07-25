from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import time
from .test_user_registration import register_user

class TestUserRegistrationAndReLogin(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)  # seconds

    def tearDown(self):
        self.browser.quit()

    def test_user_registration_and_relogin(self):
        # Register a new user
        register_user(self.browser, self.live_server_url)
        time.sleep(2)

        # Log out the user
        self.logout_user()
        time.sleep(2)

        # Log in the user
        self.login_user()
        time.sleep(2)

    def logout_user(self):
        self.browser.find_element(By.LINK_TEXT, "Logout").click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

    def login_user(self):
        self.browser.get(f"{self.live_server_url}/login/")
        self.browser.find_element(By.NAME, "username").send_keys("newuser")
        self.browser.find_element(By.NAME, "password").send_keys("testpassword123")
        self.browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
        WebDriverWait(self.browser, 10).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Logged in successfully")
        )
