import requests
import json
import brotli
import platform

import os
from dotenv import load_dotenv

from seleniumwire import webdriver  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.safari.options import Options as SafariOptions

from PyLogger.basic_logger import LoggerSingleton

logger = LoggerSingleton().get_logger()

login_url = r"https://intranet.uv.es/portal/login"
schedule_url = r"https://intranet.uv.es/portal/ac_students_schedule"
event_calendar_url = r"https://aulavirtual.uv.es/calendar/export.php?"

driver = None

def check_browser_preference():
    with open(r'app\config.json', 'r') as file:
        config = json.load(file)

    web_driver = config['webdriver']
    headless = config['headless']

    return web_driver, headless
    
def selenium_get_schedule_main(username_get, password_get):
    global driver, username, password
    username, password = username_get, password_get

    start_webdriver()

    log_into_intranet()
    navigate_to_homepage()
    enter_schedule_pag()
    get_schedule_JSON_req()
    get_calendar_ics()
    driver.quit()
    
def start_webdriver():
    def start_firefox(headless):
        options = FirefoxOptions()
        if headless == "True":
            options.add_argument("--headless")
        options.set_preference("dom.webnotifications.enabled", False)  # Disable notifications
        options.set_preference("permissions.default.image", 2)  # Disable image loading
        options.add_argument("--window-size=1024,768") # reduce window size
        options.set_preference("browser.startup.homepage", "about:blank")  # Skip homepage

        driver = webdriver.Firefox(options=options)

        logger.info(f"Initiating Firefox WebDriver...")

        return driver

    def start_chrome(headless):
        options = webdriver.ChromeOptions()
        if headless == "True":
            options.add_argument('--headless=new')
        options.add_argument("--ignore-certificate-errors")
        # options.add_argument("--allow-insecure-localhost")
        options.add_argument('--enable-automation')
        options.add_argument("--disable-notifications")
        driver = webdriver.Chrome(options=options)
        
        logger.info(f"Initiating Chrome WebDriver...")

        return driver

    def start_safari():
        options = webdriver.SafariOptions()
        driver = webdriver.Safari(options=options)

        return driver

    global driver
    
    if platform.system() == "Darwin":
        logger.debug("Darwin apple system detected as platform.")
        logger.info(f"Initiating Safari WebDriver...")
        driver = start_safari()
        return

    pref_webdriver, headless = check_browser_preference()
    if pref_webdriver:
        logger.debug(f"Headless = {headless}")
        if pref_webdriver == 'firefox': driver = start_firefox(headless) 
        elif pref_webdriver == 'chrome': driver = start_chrome(headless)
        return 
 
    browser_select = input(f"Enter '1' for Firefox, '2' for Chrome browser: ")

    if browser_select == str(1):
        logger.info(f"Initiating Firefox WebDriver...")
        driver = start_firefox()
    else:
        logger.info(f"Initiating Chrome WebDriver...")
        driver = start_chrome()

    return

def log_into_intranet():
    global driver, username, password
    logger.info(f"Opening login page: {login_url} (might take up to 20s).")
    driver.get(login_url)
    logger.info(f"Loading login page elements.")
    user_box_element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "username")))
    logger.info(f"Page elements loaded...")
    user_box_element.send_keys(username)

    pass_box_element = driver.find_element(By.ID, "password")
    pass_box_element.send_keys(password)

    logger.info(f"Logging with User and Password.")

    login_button = driver.find_element(By.ID, "botonLdap")
    login_button.click()

def navigate_to_homepage():
    global driver
    logger.info(f"Waiting for Home page to load...")
    schedule_css_selector = "div.MuiBox-root:nth-child(3) > div:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li:nth-child(5) > button:nth-child(1) > div:nth-child(1) > div:nth-child(1)"
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, schedule_css_selector)))

    logger.info(f"Loaded pag: {driver.current_url}.")

def enter_schedule_pag():
    global driver
    logger.info(f"Getting to pag: {schedule_url}.")
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            logger.debug(f"Try n={retries}")
            driver.requests.clear()
            
            driver.get(schedule_url)
            
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

            no_connection_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Sin conexión en este momento")))
            
            if no_connection_element:
                logger.warning(f"No connection message found, retrying... ({retries+1}/{max_retries})")
                driver.refresh() 
                retries += 1 

        except:
            logger.info(f"Succesfully entered Schedule URL webpage ({driver.current_url})")
            break  

        if retries >= max_retries:
            logger.error(f"ERROR: Max retries reached, exiting script...")
            exit()

def get_schedule_JSON_req():
    global driver
    logger.info(f"Searching for Calendar schedule JSON requests...")
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
        with open(r'app\data\schedule.json', 'w', encoding='utf-8') as file:
            json.dump(calendar_data, file, ensure_ascii=False, indent=4)

            logger.info(f"Calendar info converted to local JSON file...")
    else:
        logger.error(f"Failed to capture calendar JSON data...")

def log_into_aules():
    global driver, username, password
    logger.info(f"Login into Aules as internal user...")

    aules_login_internal = driver.find_element(By.ID, 'theme_boost_union-loginorder-idp').click()
    if not aules_login_internal:
        return

    user_box_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username')))
    logger.info(f"Page elements loaded...")
    user_box_element.send_keys(username)
    logger.debug("Entered username.")

    pass_box_element = driver.find_element(By.ID, 'password')
    pass_box_element.send_keys(password)
    logger.debug("Entered password.")

    login_button = driver.find_element(By.ID, 'botonLdap')
    login_button.click()

    logger.info(f"Logged into Aules")

def get_calendar_ics():
    global driver
    logger.info(f"Opening event calendar page: {event_calendar_url}.")
    driver.get(event_calendar_url)

    aules_login_internal = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'theme_boost_union-loginorder-idp')))
    
    if aules_login_internal:
        log_into_aules()
        all_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'page-header-headings')))
        logger.info(f"Opening event calendar page: {event_calendar_url}.")
        driver.get(event_calendar_url)

    all_button_id = "id_events_exportevents_all"
    all_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, all_button_id)))
    logger.info(f"Page elements loaded. Obtaining download URL...")
    all_button.click()

    driver.find_element(By.ID, "id_period_timeperiod_custom").click()
    
    driver.find_element(By.ID, "id_generateurl").click()

    export_url_ele = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "calendarexporturl")))
    export_url_ele = export_url_ele.get_attribute("value")

    logger.info(f"Obtaining event calendar file.")
    ics_response = requests.get(export_url_ele)
    
    with open(r'app\data\event_calendar.ics', 'wb') as f:
        f.write(ics_response.content)

    logger.info(f"Event calendar downloaded locally.")