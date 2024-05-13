from datetime import datetime, timedelta
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from credentials import * # personal file containing credentials

days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

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
        print(e)
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
    options = webdriver.ChromeOptions()
    options.add_argument("disable-gpu")
    if headless:
        options.add_argument('headless')
    
    if "semaine" in type:
        options.add_argument('window-size=1600x1080')
    else: 
        options.add_argument('window-size=900x900')
    
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
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
        submit_button = driver.find_element(by='name', value='submit')
        submit_button.click()
        
        # Find the element with the id 'x-auto-111-input'
        edt_field = wait.until(EC.visibility_of_element_located((By.ID, 'x-auto-111-input')))
        edt_field.send_keys(critere)
        
        # Find the button with aria-descibedby 'x-auto-6'
        search_button = driver.find_element(by=By.XPATH, value=f"//button[@aria-describedby='x-auto-6']")
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
            
        if type=="semaine prochaine" or (type=="semaine" and day_number == 5 or day_number == 6):
            if date_str is None:
                click_next_week(day_number, wait, driver)
        
        events = driver.find_element(by=By.ID, value='x-auto-129')
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
    
def click_next_week(day_number:int, wait:WebDriverWait, driver:webdriver.Chrome):
    next_monday_number = str(int(datetime.today().strftime("%d")) + 7 - day_number)
    next_week_number = str(int(datetime.today().strftime("%W")) + 1)
    next_month_number = int((datetime.today() + timedelta(days=(7-day_number))).strftime("%m"))
    year = str(int((datetime.today() + timedelta(days=(7-day_number))).strftime("%Y")))
    formatted_next_monday = "0" + next_monday_number if len(next_monday_number) == 1 else next_monday_number
    button_text = f"S{next_week_number} - lun. {formatted_next_monday} {months[next_month_number-1]} {year}"
    try:
        next_week_button = driver.find_element(by=By.XPATH, value=f"//button[contains(text(), '{button_text}')]")
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, loading_icon_class)))
        print(f"Clicking on '{next_week_button.text}'")
        next_week_button.click()
    except Exception:
        print("No next week button found")
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, loading_icon_class)))
    
def goto_date(date_str:str, wait:WebDriverWait, driver:webdriver.Chrome) -> bool:
    # Date format: dd/mm/yyyy
    max_attempts = 13
    
    date = datetime.strptime(date_str, '%d/%m/%Y')
    month_name = months[date.month-1].upper()
    
    next_month_button = driver.find_element(by=By.CLASS_NAME, value='x-date-right-icon')
    month_name_element = driver.find_element(by=By.ID, value='x-auto-30')
    
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
