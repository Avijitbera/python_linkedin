import csv
import os
import socket

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pickle
import time
import threading
import logging

logging.basicConfig(filename="error_log.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

CHROME_DRIVER_PATH = '/chromedriver'
LINKEDIN_USERNAME = ''
LINKEDIN_PASSWORD = ''
COOKIE_FILE = 'linkedin_cookies.pkl'

formatter = logging.Formatter('%(asctime)s [remove.py] %(levelname)s %(message)s')


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


full_logger = setup_logger('full_logger', 'full_log.log')


def login_and_save_cookies(driver):
    try:

        driver.get('https://www.linkedin.com/login')

        username_field = driver.find_element(By.ID, 'username')
        password_field = driver.find_element(By.ID, 'password')
        time.sleep(5)
        username_field.send_keys(LINKEDIN_USERNAME)
        password_field.send_keys(LINKEDIN_PASSWORD)
        time.sleep(2)
        password_field.submit()
        full_logger.info("Login Success")
        time.sleep(10)  # Wait for login to complete

        current_url = driver.current_url
        if "checkpoint" in current_url and "challenge" in current_url:
            full_logger.info("Verification screen")
            time.sleep(60)

        # Save cookies
        cookie = driver.get_cookies()
        if len(cookie) > 0:
            with open(COOKIE_FILE, 'wb') as file:
                pickle.dump(driver.get_cookies(), file)
            full_logger.info("Cookies saved")
            time.sleep(5)
        else:
            full_logger.info("Cookies not found")
            time.sleep(5)

    except Exception as e:
        logger.error("Login error", exc_info=e)


def remove_profile(driver: WebDriver, url):
    try:
        driver.get('https://www.linkedin.com/')
        driver.maximize_window()
        with open(COOKIE_FILE, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

        time.sleep(5)


        driver.get(url)
        full_logger.info(f"Loading profile {url}")
        time.sleep(10)
        current_url = driver.current_url

        if "authwall" in current_url:
            time.sleep(60)
            full_logger.info(f"Failed profile {url} auth required")

        print("Profile loaded")

        # button = driver.find_element(By.XPATH,
        #                              '//button[contains(@class, "artdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--secondary ember-view pvs-profile-actions__action")]')

        # add_note_button = driver.find_element(By.XPATH,
        #                                       '//button[contains(@class, "artdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--secondary ember-view pvs-profile-actions__action")]')

        name = driver.find_element(By.XPATH,
                                   "//h1[contains(@class, 'text-heading-xlarge inline t-24 v-align-middle break-words')]")

        full_logger.info(f"Profile Loaded {name.text} || {url}")

        try:
            button = driver.find_element(By.XPATH,
                                         '//button[contains(@class, "rtdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--secondary ember-view pvs-profile-actions__action")]')

            button.click()
            time.sleep(5)
            cancleButton = driver.find_element(By.XPATH,
                                               '//button[contains(@class, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view artdeco-modal__confirm-dialog-btn")]')
            # cancleButton = driver.find_element(By.ID, "ember175")
            cancleButton.click()
            full_logger.info(f"Disconnected with the profile || {url}")
            update_record(url, "Disconnect")
            time.sleep(5)
        except:
            all_button = driver.find_elements(By.TAG_NAME, "button")
            connect_buttons = [btn for btn in all_button if btn.text == "More"]
            print("Button List")
            time.sleep(1)
            driver.execute_script("arguments[0].click();", connect_buttons[0])
            time.sleep(3)
            print("Show More")
            print("Not Found")
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
            full_logger.info(f"Disconnected with the profile || {url}")
            update_record(url, "Disconnect")
            time.sleep(5)

        # print(button)
        time.sleep(2)

        # if button and "Pending" in button.text:
        #     print("Connection request send")
        #     button.click()
        #     time.sleep(5)
        #     cancleButton = driver.find_element(By.XPATH,
        #                                        '//button[contains(@class, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view artdeco-modal__confirm-dialog-btn")]')
        #     # cancleButton = driver.find_element(By.ID, "ember175")
        #     cancleButton.click()
        #     update_record(url, "Disconnect")
        #     time.sleep(5)
        # else:
        #     all_button = driver.find_elements(By.TAG_NAME, "button")
        #     connect_buttons = [btn for btn in all_button if btn.text == "More"]
        #     print("Button List")
        #     time.sleep(1)
        #     driver.execute_script("arguments[0].click();", connect_buttons[0])
        #     time.sleep(3)
        #     remove_button = driver.find_elements(By.XPATH,
        #                                               "//div[contains(@class, 'artdeco-dropdown__item artdeco-dropdown__item--is-dropdown ember-view full-width display-flex align-items-center')]")
        #     print("Show More")
        #     buttons = [btn for btn in remove_button if "Remove Connection" in btn.text]
        #     for itm in buttons:
        #         print(itm.text)
        #     time.sleep(3)
        #     driver.execute_script("arguments[0].click();", buttons[0])
        #     print("Click Connect")
        #     time.sleep(3)
        #     # add_note_button = driver.find_element(By.XPATH,
        #     #                                       '//button[contains(@class, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view ml1")]')
        #     # add_note_button.click()
        #     update_record(url, "Disconnect")
        #     time.sleep(4)
    except Exception as e:
        logger.error("Disconnect profile error", exc_info=e)


def load_remove_csv(driver):
    r = open("record.txt", 'r')
    lines = [line.rstrip('\n') for line in r]

    lines.reverse()
    full_logger.info("record.txt file loaded")
    lists = []
    if len(lines) > 0:
        for item in lines:
            url = item.split('||')
            lists.append((url[0].strip(), url[1].strip()))

    with open('remove.csv', 'r') as f:
        reader = csv.reader(f)
        # loop through each row and print each value
        for row in reader:
            for e in row:
                if e != "url":
                    # remove_profile(driver, e)
                    if len(lines) > 0:
                        result = [t for t in lists if t[0] == e and t[1] != "Disconnect"]
                        if len(result) > 0:
                            remove_profile(driver, e)
                        else:
                            result = [t for t in lists if t[0] == e]
                            if len(result) < 1:
                                remove_profile(driver, e)
                    else:
                        remove_profile(driver, e)



                        # for lin in lines:
                        #
                        #     if e in lin:
                        #
                        #         status = lin.split('||')[1]
                        #         print(status)
                        #         if status.strip() != "Disconnect":
                        #             # remove_profile(driver, e)
                        #             print("Connect")
                        #     else:
                        #         print("Connect")
                            # remove_profile(driver, e)

                        # remove_profile(driver, e)


def update_record(url, send):
    print(url)
    print(send)
    with open('record.txt', 'a') as fd:
        fd.write(f'{url} || {send}\n')



def main():
    check_connection()
    # threading.Timer(5.0, check_connection, ).start()
    # options = Options()
    # options.add_argument('--disable-notifications')
    # path = os.path.dirname(os.path.abspath(__file__))
    #
    # driver = webdriver.Chrome(service=Service(executable_path=f"{path}{CHROME_DRIVER_PATH}"), options=options)
    # print("Internet connection is available. Continuing to check...")
    # if not os.path.exists(COOKIE_FILE):
    #     login_and_save_cookies(driver)
    # else:
    #     load_remove_csv(driver)
    #
    # driver.quit()
    # check_connection()
    # while True:
    #     global running
    #     if running == False:
    #         check_connection()
    #     time.sleep(5)


path = os.path.dirname(os.path.abspath(__file__))


def check_connection():
    connected = is_connected()

    if connected:
        options = Options()
        options.add_argument('--disable-notifications')
        path = os.path.dirname(os.path.abspath(__file__))

        driver = webdriver.Chrome(service=Service(executable_path=f"{path}{CHROME_DRIVER_PATH}"), options=options)
        print("Internet connection is available. Continuing to check...")
        if not os.path.exists(COOKIE_FILE):
            login_and_save_cookies(driver)
            load_remove_csv(driver)
        else:
            load_remove_csv(driver)

        driver.quit()
    # if is_connected() == True and running == False:
    #     isConnected = is_connected()
    #     options = Options()
    #     options.add_argument('--disable-notifications')
    #
    #     running = True
    #     driver = webdriver.Chrome(service=Service(executable_path=f"{path}{CHROME_DRIVER_PATH}"), options=options)
    #     print("Internet connection is available. Continuing to check...")
    #     if not os.path.exists(COOKIE_FILE):
    #         login_and_save_cookies(driver)
    #     else:
    #         load_remove_csv(driver)
    #
    #     driver.quit()
    #     running = False

    # else:
    #     check_connection(driver)
    # while True:
    #     print(is_connected())

    # Sleep for a specified interval before checking again
    # time.sleep(2)

    # if isConnected == True:
    #
    # else:
    #     threading.Timer(2.0, check_connection(driver)).start()


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
        # return False


if __name__ == '__main__':
    main()
