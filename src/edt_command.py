from datetime import datetime, timedelta
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from credentials import * # personal file containing credentials

days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
months_french = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
loading_icon_class = 'gwt-Image'

def take_screenshot(critere:str, type:str, force:bool, date_str:str|None=None, headless:bool=True):
    if '/' in critere:
        critere = critere.replace('/', '-')
    
    date_path = f"_{date_str.replace('/', '')}" if date_str is not None else ""
        
    screenshot_path = f'./img/edt/edt_{critere}_{type}' + date_path + '.png'
    
    # Remove old screenshots
    try:
        edt_images = os.listdir('./img/edt')
        for file in edt_images:
            diff = (
                datetime.now() - datetime.fromtimestamp(os.path.getmtime(f'./img/edt/{file}'))
            )
            # If file older than 10 minutes ago
            if diff > timedelta(minutes=10): 
                print(f'Removing {file}')
                os.remove(f'./img/edt/{file}')

    except Exception as e:
        print(e)
        pass
    
    # Check if the screenshot was taken less than 10 minutes ago
    try:
        diff = (
            datetime.now() - datetime.fromtimestamp(os.path.getmtime(screenshot_path))
        )
        if not force and diff < timedelta(minutes=10): # 10 minutes
            return screenshot_path
    except Exception as e:
        print("No recent screenshot found, taking a new one")
        pass
    
    if date_str is None:
        day_number = datetime.today().weekday()
    else:
        date = datetime.strptime(date_str, '%d/%m/%Y')
        day_number = date.weekday()
    
    if type=="demain":
        day_number += 1
    
    if (day_number == 5 or day_number == 6) and (type=="jour" or type=="demain") and date_str is None:
        return days[day_number].lower()
    
    # Set up the Selenium webdriver
    options = webdriver.FirefoxOptions()
    options.add_argument("disable-gpu")
    if headless:
        options.add_argument('--headless')
    
    if "semaine" in type:
        # options.add_argument('window-size=1600,1080')
        options.add_argument('--width=1600')
        options.add_argument('--height=1080')
    else: 
        # options.add_argument('window-size=900,900')
        options.add_argument('--width=900')
        options.add_argument('--height=900')
    
    driver = webdriver.Firefox(options=options)
    wait = WebDriverWait(driver, 20)
    small_wait = WebDriverWait(driver, 3)
    
    try:
        # Access the website
        driver.get('https://www.emploisdutemps.uha.fr/')
        
        # Find the element with the id 'username'
        username_field = driver.find_element(by='id', value='username')
        username_field.send_keys(email)
        
        # Find the element with the id 'password'
        password_field = driver.find_element(by='id', value='password')
        password_field.send_keys(password)
        
        # Find the element with the name 'submit'
        submit_button = driver.find_element(by='name', value='submitBtn')
        submit_button.click()
        
        try:
            # try to find the "Ouvrir" or "Open" button (might not be present)
            small_wait.until(EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Open')]")))
            ouvrir_button = driver.find_element(by=By.XPATH, value="//button[contains(text(), 'Open')]")
            ouvrir_button.click()
        except Exception:
            pass
        
        # Find the element search field
        edt_field = wait.until(EC.visibility_of_element_located((By.ID, 'x-auto-136-input')))
        edt_field.send_keys(critere)
        
        # Find the search button
        search_button = driver.find_element(by=By.XPATH, value=f"//button[@aria-describedby='x-auto-31']")
        search_button.click()
        
        # Wait until the events are loaded
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'grilleData')))
        
        if date_str is not None:
            success = goto_date(date_str, wait, driver)
            if not success:
                raise Exception("dateTooFarError")
        
        if type=="jour" or type=="demain":
            if day_number == 7 and date_str is None:
                click_next_week(day_number-1, wait, driver)
            # find button with current day text written on it
            current_day = days[day_number % 7]
            day_button = driver.find_element(by=By.XPATH, value=f"//button[contains(text(), '{current_day}')]")
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, loading_icon_class)))
            day_button.click()
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, loading_icon_class)))
            
        if type=="semaine prochaine" or (type=="semaine" and (day_number == 5 or day_number == 6)):
            if date_str is None:
                click_next_week(day_number, wait, driver)
        
        events = driver.find_element(by=By.CLASS_NAME, value='planningPanelBackground')
        events.screenshot(screenshot_path)
        
        print(f'Screenshot saved to {screenshot_path}')
        
    except Exception as e:
        print(e)
        driver.quit()
        return str(e)
        
    else:
        # Close the webdriver
        driver.quit()
        return screenshot_path
    
def click_next_week(day_number:int, wait:WebDriverWait, driver:webdriver.Firefox):
    next_week_date = datetime.today() + timedelta(7 - day_number)
    next_week_date_str = next_week_date.strftime('%d/%m/%Y')
    goto_date(next_week_date_str, wait, driver)
    
def goto_date(date_str:str, wait:WebDriverWait, driver:webdriver.Firefox) -> bool:
    # Date format: dd/mm/yyyy
    max_attempts = 13
    
    date = datetime.strptime(date_str, '%d/%m/%Y')
    month_name = months[date.month-1].upper()
    
    next_month_button = driver.find_element(by=By.CLASS_NAME, value='x-date-right-icon')
    month_name_element = driver.find_element(by=By.ID, value='x-auto-55')
    
    attempts = 0
    while month_name + ' ' + str(date.year) not in month_name_element.text:
        next_month_button.click()
        attempts += 1
        if attempts >= max_attempts:
            return False
    
    day_button = driver.find_element(by=By.XPATH,
                        value=f"//td[contains(@class, 'x-date-active')]/a/span[text()='{date.day}']")
                        
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, loading_icon_class)))
    day_button.click()
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, loading_icon_class)))
    return True

def command_details_per_server(server_id:str) -> tuple[bool, str]:
    with open('src/bot_stuff/edt_details.json') as f:
        servers = json.load(f)
    
    if server_id not in servers:
        return (False, "")
    
    return (True, servers[server_id]['critere'])

if __name__ == "__main__": # Test
    take_screenshot("3ir", "semaine", True, None, False)
