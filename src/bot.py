import datetime
import os
from bot_stuff import private_bot_data
import discord
from discord import app_commands
from discord.ext import commands
import responses
import face_swap
import edt_command
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
    
     
    @app_commands.command(name="enable", description="enables a feature")
    @app_commands.choices(feature=[
        discord.app_commands.Choice(name="di", value="di"),
        discord.app_commands.Choice(name="cri", value="cri"),
        discord.app_commands.Choice(name="backflip", value="backflip"),
        discord.app_commands.Choice(name="insults", value="insults")
    ])
    async def enable(interaction, feature:str):
        await interaction.response.send_message(embed=responses.enable_command(interaction.guild, feature))
    
    
    @app_commands.command(name="disable",description="disables a feature")
    @app_commands.choices(feature=[
        discord.app_commands.Choice(name="di", value="di"),
        discord.app_commands.Choice(name="cri", value="cri"),
        discord.app_commands.Choice(name="backflip", value="backflip"),
        discord.app_commands.Choice(name="insults", value="insults")
    ])
    async def disable(interaction, feature:str):
        await interaction.response.send_message(embed=responses.disable_command(interaction.guild, feature))
    
    bot.tree.add_command(enable)
    bot.tree.add_command(disable)
    
    
    @app_commands.command(name="joke", description="Sends a joke in the specified language")
    @app_commands.choices(lang=[
        discord.app_commands.Choice(name="en", value="en"),
        discord.app_commands.Choice(name="fr", value="fr")
    ])
    async def joke(interaction, lang:str):
        await interaction.response.send_message(content=await responses.joke_command(lang))
        
    bot.tree.add_command(joke)
    
    
    @bot.tree.command(description="Sends a joke in french")
    async def blague(interaction):
        await interaction.response.send_message(content=await responses.joke_command("fr"))
        
    
    @bot.tree.command(description="Roast someone (a random roast will be chosen from the database)")
    async def roast(interaction, name:str):
        if (name.__len__() > 100):
            await interaction.response.send_message(content="You've exceeded the 100-character limit.", ephemeral=True)
            return
        await interaction.response.send_message(content=responses.roast_command(name, interaction.guild))
        
    
    @app_commands.command(name="edt",description="EDT de la semaine")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name="semaine", value="semaine"),
        discord.app_commands.Choice(name="jour", value="jour"),
        discord.app_commands.Choice(name="demain", value="demain")
    ])
    @app_commands.describe(critere="Le critère de recherche (par défaut: 2ir)",
                           type="Le type de recherche (par défaut: semaine)",
                           force="Force un nouveau screenshot même s'il y en a déjà créé il y a moins de 10 min (par défaut: False)")
    async def edt(interaction, critere:str="2ir", type:str="semaine", force:bool=False):
        # if interaction.guild.name != "Info & réseaux":
        #     await interaction.response.send_message(content="This command is only available in the Info & réseaux server.", ephemeral=True)
        #     return
        # if "emploi-du-temps" not in interaction.channel.name:
        #     await interaction.response.send_message(content="This command is only available in the #emploi-du-temps channel.", ephemeral=True)
        #     return
        if (critere.__len__() > 20):
            await interaction.response.send_message(content="You've exceeded the 20-character limit.", ephemeral=True)
            return
        
        await interaction.response.defer()

        img_path = edt_command.take_screenshot(critere, type, force)
        if img_path == "samedi" or img_path == "dimanche":
            return await interaction.followup.send(content=f"Tu demandes l'edt d'un {img_path}, prends ce roast chacal : \n\n"
                                                   + responses.roast_command(interaction.user.display_name, interaction.guild))
        embed = discord.Embed(title="Emploi du temps · " + type, 
                              color=discord.Color.blue(), 
                              url="https://www.emploisdutemps.uha.fr/")
        
        try:
            file = discord.File(img_path, filename="edt.png")
        except Exception as e:
            print(e)
            return await interaction.followup.send(content="An error occured. Please try again later.")
        
        embed.set_image(url="attachment://edt.png")
        embed.set_footer(text="critère: " + critere + " · le " 
                         + datetime.datetime.fromtimestamp(os.path.getmtime(img_path)).strftime("%d/%m/%Y à %H:%M:%S"))
        await interaction.followup.send(embed=embed, file=file)
    
    bot.tree.add_command(edt)
    
    @app_commands.command(name="heroswap", description="Swap faces with a random hero")
    @app_commands.choices(hero=[
        discord.app_commands.Choice(name=file, value=file) for file in os.listdir('img/face_swap')
    ])
    async def heroswap(interaction, face:discord.Attachment, hero:str="random"):
        await interaction.response.defer()
        try:
            result_path = await face_swap.swap_faces_hero(face, hero)
            if result_path == 'noface':
                return await interaction.followup.send(content="No face found in the image.")
            
            result = discord.File(result_path, filename="result.jpg")
            await interaction.followup.send(file=result)
        except Exception as e:
            await interaction.followup.send(content="An error occured. Please try again later.")
            print(e)
            
    bot.tree.add_command(heroswap)
    
    @bot.tree.command(description="Put the source face on the target face")
    async def faceswap(interaction, source:discord.Attachment, target:discord.Attachment):
        await interaction.response.defer()
        try:
            result_path = await face_swap.swap_faces(source, target)
            if result_path == 'noface_source':
                return await interaction.followup.send(content="No face found in the source image.")
            elif result_path == 'noface_target':
                return await interaction.followup.send(content="No face found in the target image.")
            
            result = discord.File(result_path, filename="result.jpg")
            await interaction.followup.send(file=result)
        except Exception as e:
            await interaction.followup.send(content="An error occured. Please try again later.")
            print(e)
    
    bot.tree.remove_command('help')
    @bot.tree.command(description="Shows the available commands")
    async def help(interaction):
        await interaction.response.send_message(embed=responses.help_command(interaction.guild))


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