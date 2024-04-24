# import pywhatkit
# res = pywhatkit.sendwhatmsg_instantly("+201098517719", "message")
# print(res)

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import pickle
import os
import random

phone = "+201098517719"
message = ['Hi There. This is a testing message the  odoo service, the above message was auto generated', "from sayed"]
my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    # Add more User-Agent strings as needed
]

my_user_agent = random.choice(user_agents)
options = Options()
#put the profile data in docker volume
options.add_argument(f"user-data-dir={str(os.getcwd())}/chromedir")
# options.add_argument("--headless")
prefs = {"download.default_directory": "."}
options.add_experimental_option("prefs", prefs)
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument(f"--user-agent={my_user_agent}")
service = Service()
browser = webdriver.Chrome( options=options)
name = "trial g"
BASE_URL = "https://web.whatsapp.com/"

browser.get(BASE_URL)
print("Kindly go to output tab and login before the timeout of 120 seconds.")
driver_ua = browser.execute_script("return navigator.userAgent")
print("User agent:")
print(driver_ua)
try:
    wait = WebDriverWait(browser, 30)  # Adjust the timeout value as needed (e.g., 60 seconds)
    wait.until(EC.presence_of_element_located((By.XPATH, f"//span[./text()='{name}']")))
    sxpath = browser.find_element("xpath", f"//span[./text()='{name}']")
    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(sxpath, 0, 0)
    action.click()
    action.perform()
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div/p')))
    inp_xpath = ('//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div/p')
    input_box = WebDriverWait(browser, 60).until(expected_conditions.presence_of_element_located((By.XPATH, inp_xpath)))
    for line in message:
        input_box.send_keys(line)
        input_box.send_keys(Keys.SHIFT, Keys.ENTER)
    input_box.send_keys(Keys.ENTER)
    time.sleep(15)
    
except Exception as e:
    print(e)
    print("The above error happened while sending the message")
finally:
    browser.quit()

### first time login
# Wait for the learner to log in
# try:
#     wait = WebDriverWait(browser, 120)  # Adjust the timeout value as needed (e.g., 60 seconds)
#     wait.until(EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']")))
#     print("Logged in successfully. Proceeding to send message")
# except Exception as e:
#     print("Timeout: Learner did not log in within the specified time.")
#     browser.quit()

# pickle.dump(browser.get_cookies(), open("cookies.pkl", "wb"))

# driver.quit()
# browser.get(CHAT_URL.format(phone=phone))
# time.sleep(10)