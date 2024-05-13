import datetime
import os
from bot_stuff import private_bot_data
import discord
from discord import app_commands
from discord.ext import commands
import responses
import json
import face_swap, edt_command, profedt_command, meme_command, poulpi_command

async def send_message(message:discord.Message, user_message:str):
    try:
        response = responses.respond(user_message, message.guild)
        if response == "parlebcp":
            await message.reply(file=discord.File("img/parlebcp.jpg"))
        elif response != None:
            await message.reply(response)
    
    except Exception as e:
        print(e)
        
def run_bot():
    TOKEN = private_bot_data.token
    
    intents = discord.Intents.all()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='/', intents=intents)

    # ------------------------------------------------------------------------------------
    # ------------------------------- Information commands -------------------------------
    # ------------------------------------------------------------------------------------
    
    @bot.tree.command(description="List all the available features")
    async def features(interaction):
        await interaction.response.send_message(embed=responses.features_command(interaction.guild))
        
    bot.tree.remove_command('help')
    @bot.tree.command(description="Shows the available commands")
    async def help(interaction):
        await interaction.response.send_message(embed=responses.help_command(interaction.guild))
    
    
    # ------------------------------------------------------------------------------------
    # ----------------------------- Functional commands ----------------------------------
    # ------------------------------------------------------------------------------------
    
    @app_commands.command(name="enable", description="enables a feature")
    @app_commands.choices(feature=[
        discord.app_commands.Choice(name="di", value="di"),
        discord.app_commands.Choice(name="cri", value="cri"),
        discord.app_commands.Choice(name="backflip", value="backflip"),
        discord.app_commands.Choice(name="insults", value="insults")
    ])
    async def enable(interaction:discord.Interaction, feature:str):
        await interaction.response.send_message(embed=responses.enable_command(interaction.guild, feature))
    
    @app_commands.command(name="disable",description="disables a feature")
    @app_commands.choices(feature=[
        discord.app_commands.Choice(name="di", value="di"),
        discord.app_commands.Choice(name="cri", value="cri"),
        discord.app_commands.Choice(name="backflip", value="backflip"),
        discord.app_commands.Choice(name="insults", value="insults")
    ])
    async def disable(interaction:discord.Interaction, feature:str):
        await interaction.response.send_message(embed=responses.disable_command(interaction.guild, feature))
    
    bot.tree.add_command(enable)
    bot.tree.add_command(disable)
    
    
    # ------------------------------------------------------------------------------------
    # -------------------------------     Fun commands     -------------------------------
    # ------------------------------------------------------------------------------------
    
    @app_commands.command(name="joke", description="Sends a joke in the specified language")
    @app_commands.choices(lang=[
        discord.app_commands.Choice(name="en", value="en"),
        discord.app_commands.Choice(name="fr", value="fr")
    ])
    async def joke(interaction:discord.Interaction, lang:str="en"):
        await interaction.response.send_message(content=await responses.joke_command(lang))
        
    bot.tree.add_command(joke)
    
    
    @bot.tree.command(description="Sends a joke in french")
    async def blague(interaction):
        await interaction.response.send_message(content=await responses.joke_command("fr"))
        
        
    @bot.tree.command(description="Sends a random meme")
    async def meme(interaction):
        await interaction.response.defer()
        image_path = meme_command.get_random_meme()
        
        if image_path == "error":
            return await interaction.followup.send(content="An error occured. Please try again later.")
        try:
            file = discord.File(image_path, filename=image_path)
            return await interaction.followup.send(file=file)
        except Exception as e:
            print(e)
            return await interaction.followup.send(content="An error occured. Please try again later.")
        
    @bot.tree.command(description="Sends a random picture of a monkey")
    async def monkey(interaction):
        await interaction.response.defer()
        image_path = meme_command.get_random_monkey()
        
        if image_path == "error":
            return await interaction.followup.send(content="An error occured. Please try again later.")
        try:
            file = discord.File(image_path, filename=image_path)
            return await interaction.followup.send(file=file)
        except Exception as e:
            print(e)
            return await interaction.followup.send(content="An error occured. Please try again later.")
        

    @bot.tree.command(description="Roast someone (a random roast will be chosen from the database)")
    @app_commands.describe(name="The name of the person to roast (can be a mention)",
                           server_specific="Whether to only include the server-specific roasts or also include the global ones")
    async def roast(interaction:discord.Interaction, name:str, server_specific:bool=False):
        if (name.__len__() > 100):
            await interaction.response.send_message(content="You've exceeded the 100-character limit.", ephemeral=True)
            return
        
        roast_result = responses.roast_command(name, interaction.guild, server_specific)
        content = roast_result[0]
        roast_index = roast_result[1]
        is_general = roast_result[2]

        # delete_roast_button = DeleteRoastButton(roast_index, interaction.guild, server_specific)
        view = DisappearingView(timeout=20)
        if not is_general:
            # view.add_item(delete_roast_button)
            pass
        
        await interaction.response.send_message(content=content, view=view)
        view.message = await interaction.original_response()
        
    @bot.tree.command(description="Add a roast to the database")
    @app_commands.describe(roast="The roast to add (must contain '@n', it is where the name will be inserted)")
    async def addroast(interaction:discord.Interaction, roast:str):
        if (roast.__len__() > 300):
            await interaction.response.send_message(content="A roast cannot be more than 300 characters long.", ephemeral=True)
            return
        result = responses.addroast_command(roast, interaction.guild)
        content = result[0]
        ephemeral = result[1]
        await interaction.response.send_message(content=content, ephemeral=ephemeral)
    
    @bot.tree.command(description="Get a poulpi picture :3")
    @app_commands.choices(state=[
        discord.app_commands.Choice(name="all", value="all"),
        discord.app_commands.Choice(name="happy", value="happy"),
        discord.app_commands.Choice(name="sad", value="sad")
    ])
    async def poulpi(interaction:discord.Interaction, state:str='all'):
        try:
            poulpi_path = poulpi_command.poulpi_picture(state)
        except Exception as e:
            print(e)
            return await interaction.response.send_message(content="An error occured. Please try again later.")
        if poulpi_path == "error":
            return await interaction.response.send_message(content="An error occured. Please try again later.")
        
        embed = discord.Embed(color=discord.Color.pink() if "sad" in poulpi_path else discord.Color.blue())
        
        try:
            file = discord.File(poulpi_path, filename='poulpi.jpg')
        except FileNotFoundError:
            return await interaction.response.send_message(content="An error occured. Please try again later.")
        
        embed.set_image(url="attachment://poulpi.jpg")
        await interaction.response.send_message(embed=embed, file=file)
        
        message = await interaction.original_response()
        reactions = poulpi_command.get_msg_reactions(poulpi_path)
        for reaction in reactions:
            await message.add_reaction(reaction)
    
    # ------------------------------------------------------------------------------------
    # -------------------------------    EDT command   -----------------------------------
    # ------------------------------------------------------------------------------------
    
    @app_commands.command(name="edt",description="EDT de la semaine")
    @app_commands.choices(type=[
        discord.app_commands.Choice(name="semaine", value="semaine"),
        discord.app_commands.Choice(name="semaine prochaine", value="semaine prochaine"),
        discord.app_commands.Choice(name="jour", value="jour"),
        discord.app_commands.Choice(name="demain", value="demain")
    ])
    @app_commands.describe(critere="Le critère de recherche (par défaut: 2ir)",
                           type="Le type de recherche (par défaut: semaine)",
                           date="Spécifer une date de format: 'jj/mm/aaaa' (par défaut: date actuelle)",
                           force="Force un nouveau screenshot même s'il y en a déjà créé il y a moins de 10 min (par défaut: False)")
    async def edt(interaction:discord.Interaction, critere:str="2ir", type:str="semaine", date:str=None, force:bool=False):
        if interaction.guild is None or \
            (interaction.guild.id != 1017392713819230338 and interaction.guild.id != 754671642327646209):
            await interaction.response.send_message(content="This command is only available in the Info & réseaux server.", ephemeral=True)
            return
        
        if (critere.__len__() > 20):
            await interaction.response.send_message(content="You've exceeded the 20-character limit.", ephemeral=True)
            return
        
        if date is not None:
            try:
                datetime.datetime.strptime(date, '%d/%m/%Y')
            except ValueError:
                await interaction.response.send_message(content="Format de date invalide. Veuillez utiliser le format `jj/mm/aaaa`.", ephemeral=True)
                return
        
        await interaction.response.defer()

        img_path = edt_command.take_screenshot(critere, type, force, date)
        if img_path == "samedi" or img_path == "dimanche":
            roast:str = responses.roast_command(interaction.user.display_name, interaction.guild, False)[0]
            return await interaction.followup.send(content=f"Tu demandes l'edt d'un {img_path}, prends ce roast chacal : \n\n"
                                                   + roast)
            
        if "dateTooFarError" in img_path:
            roast:str = responses.roast_command(interaction.user.display_name, interaction.guild, False)[0]
            return await interaction.followup.send(content="Tu veux l'edt dans plus d'1 an ?" +
                                                   " Prends ce roast chacal : \n\n" + roast)
            
        date_str = f" ({date})" if date is not None else ""
        embed = discord.Embed(title="Emploi du temps · " + type + date_str, 
                              color=discord.Color.blue(), 
                              url="https://www.emploisdutemps.uha.fr/")
        
        try:
            file = discord.File(img_path, filename="edt.png")
        except Exception as e:
            print(e)
            return await interaction.followup.send(content="Une erreur est survenue. Veuillez réessayer plus tard.")
        
        embed.set_image(url="attachment://edt.png")
        embed.set_footer(text="critère: " + critere + " · le " 
                         + datetime.datetime.fromtimestamp(os.path.getmtime(img_path)).strftime("%d/%m/%Y à %H:%M"))
        await interaction.followup.send(embed=embed, file=file)
    
    bot.tree.add_command(edt)
    
    @bot.tree.command(description="EDT d'un professeur")
    async def profedt(interaction:discord.Interaction, name:str, jours:int=7):
        if interaction.guild is None or \
            (interaction.guild.id != 1017392713819230338 and interaction.guild.id != 754671642327646209):
            await interaction.response.send_message(content="This command is only available in the Info & réseaux server.", ephemeral=True)
            return
        
        if (name.__len__() > 100):
            await interaction.response.send_message(content="You've exceeded the 100-character limit.", ephemeral=True)
            return
        
        if jours < 1 or jours > 100:
            await interaction.response.send_message(content="The number of days must be between 1 and 100.", ephemeral=True)
            return
        
        await interaction.response.defer()
        embed = profedt_command.profedt(name, jours)
        await interaction.followup.send(embed=embed)
    
    # ------------------------------------------------------------------------------------
    # -------------------------------    Face swap    ------------------------------------
    # ------------------------------------------------------------------------------------
    
    @app_commands.command(name="heroswap", description="Swaps the face of the image with the face of a hero")
    @app_commands.choices(hero=[
        discord.app_commands.Choice(name=file, value=file) for file in os.listdir('img/hero_swap')
    ])
    async def heroswap(interaction:discord.Interaction, face:discord.Attachment, hero:str="random"):
        await interaction.response.defer()
        try:
            result_path = await face_swap.swap_faces_hero(face, hero)
            if result_path == 'noface':
                return await interaction.followup.send(content="No face found in the image.")
            
            result = discord.File(result_path, filename="heroswap_result.jpg")
            delete_button = DeleteFaceSwapButton(interaction)
            delete_view = DisappearingView(timeout=120)
            delete_view.add_item(delete_button)
            
            await interaction.followup.send(file=result, view=delete_view)
            delete_view.message = await interaction.original_response()
        except Exception as e:
            await interaction.followup.send(content="An error occured. Please try again later.")
            print(e)
            
    bot.tree.add_command(heroswap)
    
    @bot.tree.command(description="Put the source face on the target face")
    async def faceswap(interaction:discord.Interaction, source:discord.Attachment, target:discord.Attachment, replace_all:bool=False):
        await interaction.response.defer()
        try:
            result_path = await face_swap.swap_faces(source, target, replace_all)
            if result_path == 'noface_source':
                return await interaction.followup.send(content="No face found in the source image.")
            elif result_path == 'noface_target':
                return await interaction.followup.send(content="No face found in the target image.")
            
            result = discord.File(result_path, filename="faceswap_result.jpg")
            delete_button = DeleteFaceSwapButton(interaction)
            delete_view = DisappearingView(timeout=120)
            delete_view.add_item(delete_button)
            
            await interaction.followup.send(file=result, view=delete_view)
            delete_view.message = await interaction.original_response()
        except Exception as e:
            await interaction.followup.send(content="An error occured. Please try again later.")
            print(e)


    # ------------------------------------------------------------------------------------
    # -------------------------------    Bot events    -----------------------------------
    # ------------------------------------------------------------------------------------
    
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
            server_list[str(guild.id)]["di"] = False
            server_list[str(guild.id)]["cri"] = False
            server_list[str(guild.id)]["backflip"] = True
            server_list[str(guild.id)]["insults"] = False
    
    with open(filename, "w") as f:
        json.dump(server_list, f, indent=4)
        

