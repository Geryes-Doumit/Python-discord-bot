import contextlib
import io
import random
import cv2
from PIL import Image
import discord
import aiohttp
import imageio
import numpy as np
import os
import imghdr

import insightface
from insightface.app import FaceAnalysis
import aiohttp
import onnxruntime

MODEL_PATH = os.environ['USERPROFILE'] + '/.insightface/models/inswapper_128/inswapper_128.onnx'
# MODEL_PATH = "/Users/Shared/Inswapper/inswapper_128.onnx"

async def swap_faces_hero(attachment:discord.Attachment, hero_choice:str):
    with contextlib.redirect_stdout(None):
        app = FaceAnalysis(name='buffalo_l')
        app.prepare(ctx_id=0, det_size=(640, 640))

    data = await get_data_from_url(attachment.url)
    
    arr = np.asarray(bytearray(data), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    # convert image to jpg if it is png
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    faces = app.get(img)

    if len(faces) == 0:
        return 'noface'
    
    face_img = random.choice(faces)
    
    with contextlib.redirect_stdout(None):
        swapper = insightface.model_zoo.get_model(MODEL_PATH)
    
    if hero_choice == "random":
        face_swap_images = os.listdir('img/hero_swap')
        hero = cv2.imread('img/hero_swap/' + random.choice(face_swap_images))
    else:
        hero = cv2.imread('img/hero_swap/' + hero_choice)
    result = hero.copy()
    face_hero = app.get(hero)[0]
    result = swapper.get(result, face_hero, face_img, paste_back=True) # type: ignore
    tosave = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_RGB2BGR)) # type: ignore
    tosave.save('img/face_swap_result.jpg')
    
    return 'img/face_swap_result.jpg'

async def swap_faces(source:discord.Attachment, target:discord.Attachment, replace_all:bool = False,
                     discard_unswapped:bool = False):
    with contextlib.redirect_stdout(None):
        app = FaceAnalysis(name='buffalo_l')
        app.prepare(ctx_id=0, det_size=(640, 640))

    data = await get_data_from_url(source.url)
    
    if imghdr.what(io.BytesIO(data)) == 'gif':
        return 'gif_source'
    
    arr = np.asarray(bytearray(data), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    # convert image to jpg if it is png
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    faces_source = app.get(img)

    if len(faces_source) == 0:
        return 'noface_source'
    
    face_source = random.choice(faces_source)
    
    data = await get_data_from_url(target.url)
    
    if imghdr.what(io.BytesIO(data)) == 'gif':
        return gif_swap_faces(app, face_source, target, discard_unswapped)
    
    arr = np.asarray(bytearray(data), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    # convert image to jpg if it is png
    if img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)

    faces_target = app.get(img)

    if len(faces_target) == 0:
        return 'noface_target'
    
    face_target = random.choice(faces_target)
    
    with contextlib.redirect_stdout(None):
        swapper = insightface.model_zoo.get_model(MODEL_PATH)
    
    result = img.copy()
    
    if replace_all and len(faces_target) > 1:
        print(f'Replacing {len(faces_target)} faces...')
        for f in faces_target:
            print('Replacing face...')
            result = swapper.get(result, f, face_source, paste_back=True) # type: ignore
    else:
        print('Replacing face...')
        result = swapper.get(result, face_target, face_source, paste_back=True) # type: ignore
    
    print('Saving image...')
    
    tosave = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_RGB2BGR)) # type: ignore
    tosave.save('img/face_swap_result.jpg')
    
    print('Done.')
    
    return 'img/face_swap_result.jpg'

def gif_swap_faces(app:FaceAnalysis, face_source:list, target:discord.Attachment, discard_unswapped:bool):
    video = cv2.VideoCapture(target.url)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    if (total_frames > 200):
        print("Too many frames!")
        return "too_many_frames"
        
    with contextlib.redirect_stdout(None):
        swapper = insightface.model_zoo.get_model(MODEL_PATH)
    
    success, frame = video.read()
    framelist = []
    print(f"Processing {int(video.get(cv2.CAP_PROP_FRAME_COUNT))} frames...")
    while success:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faces = app.get(frame_rgb)
        if len(faces) == 0:
            print("No face found")
            if not discard_unswapped: framelist.append(frame_rgb)
            success, frame = video.read()
            continue
        
        print('Replacing face in frame '+ str(len(framelist)) +' ...')
        frame_rgb = swapper.get(frame_rgb, faces[0], face_source, paste_back=True) # type: ignore
        framelist.append(frame_rgb)
        
        success, frame = video.read()
    
    imageio.mimsave('img/face_swap_result.gif', 
                    framelist, fps=video.get(cv2.CAP_PROP_FPS), format='GIF', loop=0)
    video.release()
    print("Done.")
    return 'img/face_swap_result.gif'

async def get_data_from_url(url):
        
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
    
    return data