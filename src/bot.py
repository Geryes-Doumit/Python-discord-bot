import datetime
import os
from bot_stuff import private_bot_data
import discord
from discord import app_commands
from discord.ext import commands
import responses
import json
import concurrent.futures, asyncio
import face_swap, edt_command, meme_command, poulpi_command
import heart_locket_command

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
        image_path, upvotes = meme_command.get_random_meme()
        message_content = f"`upvotes: {upvotes}`" if upvotes != "0" else ""
        
        if image_path == "error":
            return await interaction.followup.send(content="An error occured. Please try again later.")
        try:
            file = discord.File(image_path, filename=image_path)
            return await interaction.followup.send(content=message_content, file=file)
        except Exception as e:
            print(e)
            return await interaction.followup.send(content="An error occured. Please try again later.")
        
    @bot.tree.command(description="Sends a random picture of a monkey")
    async def monkey(interaction, width:int=None, height:int=None):
        await interaction.response.defer()
        image_path = meme_command.get_random_monkey(width, height)
        
        if image_path == "error":
            return await interaction.followup.send(content="An error occured. Please try again later.")
        try:
            file = discord.File(image_path, filename=image_path)
            return await interaction.followup.send(file=file)
        except Exception as e:
            print(e)
            return await interaction.followup.send(content="An error occured. Please try again later.")
        

    @bot.hybrid_group(fallback="user", description="Roast someone (a random roast will be chosen from the database)")
    @app_commands.describe(name="The name of the person to roast (can be a mention)",
                           server_specific="Whether to only include the server-specific roasts or also include the global ones")
    async def roast(ctx:commands.Context, name:str, server_specific:bool=False):
        if (name.__len__() > 100):
            await ctx.interaction.response.send_message(content="You've exceeded the 100-character limit.", ephemeral=True)
            return
        
        content = responses.roast_command(name, ctx.interaction.guild, server_specific)
        
        await ctx.interaction.response.send_message(content=content)
        
    @roast.command(description="Add a roast to the database")
    @app_commands.describe(roast="The roast to add (must contain '@n', it is where the name will be inserted)")
    async def add(ctx:commands.Context, roast:str):
        if (len(roast) > 300):
            await ctx.interaction.response.send_message(content="A roast cannot be more than 300 characters long.", ephemeral=True)
            return
        result = responses.addroast_command(roast, ctx.interaction.guild)
        content = result[0]
        ephemeral = result[1]
        await ctx.interaction.response.send_message(content=content, ephemeral=ephemeral)
        
    @roast.command(description="List the roasts in the database")
    @app_commands.describe(server_specific="Whether to only include the server-specific roasts or also include the global ones")
    async def list(ctx:commands.Context, server_specific:bool=False):
        messages:list[str] = responses.listroasts_command(ctx.interaction.guild, server_specific)
        
        await ctx.interaction.response.send_message(content=messages[0], ephemeral=True)
        for message in messages[1:]:
            await ctx.interaction.followup.send(content=message, ephemeral=True)
            
    @roast.command(description="Delete a server specific roast from the database")
    @app_commands.describe(index="The index of the roast to delete. Use the '/roast list' command to get the indexes.")
    async def delete(ctx:commands.Context, index:int):
        if index <= 0:
            await ctx.interaction.response.send_message(content="The index must be superior to 0.", ephemeral=True)
            return
        
        response, success = responses.findroast_command(index-1, ctx.interaction.guild)
        
        if not success:
            await ctx.interaction.response.send_message(content=response, ephemeral=True)
            return
        
        response = f"Are you sure you want to delete this roast? ```{response}```"
        yes_button = ConfirmDeleteRoastButton(index, ctx.interaction.guild)
        no_button = AbandonDeleteRoastButton()
        confirm_view = DisappearingView(timeout=120)
        confirm_view.add_item(yes_button)
        confirm_view.add_item(no_button)
        
        await ctx.interaction.response.send_message(content=response, view=confirm_view)
        confirm_view.message = await ctx.interaction.original_response()
    
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
            
    @bot.tree.command(description="Create a heart locket gif")
    @app_commands.describe(image="The image to put in the heart locket",
                           text="The text to put in the heart locket",
                           orientation="The orientation of the text (image-text or text-image)",
                           second_image="The second image to put in the heart locket (only for image-image orientation)"
    )
    @app_commands.choices(orientation=[
        discord.app_commands.Choice(name="image-text", value="image-text"),
        discord.app_commands.Choice(name="text-image", value="text-image"),
        discord.app_commands.Choice(name="image-image", value="image-image")
    ])
    async def heart_locket(interaction:discord.Interaction, image:discord.Attachment, orientation:str,
                           text:str="My beloved", second_image:discord.Attachment=None):
        await interaction.response.defer()
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Run in a separate thread
                future = executor.submit(asyncio.run, heart_locket_command.make_heart_locket(image, text, second_image, orientation))
                gif_path = await bot.loop.run_in_executor(None, future.result)
                
            if gif_path == "error":
                return await interaction.followup.send(content="An error occured. Please try again later.")
            elif gif_path=="image2_none":
                return await interaction.followup.send(content="You need to provide a second image for the 'image-image' orientation.")
            
            file = discord.File(gif_path, filename="heart_locket.gif")
            await interaction.followup.send(file=file)
            os.remove(gif_path)
        except Exception as e:
            print(e)
            await interaction.followup.send(content="An error occured. Please try again later.")
    
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
    @app_commands.describe(critere="Le critère de recherche",
                           type="Le type de recherche (par défaut: semaine)",
                           date="Spécifer une date de format: 'jj/mm/aaaa' (par défaut: date actuelle)",
                           force="Force un nouveau screenshot même s'il y en a déjà créé il y a moins de 10 min (par défaut: False)")
    async def edt(interaction:discord.Interaction, critere:str="_default_", type:str="semaine", date:str=None, force:bool=False):
        if interaction.guild is None:
            allowed, default_critere = False, ""
        else:
            allowed, default_critere = edt_command.command_details_per_server(str(interaction.guild.id))
        
        if not allowed:
            await interaction.response.send_message(content="This command not available in this server.", ephemeral=True)
            return
        
        if (len(critere) > 20):
            await interaction.response.send_message(content="You've exceeded the 20-character limit.", ephemeral=True)
            return
        
        if date is not None:
            try:
                datetime.datetime.strptime(date, '%d/%m/%Y')
                    
            except ValueError:
                await interaction.response.send_message(content="Format de date invalide. Veuillez utiliser le format `jj/mm/aaaa`.", ephemeral=True)
                return
        
        await interaction.response.defer()
        
        if critere == "_default_":
            critere = default_critere
            
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Run take_screenshot in a separate thread
            future = executor.submit(edt_command.take_screenshot, critere, type, force, date)
            img_path = await bot.loop.run_in_executor(None, future.result)
        # img_path = edt_command.take_screenshot(critere, type, force, date)
        if img_path == "samedi" or img_path == "dimanche":
            roast:str = responses.roast_command(interaction.user.display_name, interaction.guild, False)
            return await interaction.followup.send(content=f"Tu demandes l'edt d'un {img_path}, prends ce roast chacal : \n\n"
                                                   + roast)
            
        if "dateTooFarError" in img_path:
            roast:str = responses.roast_command(interaction.user.display_name, interaction.guild, False)
            return await interaction.followup.send(content="C'est quoi cette date ?" +
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
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Run in a separate thread
                future = executor.submit(asyncio.run, face_swap.swap_faces_hero(face, hero))
                result_path = await bot.loop.run_in_executor(None, future.result)
            # result_path = await face_swap.swap_faces_hero(face, hero)
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
    @app_commands.describe(source="The source image (the face to put on the target face)",
                           target="The target image (the face that gets replaced. Can be a GIF)",
                           replace_all="Whether to replace all the faces in the target image (not for gif images)",
                           discard_unswapped="Whether to discard the unswapped faces in the target image (only for gif images)")
    async def faceswap(interaction:discord.Interaction, source:discord.Attachment, target:discord.Attachment, 
                       replace_all:bool=False, discard_unswapped:bool=False):
        await interaction.response.defer()
        
        frame_number = await face_swap.get_number_of_frames(target)
        
        if frame_number <= 0:
            return await interaction.followup.send(content="An error occured while reading the target file.")
        elif frame_number > 200:
            return await interaction.followup.send(content="The target gif cannot contain more than 200 frames.")
        elif frame_number > 1:
            minutes = ((frame_number*2) // 60) + 1
            minutes_str = "minute" if minutes == 1 else "minutes"
            await interaction.followup.send(content=f"Processing {frame_number} frames..." +
                                        f"\n-# This could take about {minutes} {minutes_str} to finish.")
        
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Run in a separate thread
                future = executor.submit(asyncio.run, face_swap.swap_faces(source, target, replace_all, discard_unswapped))
                result_path = await bot.loop.run_in_executor(None, future.result)
            # result_path = await face_swap.swap_faces(source, target, replace_all)
            if result_path == 'noface_source':
                return await interaction.followup.send(content="No face found in the source image.")
            elif result_path == 'noface_target':
                return await interaction.followup.send(content="No face found in the target image.")
            elif result_path == 'gif_source':
                return await interaction.followup.send(content="You cannot use a gif as a source image.")
            elif result_path == 'too_many_frames':
                return await interaction.followup.send(content="The target gif cannot contain more than 200 frames.")
            
            filename = result_path.split("/")[-1]
            result = discord.File(result_path, filename=filename)
            delete_button = DeleteFaceSwapButton(interaction)
            delete_view = DisappearingView(timeout=120)
            delete_view.add_item(delete_button)
            
            message:discord.Message = await interaction.followup.send(file=result, view=delete_view)
            delete_view.message = await interaction.followup.fetch_message(message.id)
        except Exception as e:
            await interaction.followup.send(content="An error occured. Please try again later.")
            print(e)


    # ------------------------------------------------------------------------------------
    # -------------------------------    Bot events    -----------------------------------
    # ------------------------------------------------------------------------------------
    
    @bot.event
    async def on_ready():
        update_server_list(bot)
        
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} commands")
        except Exception as e:
            print(e)
        
        print("Bot is ready 🔥🔥")
    
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        
        await send_message(message, message.content)
        await bot.process_commands(message)
    
    @bot.event
    async def on_interaction(interaction:discord.Interaction):
        command:discord.app_commands.Command = interaction.command
        if command is None:
            return
        # else: 
        command_name:str = command.name
        command_origin:str = ""
        if interaction.guild is not None:
            command_origin = f"the server {interaction.guild.name}"
        else:
            command_origin = f"their DMs"
            
        date_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        log_str = f"[{date_str}] Processing /{command_name}, called by {interaction.user.name} from {command_origin}..."
        
        print(log_str)
        
    @bot.event
    async def on_app_command_completion(interaction:discord.Interaction, command:discord.app_commands.Command):
        print(f"Command /{command.name} completed.")
        print()
        
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
        try:
            if self.message is not None:
                for child in self.children:
                    self.remove_item(child)
                await self.message.edit(view=self)
        except Exception as e:
            pass

class DeleteFaceSwapButton(discord.ui.Button):
    def __init__(self, interaction:discord.Interaction):
        super().__init__(style=discord.ButtonStyle.grey, label="Delete Message")
        self.interaction = interaction
        
    async def callback(self, interaction:discord.Interaction):
        if interaction.message is not None:
            await interaction.message.delete()
        
class ConfirmDeleteRoastButton(discord.ui.Button):
    def __init__(self, roastIndex:int, guild:discord.Guild):
        super().__init__(style=discord.ButtonStyle.danger, label="Yes")
        self.roastIndex = roastIndex
        self.guild = guild
        
    async def callback(self, interaction:discord.Interaction):
        if interaction.message is not None:
            content = responses.deleteroast_command(self.roastIndex-1, self.guild)
            
            await interaction.message.edit(content=content, view=None)

class AbandonDeleteRoastButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.grey, label="No")
        
    async def callback(self, interaction:discord.Interaction):
        if interaction.message is not None:
            await interaction.message.delete()