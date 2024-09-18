from utils import *
import webscrapper as wsr
import ics_formatter as icsf
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

def check_already_created_files():
    root_dir = os.getcwd()

    ics_file_path = os.path.join(root_dir, 'generated_files/event_calendar.ics')
    schedule_file_path = os.path.join(root_dir, 'generated_files/schedule.json')

    if os.path.isfile(ics_file_path) and os.path.isfile(schedule_file_path):
        print(f"Both 'event_calendar.ics' and 'schedule.json' are present in the root directory.")
        return True
    else: return False

if not check_already_created_files():
    main()
    icsf.main_ics_formater()
else:
    icsf.main_ics_formater()
