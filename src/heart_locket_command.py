import time
import PIL.Image
import cv2
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import discord
import os
import aiohttp
import imghdr
import io

DL_DIRECTORY = os.environ['USERPROFILE'] + "\\Documents\\Python-discord-bot\\img\\heart_locket\\"
# DL_DIRECTORY = "/Users/geryes/Pictures"
# DL_DIRECTORY = "/app/img/heart_locket/"

async def make_heart_locket(image:discord.Attachment, text:str, image2:discord.Attachment=None, orientation:str="image-text", headless=True):
    # Set up the Selenium webdriver
    options = webdriver.FirefoxOptions()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", DL_DIRECTORY)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,image/jpeg,image/png,image/gif")

    options.add_argument("disable-gpu")
    
    if headless:
        options.add_argument('--headless')
    
    # return value
    path = "error"
    temp_path = "img/temp.None"
    temp_path2 = "img/temp2.None"
    
    driver = webdriver.Firefox(options=options)
    try:
        driver.get('https://makesweet.com/my/heart-locket')
        
        try:
            # find button with aria-label="Consent"
            consent_button = driver.find_element(by=By.XPATH, value="//button[@aria-label='Consent']")
            consent_button.click()
        except:
            pass
        
        if orientation=="image-text":
            temp_path = await insert_image(driver, image)
            await insert_text(driver, text)
        elif orientation=="text-image":
            await insert_text(driver, text)
            temp_path = await insert_image(driver, image)
        elif orientation=="image-image":
            temp_path = await insert_image(driver, image)
            if image2 is None:
                return "image2_none"
            temp_path2 = await insert_image(driver, image2, True)
        
        wb_animate = driver.find_element(by=By.ID, value="wb-animate")
        wb_animate.click()
        
        wb_make_gif = driver.find_element(by=By.ID, value="wb-make-gif")
        wb_make_gif.click()
        
        wait = WebDriverWait(driver, 30)
        wait.until(EC.visibility_of_element_located((By.ID, "wb-working-save")))
        
        wb_save = driver.find_element(by=By.ID, value="wb-working-save")
        wb_save.click()
        print("Downloading gif...")
        
        filename = getDownLoadedFileName(driver, 10)
        
        path = "img/heart_locket/" + filename
        
    except Exception as e:
        print(e)
        pass
    
    finally:
        driver.quit()
        try:
            os.remove(temp_path)
            os.remove(temp_path2)
        except:
            pass
        
    return path
        
async def insert_image(driver, image:discord.Attachment, second_image=False):
    if not second_image:
        temp_path = await download_image(image)
    else:
        temp_path = await download_image(image, "2")
    # crop image to a square
    await crop_image(temp_path)
    
    try:
        wb_add = driver.find_element(by=By.ID, value="wb-add")
        wb_add.click()
    except:
        pass
    
    # Find the label that contains "photo..." string
    input_photo_button = driver.find_element(by=By.XPATH, value="//input[@title='Insert photo...']")
    input_photo_button.send_keys(os.path.abspath(temp_path))
    
    print("added image...")
    return temp_path

async def insert_text(driver:webdriver.Firefox, text:str):
    try:
        wb_add = driver.find_element(by=By.ID, value="wb-add")
        wb_add.click()
    except:
        pass
    
    wait = WebDriverWait(driver, 10)
    
    # Find the label that contains "text..." string
    wait.until(EC.visibility_of_element_located((By.ID, "add_text")))
    input_text_button = driver.find_element(by=By.ID, value="add_text")
    input_text_button.click()
    
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "textbar_text")))
    text_area = driver.find_element(by=By.CLASS_NAME, value="textbar_text")
    
    if "\\n" in text:
        formatted_text = text.replace("\\n", "\n")
    else:
        text_list = filter_non_bmp_characters(text).split(" ")
        formatted_text = text_list[0]
        latest_line = text_list[0]
        for word in text_list[1:]:
            if len(latest_line) + len(word) > 11 and len(latest_line) > 0 and len(word) > 1:
                formatted_text += "\n" + word
                latest_line = word
            else:
                formatted_text += " " + word
                latest_line += " " + word
    
    text_area.clear()
    text_area.send_keys(formatted_text)
    
    ok_text_button = driver.find_element(by=By.CLASS_NAME, value="ok_text")
    ok_text_button.click()
    
    print("added text...")
    
def filter_non_bmp_characters(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

async def download_image(image:discord.Attachment, num_str=""):
    data = await get_data_from_url(image.url)
    extention = imghdr.what(io.BytesIO(data))
    filename = f"temp{num_str}.{extention}"
    with open(f"img/{filename}", "wb") as f:
        f.write(data)
    return "img/" + filename

async def crop_image(path:str):
    im = PIL.Image.open(path)
    width, height = im.size
    new_size = min(width, height)
    # Thanks you, stackoverflow :)
    left = (width - new_size)/2
    top = (height - new_size)/2
    right = (width + new_size)/2
    bottom = (height + new_size)/2
    
    im = im.crop((left, top, right, bottom))
    im.save(path)
    
# method to get the downloaded file name
# thanks again, stackoverflow
def getDownLoadedFileName(driver, waitTime):
    driver.execute_script("window.open()")
    # switch to new tab
    driver.switch_to.window(driver.window_handles[-1])
    # navigate to firefox downloads
    driver.get('about:downloads')
    # define the endTime
    endTime = time.time()+waitTime
    while True:
        try:
            fileName = driver.execute_script("return document.querySelector('#contentAreaDownloadsView .downloadMainArea .downloadContainer description:nth-of-type(1)').value")
            if fileName:
                return fileName
        except Exception as e:
            print(e)
            pass
        time.sleep(1)
        if time.time() > endTime:
            break
    
async def get_data_from_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
    
    return data

# only for debugging purposes
class Test:
    def __init__(self, url):
        self.url = url

if __name__ == "__main__": # for debugging purposes
    import asyncio
    test = Test("https://img.freepik.com/photos-gratuite/morskie-oko-tatry_1204-510.jpg?t=st=1734421226~exp=1734424826~hmac=e6f56fce363081df8e0b909c4a20e82de459daabfe392082aaf3e99231204986&w=2000")
    
    test_str = asyncio.run(make_heart_locket(test, "Hello, world!", test, orientation="image-image", headless=False))
    
    print(test_str)