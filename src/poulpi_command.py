import random
import os
import json

def poulpi_picture(state:str='all') -> str: # returns the path of the picture
    if state == 'happy' or state == 'sad':
        img_list: list[str] = os.listdir('img/poulpi/' + state)
        return 'img/poulpi/' + state + '/' + random.choice(img_list)    
    
    happy_list: list[str] = os.listdir('img/poulpi/happy')
    sad_list: list[str] = os.listdir('img/poulpi/sad')
    
    rand_state: str = random.choice(['happy', 'sad'])
    
    if rand_state == 'happy':
        return 'img/poulpi/happy/' + random.choice(happy_list)
    elif rand_state == 'sad':
        return 'img/poulpi/sad/' + random.choice(sad_list)
    
    return 'error'

def get_msg_reactions(poulpi_path: str) -> list[str]:
    with open('src/responses_data/poulpi_reactions.json', 'r', encoding='utf8') as f:
        reactions: dict[str, list[str]] = json.load(f)
    
    for reaction in reactions:
        if reaction in poulpi_path:
            return reactions[reaction]
    
    return []