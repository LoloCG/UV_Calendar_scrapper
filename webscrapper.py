import requests
import json
import brotli
from seleniumwire import webdriver  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

from utils import *

login_url = r"https://intranet.uv.es/portal/login"
schedule_url = r"https://intranet.uv.es/portal/ac_students_schedule"
event_calendar_url = r"https://aulavirtual.uv.es/calendar/export.php?"

driver = None

def selenium_get_schedule_main(username_get, password_get):
    global driver, username, password
    username, password = username_get, password_get

    start_webdriver()

    log_into_intranet()
    navigate_to_homepage()
    enter_schedule_pag()
    get_schedule_JSON_req()
    get_calendar_ics()

def start_webdriver():
    global driver
    timelog(f"Initiating WebDriver...")
    # For firefox only
    options = Options()
    # options.headless = True  # Enable headless mode
    options.set_preference("dom.webnotifications.enabled", False)  # Disable notifications
    options.set_preference("permissions.default.image", 2)  # Disable image loading
    options.add_argument("--window-size=1024,768") # reduce window size
    options.set_preference("browser.startup.homepage", "about:blank")  # Skip homepage

    driver = webdriver.Firefox(options=options)
    
def log_into_intranet():
    global driver, username, password
    timelog(f"Opening login page: {login_url}...")
    driver.get(login_url)

    user_box_element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "username")))
    timelog(f"Page elements loaded...")
    user_box_element.send_keys(username)

    pass_box_element = driver.find_element(By.ID, "password")
    pass_box_element.send_keys(password)

    timelog(f"Logging with User and Password.")

    login_button = driver.find_element(By.ID, "botonLdap")
    login_button.click()

def navigate_to_homepage():
    global driver
    timelog(f"Waiting for Home page to load...")
    schedule_css_selector = "div.MuiBox-root:nth-child(3) > div:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li:nth-child(5) > button:nth-child(1) > div:nth-child(1) > div:nth-child(1)"
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, schedule_css_selector)))

    timelog(f"Loaded pag: {driver.current_url}.")

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
        with open('generated_files/schedule.json', 'w', encoding='utf-8') as file:
            json.dump(calendar_data, file, ensure_ascii=False, indent=4)

            timelog(f"Calendar info converted to local JSON file...")
    else:
        timelog(f"Failed to capture calendar JSON data...")

def log_into_aules():
    global driver, username, password
    timelog(f"Login into Aules as internal user...")

    aules_login_internal = driver.find_element(By.ID, 'theme_boost_union-loginorder-idp').click()
    if not aules_login_internal:
        return

    user_box_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username')))
    timelog(f"Page elements loaded...")
    user_box_element.send_keys(username)

    pass_box_element = driver.find_element(By.ID, 'password')
    pass_box_element.send_keys(password)

    login_button = driver.find_element(By.ID, 'botonLdap')
    login_button.click()

    timelog(f"Logged into Aules")

def get_calendar_ics():
    global driver
    timelog(f"Opening event calendar page: {event_calendar_url}.")
    driver.get(event_calendar_url)

    aules_login_internal = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'theme_boost_union-loginorder-idp')))
    
    if aules_login_internal:
        log_into_aules()
        all_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'page-header-headings')))
        timelog(f"Opening event calendar page: {event_calendar_url}.")
        driver.get(event_calendar_url)

    all_button_id = "id_events_exportevents_all"
    all_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, all_button_id)))
    timelog(f"Page elements loaded. Obtaining download URL...")
    all_button.click()

    driver.find_element(By.ID, "id_period_timeperiod_custom").click()
    
    driver.find_element(By.ID, "id_generateurl").click()

    export_url_ele = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "calendarexporturl")))
    export_url_ele = export_url_ele.get_attribute("value")

    timelog(f"Obtaining event calendar file.")
    ics_response = requests.get(export_url_ele)
    
    ics_file_path = 'generated_files/event_calendar.ics'
    with open(ics_file_path, 'wb') as f:
        f.write(ics_response.content)

    timelog(f"Event calendar downloaded locally.")