from datetime import datetime, timedelta
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from credentials import * # personal file containing credentials

days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
months = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

def take_screenshot(critere:str, type:str, force:bool):
    if '/' in critere:
        critere = critere.replace('/', '-')
        
    screenshot_path = f'./img/edt/edt_{critere}_{type}.png'
    
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
    
    day_number = datetime.today().weekday()
    if type=="demain":
        day_number += 1
    
    if (day_number == 5 or day_number == 6) and (type=="jour" or type=="demain"):
        return days[day_number].lower()
    
    # Set up the Selenium webdriver
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("disable-gpu")
    options.add_argument('window-size=1600x1080') if type=="semaine" or type=="semaine prochaine"\
                                                  else options.add_argument('window-size=900x900')
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
        
        if type=="jour" or type=="demain":
            if day_number == 7:
                click_next_week(day_number-1, wait, driver)
            # find button with current day text written on it
            current_day = days[day_number % 7]
            day_button = driver.find_element(by=By.XPATH, value=f"//button[contains(text(), '{current_day}')]")
            day_button.click()
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'gwt-Image')))
            
        if type=="semaine prochaine" or (type=="semaine" and day_number == 5 or day_number == 6):
            click_next_week(day_number, wait, driver)
        
        events = driver.find_element(by=By.ID, value='x-auto-129')
        events.screenshot(screenshot_path)
        
        print(f'Screenshot saved to {screenshot_path}')
        
    except Exception as e:
        print(e)
        return e.__str__()
        
    finally:
        # Close the webdriver
        driver.quit()
        return screenshot_path
    
def click_next_week(day_number, wait:WebDriverWait, driver:webdriver.Chrome):
    next_monday_number = str(int(datetime.today().strftime("%d")) + 7 - day_number)
    next_week_number = str(int(datetime.today().strftime("%W")) + 1)
    next_month_number = int((datetime.today() + timedelta(days=(7-day_number))).strftime("%m"))
    year = str(int((datetime.today() + timedelta(days=(7-day_number))).strftime("%Y")))
    formatted_next_monday = "0" + next_monday_number if len(next_monday_number) == 1 else next_monday_number
    button_text = f"S{next_week_number} - lun. {formatted_next_monday} {months[next_month_number-1]} {year}"
    try:
        next_week_button = driver.find_element(by=By.XPATH, value=f"//button[contains(text(), '{button_text}')]")
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'gwt-Image')))
        print(f"Clicking on '{next_week_button.text}'")
        next_week_button.click()
    except Exception:
        print("No next week button found")
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, 'gwt-Image')))