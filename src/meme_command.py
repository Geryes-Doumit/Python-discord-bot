import requests

def get_random_meme():
    filepath = "img/random_meme.jpg"
    try:
        # get json from https://meme-api.com/gimme
        response = requests.get("https://meme-api.com/gimme")
        json_response = response.json()
        
        image_url = json_response["url"]
        
        image_response = requests.get(image_url)
        
        with open(filepath, "wb") as f:
            f.write(image_response.content)
            
        print("Got meme from " + image_url)
        return filepath
    
    except Exception as e:
        print(e)
        return "error"