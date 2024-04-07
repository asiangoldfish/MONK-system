from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Preset user information
DEFAULT_USER_INFO = {
    "username": "newuser",
    "full_name": "Test User",
    "mobile": "1234567890",
    "specialization": "Tester",
    "password": "testpassword123"
}

def register_user(browser, live_server_url, user_info=DEFAULT_USER_INFO):
    browser.get(f"{live_server_url}/register/")
    browser.find_element(By.NAME, "username").send_keys(user_info["username"])
    browser.find_element(By.NAME, "name").send_keys(user_info["full_name"])
    browser.find_element(By.NAME, "mobile").send_keys(user_info["mobile"])
    browser.find_element(By.NAME, "specialization").send_keys(user_info["specialization"])
    browser.find_element(By.NAME, "password1").send_keys(user_info["password"])
    browser.find_element(By.NAME, "password2").send_keys(user_info["password"])
    browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()
    WebDriverWait(browser, 10).until(EC.url_changes)
