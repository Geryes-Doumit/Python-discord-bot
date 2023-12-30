from ast import arg

from interactions import Embed
from bot_stuff import private_bot_data
import discord
from discord import app_commands
from discord.ext import commands
import responses

async def send_message(message:discord.message, user_message:str):
    try:
        response = responses.respond(user_message)
        if response != None:
            await message.reply(response)
    
    except Exception as e:
        print(e)
        
def run_bot():
    TOKEN = private_bot_data.token
    
    intents = discord.Intents.all()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='/', intents=intents)

    @bot.tree.command()
    async def features(interaction):
        await interaction.response.send_message(embed=responses.features_command())
    
    @bot.tree.command()
    async def joke(interaction):
        await interaction.response.send_message(content=responses.joke_command())
    
    bot.tree.remove_command('help')
    @bot.tree.command()
    async def help(interaction):
        await interaction.response.send_message(embed=responses.help_command())

    @bot.event
    async def on_ready():
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
                
    bot.run(TOKEN)