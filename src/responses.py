import random
from sre_constants import IN
import discord
import requests
import data

def respond(message:str):
    lower_message = message.lower()
    
    if "backflip" in lower_message or "back flip" in lower_message:
        return data.backflip_gifs[random.randint(0, len(data.backflip_gifs) - 1)]
    
    for word in lower_message.split():
        if word in data.french_insults:
            return data.fr_responses_to_insults[random.randint(0, len(data.fr_responses_to_insults) - 1)]
        
        if word.__len__() < 5:
            continue
        if word.startswith("di") or word.startswith("dy"):
            return alpha_characters_of(word[2:])
        if word.startswith("cri") or word.startswith("cry"):
            return alpha_characters_of(word[3:]).upper()

def alpha_characters_of(word:str) -> str:
    return ''.join([i for i in word if i.isalpha()])

def joke_command():
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    json = response.json()
    return json["setup"] + "\n" + json["punchline"]

def features_command() -> discord.Embed:
    title =  "Available features"
    embed = discord.Embed(title=title, color=discord.Color.yellow())
    
    title = "Backflip GIFs:" 
    desc = "When a message contains 'backflip', the bot will respond with a backflip GIF"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "Di:"
    desc = "If a word starts with 'di' or 'dy', the bot will answer with the rest of the word"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "Cri:"
    desc = "If a word starts with 'cri' or 'cry', the bot will answer with the rest of the word in uppercase"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "Insults:"
    desc = "If a message contains a french insult, the bot will answer with a random response"
    embed.add_field(name=title, value=desc, inline=False)
    
    return embed

def help_command() -> discord.Embed:
    title =  "Available commands"
    embed = discord.Embed(title=title, color=discord.Color.yellow())
    
    title = "/joke:" 
    desc = "The bot will answer with a random joke"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "/features:"
    desc = "The bot will answer with a list of all the available features (automatic responses)"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "/help:"
    desc = "Shows this message"
    embed.add_field(name=title, value=desc, inline=False)
    
    return embed