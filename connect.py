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
LINKEDIN_USERNAME = ''
LINKEDIN_PASSWORD = ''
COOKIE_FILE = 'linkedin_cookies.pkl'


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

        time.sleep(5)  # Wait for login to complete

        # Save cookies
        with open(COOKIE_FILE, 'wb') as file:
            pickle.dump(driver.get_cookies(), file)
    except Exception as e:
        logger.error("connect profile error", exc_info=e)


def load_connect_csv(driver):
    r = open("record.txt", 'r')
    lines = [line.rstrip('\n') for line in r]
    # print(lines)
    lines.reverse()

    with open('connect.csv', 'r') as f:
        reader = csv.reader(f)
        # loop through each row and print each value
        for row in reader:
            for e in row:

                if e != "url":
                    for lin in lines:

                        if e in lin:

                            status = lin.split('||')[1]
                            # print(status)
                            if status != "Connect":
                                connect_profile(driver, e)


def connect_profile(driver: WebDriver, url):
    try:

        driver.get('https://www.linkedin.com/')

        with open(COOKIE_FILE, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

        driver.get(url)
        time.sleep(5)
        # check_connection_status(driver)

        # Connect
        try:
            connect_button = driver.find_element(By.XPATH,
                                                 '//button[contains(@class, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view pvs-profile-actions__action")]')
            print(connect_button)
            print(connect_button)
            if connect_button:
                print("Found")
                connect_button.click()
                time.sleep(5)
                add_note_button = driver.find_element(By.XPATH,
                                                      '//button[contains(@class, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view ml1")]')
                add_note_button.click()
                time.sleep(2)
                # send_invitation_button = driver.find_element(By.XPATH, '//button[contains(@class, "ml1")]')
                update_record(url, "Connect")
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


isConnected = False


def main():
    while True:
        check_connection()
        time.sleep(5)
        if (isConnected):
            break


def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False


def check_connection():
    print(is_connected())

    if is_connected():
        isConnected = is_connected()
        options = Options()
        options.add_argument('--disable-notifications')
        path = os.path.dirname(os.path.abspath(__file__))

        driver = webdriver.Chrome(service=Service(executable_path=f"{path}{CHROME_DRIVER_PATH}"), options=options)
        print("Internet connection is available. Continuing to check...")
        if not os.path.exists(COOKIE_FILE):
            login_and_save_cookies(driver)
        else:
            load_connect_csv(driver)

        driver.quit()


if __name__ == '__main__':
    main()