# ------------------------------------------------------------------------------------
# -------------------------------    UI classes    -----------------------------------
# ------------------------------------------------------------------------------------

class DisappearingView(discord.ui.View):
    def __init__(self, timeout:float=120):
        super().__init__(timeout=timeout)
        self.message:discord.Message|None = None # need to set this ourselves
        
    async def on_timeout(self):
        for child in self.children:
            self.remove_item(child)
        if self.message is not None:
            await self.message.edit(view=self)

class DeleteFaceSwapButton(discord.ui.Button):
    def __init__(self, interaction:discord.Interaction):
        super().__init__(style=discord.ButtonStyle.grey, label="Delete Message")
        self.interaction = interaction
        
    async def callback(self, interaction:discord.Interaction):
        if interaction.message is not None:
            await interaction.message.delete()
        
class DeleteRoastButton(discord.ui.Button):
    def __init__(self, roastIndex:int, guild:discord.Guild, server_specific:bool):
        super().__init__(style=discord.ButtonStyle.danger, label="Delete Roast")
        self.roastIndex = roastIndex
        self.guild = guild
        self.server_specific = server_specific
        
    async def callback(self, interaction:discord.Interaction):
        if interaction.message is not None:
            await interaction.message.edit(
                content=responses.deleteroast_button_function(self.roastIndex, self.guild, self.server_specific),
                view=None,
            )
        