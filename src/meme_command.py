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
    
def get_random_monkey():
    filepath = "img/meme/monkey/random_monkey.png"
    try:
        image_response = requests.get("https://www.placemonkeys.com/900/900?random")
        
        with open(filepath, "wb") as f:
            f.write(image_response.content)
            
        print("Got the monkey ;)")
        return filepath
    
    except Exception as e:
        print(e)
        return "error"