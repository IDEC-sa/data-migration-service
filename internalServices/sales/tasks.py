from celery import shared_task
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
from selenium.webdriver import ActionChains
import os
from django.conf import settings
from .services import salesReport
from django.contrib.auth import get_user_model
User = get_user_model()


@shared_task(queue="q1")
def my_task(message=[], sched=0):
    if sched:
        print("scheduled")
        message = salesReport().qs
        message.append('------------------------------------------------------------')
        message.append('This is a scheduled message sent daily at this time to review the progress of the data migration')
    my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    options = Options()
    #put the profile data in docker volume
    options.add_argument(f"user-data-dir={str(os.getcwd())}/chromedir")
    options.add_argument("--headless")
    prefs = {"download.default_directory": "."}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument(f"--user-agent={my_user_agent}")
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
        time.sleep(0)
        conds = {'latency': 0, 'throughput': 5000, 'offline': True}
        browser.set_network_conditions(**conds)
        input_box.send_keys(Keys.ENTER)
        ele_xpath = f"//span[@aria-label=' Pending ']"
        ele = wait.until(EC.presence_of_element_located((By.XPATH, ele_xpath)))
        conds['offline'] = False
        browser.set_network_conditions(**conds)
        print(browser.get_network_conditions())
        wait.until(EC.invisibility_of_element(ele))
        print("message was sent")
    except Exception as e:
        print(e)
        print("The above error happened while sending the message")
    finally:
        browser.quit()
    return
