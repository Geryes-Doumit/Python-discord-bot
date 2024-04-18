import random
import cv2
from PIL import Image
import discord
import aiohttp
import numpy as np
import os

import insightface
from insightface.app import FaceAnalysis
import aiohttp

async def swap_faces_hero(attachment:discord.Attachment, hero_choice:str):
    app = FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=0, det_size=(640, 640))

    data = await get_data_from_url(attachment.url)
    
    arr = np.asarray(bytearray(data), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    # convert image to jpg if it is png
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    face = app.get(img)

    if face.__len__() == 0:
        return 'noface'
    
    face_img = random.choice(face)
    
    swapper = insightface.model_zoo.get_model(os.environ['USERPROFILE'] + '/.insightface/models/inswapper_128/inswapper_128.onnx')
    
    if hero_choice == "random":
        face_swap_images = os.listdir('img/hero_swap')
        hero = cv2.imread('img/hero_swap/' + random.choice(face_swap_images))
    else:
        hero = cv2.imread('img/hero_swap/' + hero_choice)
    result = hero.copy()
    face_hero = app.get(hero)[0]
    result = swapper.get(result, face_hero, face_img, paste_back=True)
    tosave = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
    tosave.save('img/hero_swap_result.jpg')
    
    return 'img/face_swap_result.jpg'

async def swap_faces(source:discord.Attachment, target:discord.Attachment, replace_all:bool = False):
    app = FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=0, det_size=(640, 640))

    data = await get_data_from_url(source.url)
    
    arr = np.asarray(bytearray(data), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    # convert image to jpg if it is png
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    face = app.get(img)

    if face.__len__() == 0:
        return 'noface_source'
    
    face_source = random.choice(face)
    
    data = await get_data_from_url(target.url)
    
    arr = np.asarray(bytearray(data), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    # convert image to jpg if it is png
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    face = app.get(img)

    if face.__len__() == 0:
        return 'noface_target'
    
    if replace_all:
        face_target = face
    else:
        face_target = random.choice(face)
    
    swapper = insightface.model_zoo.get_model(os.environ['USERPROFILE'] + '/.insightface/models/inswapper_128/inswapper_128.onnx')
    
    
    result = img.copy()
    
    if replace_all and len(face_target) > 1:
        for f in face_target:
            print('Replacing face...')
            result = swapper.get(result, f, face_source, paste_back=True)
    else:
        print('Replacing face...')
        result = swapper.get(result, face_target, face_source, paste_back=True)
    
    print('Saving image...')
    
    tosave = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
    tosave.save('img/hero_swap_result.jpg')
    
    print('Done.')
    
    return 'img/hero_swap_result.jpg'

async def get_data_from_url(url):
        
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
    
    return data
