import os
import socket

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pickle
import time
import csv
import logging


logging.basicConfig(filename="error_log.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

CHROME_DRIVER_PATH = '/chromedriver'
LINKEDIN_USERNAME = 'offlyapp@gmail.com'
LINKEDIN_PASSWORD = 'TesterBest@2027'
COOKIE_FILE = 'linkedin_cookies.pkl'

formatter = logging.Formatter('%(asctime)s [connect.py] %(levelname)s %(message)s')



def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


full_logger = setup_logger('full_logger', 'full_log.log')

#login and save cookies locally
def login_and_save_cookies(driver: WebDriver):
    try:
        driver.get('https://www.linkedin.com/login')

        username_field = driver.find_element(By.ID, 'username')
        password_field = driver.find_element(By.ID, 'password')
        time.sleep(5)
        username_field.send_keys(LINKEDIN_USERNAME)
        password_field.send_keys(LINKEDIN_PASSWORD)
        time.sleep(2)
        password_field.submit()

        time.sleep(20)  # Wait for login to complete
        full_logger.info("Login Success")
        # Save cookies
        with open(COOKIE_FILE, 'wb') as file:
            pickle.dump(driver.get_cookies(), file)
        full_logger.info("Cookies saved")
        time.sleep(5)
    except Exception as e:
        logger.error("connect profile error", exc_info=e)


def load_connect_csv(driver):
    r = open("record.txt", 'r')
    lines = [line.rstrip('\n') for line in r]
    # print(lines)
    lines.reverse()
    full_logger.info("record.txt file loaded")

    lists = []
    if len(lines) > 0:
        for item in lines:
            url = item.split('||')
            lists.append((url[0].strip(), url[1].strip()))


    with open('connect.csv', 'r') as f:
        reader = csv.reader(f)

        # loop through each row and print each value
        for row in reader:
            for e in row:
                if e != "url":

                    if len(lines) > 0:
                        result = [t for t in lists if t[0] == e and t[1] != "Connect"]
                        # matches = (x for x in lists if x[1] > e)

                        if len(result) > 0:
                            connect_profile(driver, e)
                        else:
                            result = [t for t in lists if t[0] == e]
                            if len(result) < 1:
                                connect_profile(driver, e)
                    else:
                        connect_profile(driver, e)
                        # for lin in lines:
                        #     print(e in lin)
                        #     print(e)
                        #     print(lin)
                        #     if e in lin:
                        #         status = lin.split('||')[1]
                        #         print(status)
                        #         print("Status")
                        #         if status.strip() != "Connect":
                        #             print("CALL")
                        #             connect_profile(driver, e)
                        #     else:
                        #         print("CALL@")
                        #         connect_profile(driver, e)
                    # else:
                    #
                    #     connect_profile(driver, e)

                            # connect_profile(driver, e)
                    # else:
                    #
                    #     connect_profile(driver, e)


def connect_profile(driver: WebDriver, url):
    try:

        driver.get('https://www.linkedin.com/')
        driver.maximize_window()

        with open(COOKIE_FILE, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

        driver.get(url)
        full_logger.info(f"Loading profile {url}")
        time.sleep(5)
        current_url = driver.current_url
        print(current_url)
        if "authwall" in current_url:
            time.sleep(60)
            full_logger.info(f"Failed profile {url} auth required")

        name = driver.find_element(By.XPATH, "//h1[contains(@class, 'text-heading-xlarge inline t-24 v-align-middle break-words')]")

        full_logger.info(f"Profile Loaded {name.text} || {url}")
        # check_connection_status(driver)

        # Connect
        try:
            connect_button = driver.find_element(By.XPATH,
                                                 '//button[contains(@class, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view pvs-profile-actions__action")]')

            if connect_button.text == "Follow":
                all_button = driver.find_elements(By.TAG_NAME, "button")
                connect_buttons = [btn for btn in all_button if btn.text == "More"]
                print("Button List")
                time.sleep(1)
                driver.execute_script("arguments[0].click();", connect_buttons[0])
                time.sleep(3)
                print("Show More")
                connect_now_button = driver.find_elements(By.XPATH,
                                                          "//div[contains(@class, 'artdeco-dropdown__item artdeco-dropdown__item--is-dropdown ember-view full-width display-flex align-items-center')]")

                buttons = [btn for btn in connect_now_button if "Connect" in btn.text]
                for itm in buttons:
                    print(itm.text)
                time.sleep(3)
                driver.execute_script("arguments[0].click();", buttons[0])
                print("Click Connect")
                time.sleep(3)
                add_note_button = driver.find_element(By.XPATH,
                                                      '//button[contains(@class, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view ml1")]')
                add_note_button.click()
                time.sleep(3)
                update_record(url, "Connect")
                time.sleep(5)
            else:

                if connect_button:

                    if connect_button.text == "Message":
                        full_logger.info(f"Connection request has send to {name.text} || {url}")
                        update_record(url, "Connect")
                        time.sleep(5)
                    else:
                        connect_button.click()
                        time.sleep(5)
                        add_note_button = driver.find_element(By.XPATH,
                                                              '//button[contains(@class, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view ml1")]')
                        add_note_button.click()
                        time.sleep(5)
                        # send_invitation_button = driver.find_element(By.XPATH, '//button[contains(@class, "ml1")]')
                        full_logger.info(f"Connection request has send to {name.text} || {url}")
                        update_record(url, "Connect")
                        time.sleep(5)

                    # send_invitation_button.click()

                    # print('Connection request sent!')
                else:
                    print('Already connected or no connect button found.')
        except Exception as e:
            logger.error("connect profile error", exc_info=e)
    except Exception as e:
        logger.error("connect profile error", exc_info=e)


def update_record(url, send):

    with open('record.txt', 'a') as fd:
        fd.write(f'{url} || {send}\n')





def main():
    check_connection()
    # options = Options()
    # options.add_argument('--disable-notifications')
    # path = os.path.dirname(os.path.abspath(__file__))
    #
    # driver = webdriver.Chrome(service=Service(executable_path=f"{path}{CHROME_DRIVER_PATH}"), options=options)
    #
    # if not os.path.exists(COOKIE_FILE):
    #     full_logger.info("Cookie not found")
    #     login_and_save_cookies(driver)
    #     load_connect_csv(driver)
    # else:
    #     load_connect_csv(driver)
    #
    # driver.quit()
    # while True:
    #     check_connection()
    #     time.sleep(5)
    #     if (isConnected):
    #         break


def is_connected():
    while True:

        try:
            # connect to the host -- tells us if the host is actually
            # reachable
            socket.create_connection(("1.1.1.1", 53))
            full_logger.info("Connected")
            return True
        except OSError:
            full_logger.info("Reconnecting...")
            time.sleep(5)


def check_connection():
    connected = is_connected()

    if connected:

        options = Options()
        options.add_argument('--disable-notifications')
        path = os.path.dirname(os.path.abspath(__file__))

        driver = webdriver.Chrome(service=Service(executable_path=f"{path}{CHROME_DRIVER_PATH}"), options=options)

        if not os.path.exists(COOKIE_FILE):
            full_logger.info("Cookie not found")
            login_and_save_cookies(driver)
            load_connect_csv(driver)
        else:
            load_connect_csv(driver)

        driver.quit()


if __name__ == '__main__':
    main()
