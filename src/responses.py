import random
import discord
import requests
from blagues_api import BlaguesAPI
from bot_stuff import blague_api_data
import json

def respond(message:str, guild):
    lower_message = message.lower()
    
    with open("src/bot_stuff/servers.json", "r", encoding='utf-8') as f:
        server_list = json.load(f)
    
    if feature_enabled(server_list, guild, "backflip"):
        if "backflip" in lower_message or "back flip" in lower_message:
            backflip_gifs = json.load(open("src/responses_data/backflip_gifs.json", "r", encoding='utf-8'))
            return backflip_gifs[random.randint(0, len(backflip_gifs) - 1)]
    
    json_insults = json.load(open("src/responses_data/fr_insults.json", "r", encoding='utf-8'))
    fr_short_insults = json_insults["single-word-insults"]
    fr_multiword_insults = json_insults["multi-word-insults"]
    fr_responses_to_insults = json.load(open("src/responses_data/fr_responses_to_insults.json", "r", encoding='utf-8'))
    
    for insult in fr_multiword_insults:
        if insult in lower_message and feature_enabled(server_list, guild, "insults"):
            return fr_responses_to_insults[random.randint(0, len(fr_responses_to_insults) - 1)]
    
    for word in lower_message.split():
        if alpha_characters_of(word) in fr_short_insults and feature_enabled(server_list, guild, "insults"):
            return fr_responses_to_insults[random.randint(0, len(fr_responses_to_insults) - 1)]
        
        if alpha_characters_of(word).__len__() < 5:
            continue
        if (word.startswith("di") or word.startswith("dy")) and feature_enabled(server_list, guild, "di"):
            return alpha_characters_of(word[2:])
        if (word.startswith("cri") or word.startswith("cry")) and feature_enabled(server_list, guild, "cri"):
            return alpha_characters_of(word[3:]).upper()

def alpha_characters_of(word:str) -> str:
    return ''.join([i for i in word if i.isalpha()])

def feature_enabled(server_list, guild, feature:str) -> bool:
    return server_list[str(guild.id)][feature]

async def joke_command(lang:str) -> str:
    if lang == "fr":
        blagues = BlaguesAPI(blague_api_data.TOKEN)
        joke = await blagues.random()
        return joke.joke + "\n" + joke.answer
    
    elif lang == "en":
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        json = response.json()
        return json["setup"] + "\n" + json["punchline"]

def features_command(guild) -> discord.Embed:
    with open("src/bot_stuff/servers.json", "r", encoding='utf-8') as f:
        server_list = json.load(f)
    
    title =  "Available features (automatic responses)"
    embed = discord.Embed(title=title, color=discord.Color.yellow())
    
    title = "Backflip GIFs:" + status_string(server_list[str(guild.id)]["backflip"])
    desc = "When a message contains 'backflip', the bot will respond with a backflip GIF"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "Di:" + status_string(server_list[str(guild.id)]["di"])
    desc = "If a word starts with 'di' or 'dy', the bot will answer with the rest of the word"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "Cri:" + status_string(server_list[str(guild.id)]["cri"])
    desc = "If a word starts with 'cri' or 'cry', the bot will answer with the rest of the word in uppercase"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "Insults:" + status_string(server_list[str(guild.id)]["insults"])
    desc = "If a message contains a french insult, the bot will answer with a random response"
    embed.add_field(name=title, value=desc, inline=False)
    
    footer = "To activate or deactivate a feature, use the /enable or /disable commands"
    embed.set_footer(text=footer)
    
    return embed

def status_string(bool):
    return "" if bool else " (disabled)"

def help_command(guild) -> discord.Embed:
    title =  "Available commands"
    embed = discord.Embed(title=title, color=discord.Color.yellow())
    
    title = "/joke [lang]:" 
    desc = "Answers with a random joke in the specified language"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "/blague:"
    desc = "Answers with a random joke in french"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "/features:"
    desc = "Shows a list of all the available features (automatic responses)"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "/enable or /disable [feature]:"
    desc = "Activates or deactivates a feature"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "/roast [name]:"
    desc = "Roasts the specified person"
    embed.add_field(name=title, value=desc, inline=False)
    
    if guild.name == "Info & réseaux":
        title = "/edt"
        desc = "Récupère et envoie l'emploi du temps"
        embed.add_field(name=title, value=desc, inline=False)
    
    title = "/help:"
    desc = "Shows this message"
    embed.add_field(name=title, value=desc, inline=False)
    
    return embed

def enable_command(guild, feature:str):
    with open("src/bot_stuff/servers.json", "r", encoding='utf-8') as f:
        server_list = json.load(f)
    
    if server_list[str(guild.id)][feature] == True:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="Feature already enabled", value=f"The '{feature}' feature is already enabled for this server", inline=False)
        return embed
    
    server_list[str(guild.id)][feature] = True
    
    with open("src/bot_stuff/servers.json", "w") as f:
        json.dump(server_list, f, indent=4)
        
    embed = discord.Embed(color=discord.Color.green())
    embed.add_field(name="Feature enabled", value=f"The '{feature}' feature has been enabled for this server", inline=False)
    return embed

def disable_command(guild, feature:str):
    with open("src/bot_stuff/servers.json", "r", encoding='utf-8') as f:
        server_list = json.load(f)
    
    if server_list[str(guild.id)][feature] == False:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="Feature already disabled", value=f"The '{feature}' feature is already disabled for this server", inline=False)
        return embed
    
    server_list[str(guild.id)][feature] = False
    
    with open("src/bot_stuff/servers.json", "w") as f:
        json.dump(server_list, f, indent=4)
    
    embed = discord.Embed(color=discord.Color.yellow())
    embed.add_field(name="Feature disabled", value=f"The '{feature}' feature has been disabled for this server", inline=False)
    return embed

def roast_command(name:str, guild:discord.guild) -> str:
    all_roasts = json.load(open("src/responses_data/roasts_per_server.json", "r", encoding='utf-8'))
    
    try :
        roasts = all_roasts[str(guild.id)] + all_roasts["general"]
    except Exception as e:
        roasts = all_roasts["general"]
    
    return roasts[random.randint(0, len(roasts) - 1)] + " " + name + "."