import requests

def get_random_meme() -> tuple[str, str]:
    filepath = "img/meme/random_meme."
    extension = "null"
    k = 0
    max_tries = 10
    extension_list = ["jpg", "png", "jpeg", "gif"]
    try:
        while extension not in extension_list and k < max_tries:
            if k > 0:
                print("Trying again...")
            
            # get json from https://meme-api.com/gimme
            response = requests.get("https://meme-api.com/gimme")
            json_response = response.json()
            
            image_url = json_response["url"]
            upvotes = json_response["ups"]
            
            extension = image_url.split(".")[-1]
            
            k += 1
        
        if k == max_tries and extension not in extension_list:
            return "error", "0"
            
        image_response = requests.get(image_url)
        filepath += extension
        with open(filepath, "wb") as f:
            f.write(image_response.content)
            
        print("Got meme from " + image_url)
        return filepath, upvotes
    
    except Exception as e:
        print(e)
        return "error", "0"
    
def get_random_monkey(width: int|None = None, height: int|None = None) -> str:
    filepath = "img/meme/monkey/random_monkey.png"
    try:
        if width is not None and height is not None:
            image_response = requests.get(f"https://www.placemonkeys.com/{width}/{height}?random")
        elif width is not None:
            image_response = requests.get(f"https://www.placemonkeys.com/{width}?random")
        elif height is not None:
            image_response = requests.get(f"https://www.placemonkeys.com/{height}?random")
        else:
            image_response = requests.get("https://www.placemonkeys.com/2160?random")
        
        with open(filepath, "wb") as f:
            f.write(image_response.content)
            
        print("Got the monkey ;)")
        return filepath
    
    except Exception as e:
        print(e)
        return "error"