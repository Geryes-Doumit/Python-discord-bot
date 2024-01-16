import datetime
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from credentials import * # personal file containing credentials
from selenium.webdriver.support.ui import WebDriverWait

days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

def take_screenshot(critere, type, force):
    if '/' in critere:
        critere = critere.replace('/', '-')
        
    screenshot_path = f'./img/edt_{critere}_{type}.png'
    
    try:
        for file in os.listdir('./img'):
            if file.startswith('edt') and file.endswith('.png') and time.time() - os.path.getmtime(screenshot_path) > 600:
                print(f'Removing {file}')
                os.remove(f'./img/{file}')
        
        if time.time() - os.path.getmtime(screenshot_path) < 600 and not force: # 10 minutes
            return screenshot_path
    except Exception as e:
        pass
    
    # Set up the Selenium webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("disable-gpu")
    options.add_argument('window-size=1600x1080') if type=="semaine" \
                                                  else options.add_argument('window-size=900x900')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        # Access the website
        driver.get('https://www.emploisdutemps.uha.fr/')
        
        # Find the element with the id 'username'
        username_field = driver.find_element(by='id', value='username')
        username_field.send_keys('geryes.doumit@uha.fr')
        
        # Find the element with the id 'password'
        password_field = driver.find_element(by='id', value='password')
        password_field.send_keys(password)
        
        # Find the element with the name 'submit'
        submit_button = driver.find_element(by='name', value='submit')
        submit_button.click()
        
        # Find the element with the id 'x-auto-33-input'
        edt_field = wait.until(EC.visibility_of_element_located((By.ID, 'x-auto-33-input')))
        edt_field.send_keys(critere)
        
        # Find the button with class name 'x-btn-text'
        search_button = driver.find_element(by=By.CLASS_NAME, value='x-btn-text')
        search_button.click()
        
        # Wait until the events are loaded
        wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'eventText')))
        
        if type=="jour" or type=="demain":
            # find button with current day text written on it
            day_number = datetime.datetime.today().weekday()
            if type=="demain":
                day_number += 1 % 7
            current_day = days[day_number] if day_number < 5 else days[4]
            day_button = driver.find_element(by=By.XPATH, value=f"//button[contains(text(), '{current_day}')]")
            day_button.click()
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'gwt-PopupPanel')))
        
        events = driver.find_element(by=By.ID, value='x-auto-129')
        events.screenshot(screenshot_path)
        
        print(f'Screenshot saved to {screenshot_path}')
        
    except Exception as e:
        return e.__str__()
        
    finally:
        # Close the webdriver
        driver.quit()
        return screenshot_path
