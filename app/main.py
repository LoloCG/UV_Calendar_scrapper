import webscrapper as wsr
import ics_formatter as icsf
import os
from dotenv import load_dotenv
from PyLogger.basic_logger import LoggerSingleton

username, password = None, None

def main():  
    global username, password
    logger.info("Starting script...")

    username, password = get_accout_credentials()

    wsr.selenium_get_schedule_main(username, password)

    icsf.main_ics_formater()
    
    delete_leftover_files()
    
    logger.info("Ending program.")

def delete_leftover_files():
    logger.debug(f"Deleting garbage files generated.")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files_to_remove = [
        os.path.join(base_dir, "data", "event_calendar.ics"),
        os.path.join(base_dir, "data", "schedule.json")
    ]
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Removed {file_path}.")
        else:
            logger.warning(f"Could not remove {file_path}.")

def get_accout_credentials():
    load_dotenv()

    username = os.getenv('UV_USERNAME')
    password = os.getenv('UV_PASSWORD')

    if not username or not password:
        username = input(f"Enter username: ")
        password = getpass.getpass("Enter password: ")

        if not len(password) <= 5: mask_pass = password[0:2]+ ((len(password) - 4) * '*' ) + password[-2:]
        else: mask_pass = ((len(password) - 2) * '*' ) + password[-2:]

        print(f"Username = {username}, Password = {mask_pass}")
    
    else: logger.debug("User credentials found in .env file.")
    
    return username, password

if __name__ == '__main__':
    logger_instance = LoggerSingleton()
    logger_instance.set_logger_config(level='DEBUG')
    logger_instance.set_third_party_loggers_level(level='ERROR')
    logger = logger_instance.get_logger()
    logger.debug("Version v1.3.")
    main()

# UNUSED Functions
def check_already_created_files():
    root_dir = os.getcwd()

    ics_file_path = os.path.join(root_dir, 'event_calendar.ics')
    schedule_file_path = os.path.join(root_dir, 'schedule.json')

    if os.path.isfile(ics_file_path) and os.path.isfile(schedule_file_path):
        print(f"Both 'event_calendar.ics' and 'schedule.json' are present in the root directory.")
        start_timer()
        return True
    else: return False