import random
import discord
import requests
import responses_data
import json

def respond(message:str, guild):
    lower_message = message.lower()
    
    with open("src/bot_stuff/servers.json", "r") as f:
        server_list = json.load(f)
    
    if feature_activated(server_list, guild, "backflip"):
        if "backflip" in lower_message or "back flip" in lower_message:
            return responses_data.backflip_gifs[random.randint(0, len(responses_data.backflip_gifs) - 1)]
    
    for word in lower_message.split():
        if word in responses_data.french_insults and feature_activated(server_list, guild, "insults"):
            return responses_data.fr_responses_to_insults[random.randint(0, len(responses_data.fr_responses_to_insults) - 1)]
        
        if word.__len__() < 5:
            continue
        if (word.startswith("di") or word.startswith("dy")) and feature_activated(server_list, guild, "di"):
            return alpha_characters_of(word[2:])
        if (word.startswith("cri") or word.startswith("cry")) and feature_activated(server_list, guild, "cri"):
            return alpha_characters_of(word[3:]).upper()

def alpha_characters_of(word:str) -> str:
    return ''.join([i for i in word if i.isalpha()])

def feature_activated(server_list, guild, feature:str) -> bool:
    return server_list[str(guild.id)][feature]

def joke_command():
    response = requests.get("https://official-joke-api.appspot.com/random_joke")
    json = response.json()
    return json["setup"] + "\n" + json["punchline"]

def features_command(guild) -> discord.Embed:
    with open("src/bot_stuff/servers.json", "r") as f:
        server_list = json.load(f)
    
    title =  "Available features"
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
    desc += "If a message contains a french insult, the bot will answer with a random response"
    embed.add_field(name=title, value=desc, inline=False)
    
    footer = "To activate or deactivate a feature, use the /activate or /deactivate commands"
    embed.set_footer(text=footer)
    
    return embed

def status_string(bool):
    return "" if bool else "(deactivated)"

def help_command() -> discord.Embed:
    title =  "Available commands"
    embed = discord.Embed(title=title, color=discord.Color.yellow())
    
    title = "/joke:" 
    desc = "The bot will answer with a random joke"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "/features:"
    desc = "The bot will answer with a list of all the available features (automatic responses)"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "/activate or /deactivate [feature]:"
    desc = "Activate or deactivate a feature"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "/help:"
    desc = "Shows this message"
    embed.add_field(name=title, value=desc, inline=False)
    
    return embed

def activate_command(guild, feature:str):
    with open("src/bot_stuff/servers.json", "r") as f:
        server_list = json.load(f)
    
    if server_list[str(guild.id)][feature] == True:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="Feature already activated", value=f"The '{feature}' feature is already activated for this server", inline=False)
        return embed
    
    server_list[str(guild.id)][feature] = True
    
    with open("src/bot_stuff/servers.json", "w") as f:
        json.dump(server_list, f, indent=4)
        
    embed = discord.Embed(color=discord.Color.green())
    embed.add_field(name="Feature activated", value=f"The '{feature}' feature has been activated for this server", inline=False)
    return embed

def deactivate_command(guild, feature:str):
    with open("src/bot_stuff/servers.json", "r") as f:
        server_list = json.load(f)
    
    if server_list[str(guild.id)][feature] == False:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="Feature already deactivated", value=f"The '{feature}' feature is already deactivated for this server", inline=False)
        return embed
    
    server_list[str(guild.id)][feature] = False
    
    with open("src/bot_stuff/servers.json", "w") as f:
        json.dump(server_list, f, indent=4)
    
    embed = discord.Embed(color=discord.Color.yellow())
    embed.add_field(name="Feature deactivated", value=f"The '{feature}' feature has been deactivated for this server", inline=False)
    return embed