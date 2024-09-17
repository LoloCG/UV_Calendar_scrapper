import time
from dotenv import load_dotenv
import os
import json
import brotli
# import requests
from seleniumwire import webdriver  
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


print(f"Starting script...")
start_time = time.time()

end_time = (time.time() - start_time)
print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Loading User and Password.")

load_dotenv()
username = os.getenv('UV_USERNAME')
password = os.getenv('UV_PASSWORD')

if not username or not password:
    print("Error: Environment variables for username and password are not set")
    exit()

end_time = (time.time() - start_time)
print(f"{time.strftime('%M:%S', time.localtime(end_time))} - User and Password successfully loaded.")

login_url = r"https://intranet.uv.es/portal/login"
schedule_url = r"https://intranet.uv.es/portal/ac_students_schedule"

end_time = (time.time() - start_time)
print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Initiating WebDriver...")
driver = webdriver.Firefox()

end_time = (time.time() - start_time)
print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Getting into logging page...")

driver.get(login_url)

# ========= In the login URL =========
end_time = (time.time() - start_time)
print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Loaded pag: {driver.current_url}.")

# wait until the element is loaded to enter all the data
user_box_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
user_box_element.send_keys(username)

pass_box_element = driver.find_element(By.ID, "password")
pass_box_element.send_keys(password)

login_button = driver.find_element(By.ID, "botonLdap")
login_button.click()

end_time = (time.time() - start_time)
print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Logged with User and Password.")

# ========= In the Home URL =========
# Use the schedule button as element to wait loading until proceeding
schedule_css_selector = "div.MuiBox-root:nth-child(3) > div:nth-child(2) > div:nth-child(1) > ul:nth-child(2) > li:nth-child(5) > button:nth-child(1) > div:nth-child(1) > div:nth-child(1)"
WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, schedule_css_selector)))
end_time = (time.time() - start_time)
print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Loaded pag: {driver.current_url}.")

# ========= In the Calendar URL =========
max_retries = 3
retries = 0
while retries < max_retries:
    try:
        driver.requests.clear()
        end_time = (time.time() - start_time)
        print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Getting to pag: {schedule_url}.")
        driver.get(schedule_url)
        
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))

        no_connection_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "Sin conexión en este momento")))
        
        if no_connection_element:
            end_time = (time.time() - start_time)
            print(f"{time.strftime('%M,%S', time.localtime(end_time))} - No connection message found, retrying... ({retries+1}/{max_retries})")
            driver.refresh() 
            retries += 1 

    except:
        end_time = (time.time() - start_time)
        print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Succesfully entered schedule URL webpage ({driver.current_url})")
        break  

    if retries >= max_retries:
        end_time = (time.time() - start_time)
        print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Max retries reached, exiting...")
        # driver.quit()
        exit()

# ========= Search for request performed after getting into the calendar URL ========
end_time = (time.time() - start_time)
print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Searching for Calendar JSON requests...")

calendar_json_data = None
for request in driver.requests:
    if request.response:
        if 'teacherstudent' in request.url and 'application/json' in request.response.headers.get('Content-Type', ''):
            #print(f"URL: {request.url}")

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

        end_time = (time.time() - start_time)
        print(f"{time.strftime('%M:%S', time.localtime(end_time))} - Calendar info converted to local JSON file...")
else:
    print(f"Failed to capture calendar JSON data...")

# Print and save the cookies into JSON file
end_time = (time.time() - start_time)
print(f"{time.strftime('%M:%S', time.localtime(end_time))} - placing cookies into JSON file...")
cookies = driver.get_cookies()
with open('cookies.json', 'w') as file:
    json.dump(cookies, file)

print(f"\nScript ended")
end_time = (time.time() - start_time)
print(f"Total time elapsed since start: {time.strftime('%M:%S', time.localtime(end_time))}")


