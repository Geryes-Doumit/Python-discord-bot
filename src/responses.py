import random
import discord
import requests
from blagues_api import BlaguesAPI
from bot_stuff import blague_api_data
import json


#-----------------------------
#Automatic responses
#-----------------------------

def respond(message:str, guild:discord.Guild|None) -> None|str:
    
    if guild is None:
        return
    
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

def feature_enabled(server_list:dict, guild, feature:str) -> bool:
    return server_list[str(guild.id)][feature]


#-----------------------------
#Commands
#-----------------------------

async def joke_command(lang:str) -> str:
    if lang == "fr":
        blagues = BlaguesAPI(blague_api_data.TOKEN)
        joke = await blagues.random()
        return joke.joke + "\n" + joke.answer
    
    elif lang == "en":
        response = requests.get("https://official-joke-api.appspot.com/random_joke")
        json = response.json()
        return json["setup"] + "\n" + json["punchline"]
    
    else:
        return "Invalid language."

def features_command(guild:discord.Guild) -> discord.Embed:
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
    return " `enabled`" if bool else " `disabled`"

def help_command(guild) -> discord.Embed:
    title =  "Available commands"
    embed = discord.Embed(title=title, color=discord.Color.yellow())
    
    title = "Github repository" 
    desc = "To see all available commands and features, visit the \
        [Github repository](https://github.com/Geryes-Doumit/Python-discord-bot)"
    embed.add_field(name=title, value=desc, inline=False)
    
    title = "Features"
    desc = "To see the status of the automatic responses, use the `/features` command"
    embed.add_field(name=title, value=desc, inline=False)
    
    return embed

def enable_command(guild:discord.Guild | None, feature:str) -> discord.Embed:
    if guild is None:
        return discord.Embed(color=discord.Color.red()).add_field(name="Error", value="This command can only be used in a server", inline=False)
    
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

def disable_command(guild:discord.Guild | None, feature:str) -> discord.Embed:
    if guild is None:
        return discord.Embed(color=discord.Color.red()).add_field(name="Error", value="This command can only be used in a server", inline=False)
    
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

def roast_command(name:str, guild:discord.Guild | None, server_specific=False) -> str:
    all_roasts = json.load(open("src/responses_data/roasts_per_server.json", "r", encoding='utf-8'))
    general_roasts = all_roasts["general"]
    roasts = []
    
    if guild is not None:
        try :
            if not server_specific:
                roasts += general_roasts
            roasts += all_roasts[str(guild.id)]
            
        except KeyError: # if the server doesn't have a list of specific roasts yet
            roasts += general_roasts
    
    else:
        roasts += general_roasts
    
    index = random.randint(0, len(roasts) - 1)
    roast = roasts[index]
    return roast.replace("@n", name)

def findroast_command(roastIndex:int, guild:discord.Guild) -> tuple[str, bool]:
    all_roasts = json.load(open("src/responses_data/roasts_per_server.json", "r", encoding='utf-8'))
    
    roasts = []
    success = False
    
    try :
        roasts += all_roasts[str(guild.id)]
    except KeyError: # if the server doesn't have a list of specific roasts yet
        return "No roasts found.", success
    
    try :
        roast = roasts[roastIndex]
    except Exception:
        return "Invalid roast index. Use `/roast list` to see all the roasts and their indexes.", success
    
    success = True
    return roast, success

def deleteroast_command(roastIndex:int, guild:discord.Guild) -> str:
    all_roasts = json.load(open("src/responses_data/roasts_per_server.json", "r", encoding='utf-8'))
    
    roasts = []
    
    try :
        roasts += all_roasts[str(guild.id)]
    except KeyError: # if the server doesn't have a list of specific roasts yet
        return "No roasts to delete."
    
    try :
        roast = roasts[roastIndex]
        all_roasts[str(guild.id)].remove(roast)
        
        if len(all_roasts[str(guild.id)]) == 0:
            del all_roasts[str(guild.id)]
            
    except Exception:
        return "Invalid roast index. Use `/roast list` to see all the roasts and their indexes."
    
    with open("src/responses_data/roasts_per_server.json", "w") as f:
        json.dump(all_roasts, f, indent=4)
    
    return f"Successfully deleted the roast. ```{roast}```"

def addroast_command(roast:str, guild:discord.Guild | None, server_specific:bool=True) -> tuple[str, bool]:
    ephemeral = True
    
    if guild is None:
        return "This command can only be used in a server", ephemeral
    
    if not roast.__contains__('@n'):
        return "Roasts must contain '@n' to specify where the name of the person to roast goes", ephemeral
    
    with open("src/responses_data/roasts_per_server.json", "r", encoding='utf-8') as f:
        all_roasts = json.load(f)
    
    try :
        if server_specific:
            all_roasts[str(guild.id)].append(roast)
        else:
            all_roasts["general"].append(roast)
    
    except KeyError: # if the server doesn't have a list of roasts yet
        if server_specific:
            all_roasts[str(guild.id)] = [roast]
        
    with open("src/responses_data/roasts_per_server.json", "w") as f:
        json.dump(all_roasts, f, indent=4)
    
    ephemeral = False
    return f"Roast added to the {'server' if server_specific else 'general'} roasts.```{roast}```", ephemeral

def listroasts_command(guild:discord.Guild | None, server_specific:bool):
    all_roasts = json.load(open("src/responses_data/roasts_per_server.json", "r", encoding='utf-8'))
    
    general_roasts:list[str] = all_roasts["general"]
    server_roasts = []
    
    try :
        server_roasts = all_roasts[str(guild.id)]
    except KeyError as e:
        print(e)
        pass
    
    messages:list[str] = []
    
    content:str = ""
    
    if not server_specific:
        content += "## General roasts\n"
        content += "-# _These general roasts are available in every server, they cannot be deleted._\n"
        for roast in general_roasts:
            if len(content) + len(roast) > 2000:
                messages.append(content)
                content = ""
            content += "- " + roast + "\n"
        
        messages.append(content)
        content = ""
    
    content += "## Server roasts\n"
    content += "-# _To delete a server roast, use the `/roast delete` command with the correct index._\n"
    if len(server_roasts) == 0:
        content += "No server roasts yet, use `/roast add` to add one"
    else:
        for i in range(len(server_roasts)):
            roast = server_roasts[i]
            if len(content) + len(roast) > 2000:
                messages.append(content)
                content = ""
            content += str(i+1) + ". " + roast + "\n"
        
        messages.append(content)
    
    return messages