import requests
import json
import brotli
from seleniumwire import webdriver  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from utils import *

login_url = r"https://intranet.uv.es/portal/login"
schedule_url = r"https://intranet.uv.es/portal/ac_students_schedule"
event_calendar_url = r"https://aulavirtual.uv.es/calendar/export.php?"

driver = None

def selenium_get_schedule_main():
    global driver 
    timelog(f"Initiating WebDriver...")
    driver = webdriver.Firefox()

    log_into_page()
    navigate_to_homepage()
    enter_schedule_pag()
    get_schedule_JSON_req()
    get_calendar_ics()

# ========= In the login URL =========
def log_into_page():
    global driver
    timelog(f"Opening login page: {login_url}...")
    driver.get(login_url)

    # wait until the element is loaded to enter all the data
    user_box_element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "username")))
    timelog(f"Page elements loaded...")
    user_box_element.send_keys(username)

    pass_box_element = driver.find_element(By.ID, "password")
    pass_box_element.send_keys(password)

    timelog(f"Logging with User and Password.")

    login_button = driver.find_element(By.ID, "botonLdap")
    login_button.click()

# ========= In the Home URL =========
def navigate_to_homepage():
    global driver
    timelog(f"Waiting for Home page to load...")
    # Use the schedule button as element to wait loading until proceeding
    schedule_css_selector = "div.MuiBox-root:nth-child(3) > div:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li:nth-child(5) > button:nth-child(1) > div:nth-child(1) > div:nth-child(1)"
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, schedule_css_selector)))

    timelog(f"Loaded pag: {driver.current_url}.")

# ========= In the Calendar URL =========
def enter_schedule_pag():
    global driver
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            driver.requests.clear()
            
            timelog(f"Getting to pag: {schedule_url}.")
            driver.get(schedule_url)
            
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

            no_connection_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Sin conexión en este momento")))
            
            if no_connection_element:
                timelog(f"No connection message found, retrying... ({retries+1}/{max_retries})")
                driver.refresh() 
                retries += 1 

        except:
            timelog(f"Succesfully entered schedule URL webpage ({driver.current_url})")
            break  

        if retries >= max_retries:
            timelog(f"ERROR: Max retries reached, exiting script...")
            exit()

# ========= Search for request performed after getting into the calendar URL ========
def get_schedule_JSON_req():
    global driver
    timelog(f"Searching for Calendar schedule JSON requests...")
    calendar_json_data = None
    for request in driver.requests:
        if request.response:
            if 'teacherstudent' in request.url and 'application/json' in request.response.headers.get('Content-Type', ''):

                response_encoding = request.response.headers.get('Content-Encoding', 'utf-8')
                if response_encoding == 'br':
                    decompressed_data = brotli.decompress(request.response.body)
                    calendar_json_data = decompressed_data.decode('utf-8', errors='replace')
                else:
                    calendar_json_data = request.response.body.decode(response_encoding, errors='replace')

    if calendar_json_data:
        calendar_data = json.loads(calendar_json_data)
        with open('schedule.json', 'w', encoding='utf-8') as file:
            json.dump(calendar_data, file, ensure_ascii=False, indent=4)

            timelog(f"Calendar info converted to local JSON file...")
    else:
        timelog(f"Failed to capture calendar JSON data...")


def get_calendar_ics():
    global driver
    timelog(f"Opening event calendar page: {event_calendar_url}.")

    all_button_id = "id_events_exportevents_all"
    all_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, all_button_id)))
    all_button.click()

    interval_button_id = "id_period_timeperiod_custom"
    driver.find_element(By.ID, interval_button_id).click()

    export_url_ele_id = "calendarexporturl"
    export_url_ele = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, export_url_id)))
    timelog(f"Obtaining event calendar file.")
    export_url = export_url_ele.get_attribute("value")
    
    ics_response = requests.get(export_url)
    
    ics_file_path = 'event_calendar.ics'
    with open(ics_file_path, 'wb') as f:
        f.write(ics_response.content)

    timelog(f"Event calendar downloaded locally.")