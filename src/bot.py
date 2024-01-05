from bot_stuff import private_bot_data
import discord
from discord import app_commands
from discord.ext import commands
import responses
import json

async def send_message(message:discord.message, user_message:str):
    try:
        response = responses.respond(user_message, message.guild)
        if response != None:
            await message.reply(response)
    
    except Exception as e:
        print(e)
        
def run_bot():
    TOKEN = private_bot_data.token
    
    intents = discord.Intents.all()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='/', intents=intents)

    @bot.tree.command(description="List all the available features")
    async def features(interaction):
        await interaction.response.send_message(embed=responses.features_command(interaction.guild))
        
    @app_commands.command(name="activate",description="Activate a feature")
    @app_commands.choices(feature=[
        discord.app_commands.Choice(name="di", value="di"),
        discord.app_commands.Choice(name="cri", value="cri"),
        discord.app_commands.Choice(name="backflip", value="backflip"),
        discord.app_commands.Choice(name="insults", value="insults")
    ])
    async def activate(interaction, feature:str):
        await interaction.response.send_message(embed=responses.activate_command(interaction.guild, feature))
        
    @app_commands.command(name="deactivate",description="Deactivate a feature")
    @app_commands.choices(feature=[
        discord.app_commands.Choice(name="di", value="di"),
        discord.app_commands.Choice(name="cri", value="cri"),
        discord.app_commands.Choice(name="backflip", value="backflip"),
        discord.app_commands.Choice(name="insults", value="insults")
    ])
    async def deactivate(interaction, feature:str):
        await interaction.response.send_message(embed=responses.deactivate_command(interaction.guild, feature))
    
    bot.tree.add_command(activate)
    bot.tree.add_command(deactivate)
    
    @app_commands.command(name="joke",description="Tell a joke")
    @app_commands.choices(lang=[
        discord.app_commands.Choice(name="fr", value="fr"),
        discord.app_commands.Choice(name="en", value="en")
    ])
    async def joke(interaction, lang:str):
        await interaction.response.send_message(content=await responses.joke_command(lang))
        
    bot.tree.add_command(joke)
    
    bot.tree.remove_command('help')
    @bot.tree.command(description="help message")
    async def help(interaction):
        await interaction.response.send_message(embed=responses.help_command())

    @bot.event
    async def on_ready():
        update_server_list(bot)
        print("Bot is ready 🔥🔥")
        
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(e)
    
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        
        await send_message(message, message.content)
        await bot.process_commands(message)
        
    @bot.event
    async def on_guild_join(guild):
        update_server_list(bot)
                
    bot.run(TOKEN)
    
def update_server_list(bot:commands.Bot):
    filename = "src/bot_stuff/servers.json"
    with open(filename, "r") as f:
        server_list = json.load(f)
    
    for guild in bot.guilds:
        if str(guild.id) not in server_list:
            print(f"Adding {guild.name} to the server list")
            server_list[str(guild.id)] = {}
            server_list[str(guild.id)]["server_name"] = guild.name
            server_list[str(guild.id)]["di"] = True
            server_list[str(guild.id)]["cri"] = True
            server_list[str(guild.id)]["backflip"] = True
            server_list[str(guild.id)]["insults"] = True
    
    with open(filename, "w") as f:
        json.dump(server_list, f, indent=4)