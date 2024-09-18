from utils import *
import webscrapper as wsr
import os

username, password = None, None

def main():
    global username, password
    print("Starting script...")

    username, password = check_credentials()
    if username is None and password is None: 
        username, password = ask_for_credentials()

    start_timer()

    wsr.selenium_get_schedule_main(username, password)

main()
