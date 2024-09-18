import time
import getpass
from dotenv import load_dotenv
import os

start_time = None

def timelog(print_text):    
    global start_time
    
    end_time = time.time() - start_time

    minutes, seconds = divmod(end_time, 60)
    print(f"{time.strftime('%M:%S', time.localtime(end_time))} - {print_text}")

def start_timer():
    global start_time
    start_time = time.time()

def check_credentials():
    load_dotenv()

    username = os.getenv('UV_USERNAME')
    password = os.getenv('UV_PASSWORD')

    if not username or not password:
        return None, None
    
    print("User credentials found in .env file.")
    return username, password

def check_browser_preference():
    load_dotenv()

    web_driver = os.getenv('WEB_DRIVER')

    if not web_driver:
        return None

    return web_driver
    
def ask_for_credentials():
    username = input(f"Enter username: ")
    password = getpass.getpass("Enter password: ")

    if not len(password) <= 5: mask_pass = password[0:2]+ ((len(password) - 4) * '*' ) + password[-2:]
    else: mask_pass = ((len(password) - 2) * '*' ) + password[-2:]

    print(f"Username = {username}, Password = {mask_pass}")
    
    return username, password