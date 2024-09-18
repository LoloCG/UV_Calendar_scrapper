from utils import *
import webscrapper as wsr
import os

def main():
    print("Starting script...")

    username, password = check_credentials()
    if username is None and password is None: 
        username, password = ask_for_credentials()

    start_timer()

    wsr.selenium_get_schedule_main()

main()

print(f"Total time elapsed since start: {start_time}")
