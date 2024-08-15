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

        time.sleep(5)  # Wait for login to complete

        # Save cookies
        with open(COOKIE_FILE, 'wb') as file:
            pickle.dump(driver.get_cookies(), file)
    except Exception as e:
        logger.error("Login error", exc_info=e)



def remove_profile(driver: WebDriver, url):
    try:
        driver.get('https://www.linkedin.com/')

        with open(COOKIE_FILE, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)

        driver.get(url)
        time.sleep(5)
        button = driver.find_element(By.XPATH,
                                     '//button[contains(@class, "artdeco-button artdeco-button--muted artdeco-button--2 artdeco-button--secondary ember-view pvs-profile-actions__action")]')
        time.sleep(2)
        print(button.text)
        print(button)
        if button and "Pending" in button.text:
            print("Connection request send")
            button.click()
            time.sleep(5)
            cancleButton = driver.find_element(By.XPATH,
                                               '//button[contains(@class, "artdeco-button artdeco-button--2 artdeco-button--primary ember-view artdeco-modal__confirm-dialog-btn")]')
            # cancleButton = driver.find_element(By.ID, "ember175")
            cancleButton.click()
            update_record(url, "Disconnect")
            time.sleep(5)
    except Exception as e:
        logger.error("Disconnect profile error", exc_info=e)


def load_remove_csv(driver):
    r = open("record.txt", 'r')
    lines = [line.rstrip('\n') for line in r]
    # print(lines)
    lines.reverse()
    with open('remove.csv', 'r') as f:
        reader = csv.reader(f)
        # loop through each row and print each value
        for row in reader:
            for e in row:
                print(e)
                if e != "url":
                    for lin in lines:

                        if e in lin:

                            status = lin.split('||')[1]
                            # print(status)
                            if status != "Disconnect":

                                print(f"URL-- {e}")
                                remove_profile(driver, e)


def update_record(url, send):
    print(url)
    print(send)
    with open('record.txt', 'a') as fd:
        fd.write(f'{url} || {send}\n')


isConnected = False


def main():
    # threading.Timer(2.0, check_connection, args=[driver]).start()
    while True:
        check_connection()
        time.sleep(5)
        if (isConnected):
            break


def check_connection():
    print(is_connected())
    if is_connected() == True:
        isConnected = is_connected()
        options = Options()
        options.add_argument('--disable-notifications')
        path = os.path.dirname(os.path.abspath(__file__))

        driver = webdriver.Chrome(service=Service(executable_path=f"{path}{CHROME_DRIVER_PATH}"), options=options)
        print("Internet connection is available. Continuing to check...")
        if not os.path.exists(COOKIE_FILE):
            login_and_save_cookies(driver)
        else:
            load_remove_csv(driver)

        driver.quit()

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
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    return False


if __name__ == '__main__':
    main()
