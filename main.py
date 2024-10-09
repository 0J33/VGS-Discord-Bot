import asyncio
import os
from dotenv import load_dotenv
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select
from time import time, ctime
import pathlib
import mongo
import select_handle
from select_handle import *

load_dotenv()

#bot token
TOKEN = os.getenv("str_TOKEN")
#keep bot alive
from keep_alive import keep_alive

#enable discord intents
intents = discord.Intents.all()
#create bot client
client = commands.AutoShardedBot(command_prefix=";", help_command = None, intents = intents)

#get the time
async def get_time():
  return ctime(time())

#method that logs data from slash commands
async def log(interaction, message):
    #get the time
    datetime = await get_time()
    #log the command used
    mongo.log(str('{}'.format(interaction.user.name)), str(message), str(datetime))

#method that handles exception messages
async def excp(interaction, message, exc):
    #get the time
    datetime = await get_time()
    #log the command and exception
    mongo.excp(str('{}'.format(interaction.user.name)), str(message), str(exc), str(datetime))

#bot activity and login message
@client.event
async def on_ready():
    #change the bot status
    await client.change_presence(status=discord.Status.online, activity=discord.Game('/help • vgs.ojee.net'))
    #print login message
    print('We have logged in as {0.user}'.format(client))
    try:
      #sync the commands and print number of synced commands
      synced = await client.tree.sync()
      print(f"Synced {len(synced)} command(s)")
    except Exception as exc:
      print(str(exc))

#if message by bot do nothing
@client.event
async def on_message(message):
    
    #if the bot is the author do nothing
    if message.author == client.user:
        return

@client.tree.command(name="help", description="Shows command list")
async def help(interaction: discord.Interaction):
  
    await log(interaction, "/help")
    
    #help command list for members
    member_help = """**/help**\nshows command list\n
    **/register_self**\nregister yourself as a member\n
    **/unregister_self**\nunregister yourself as a member\n
    **/my_xp**\ncheck your xp\n
    **/list_ids**\nlist ids of all members in a comittee\n
    **/leaderboard**\ncheck the leaderboard for a committee\n
    **/leaderboard_all**\ncheck the leaderboard for all committees\n"""
    
    #help command list for admins
    admin_help = """**/help**\nshows command list\n
    **/register_member**\nregister a member\n
    **/unregister_member**\nunregister a member\n
    **/register_self**\nregister yourself as a member\n
    **/unregister_self**\nunregister yourself as a member\n
    **/my_xp**\ncheck your xp\n
    **/commitee_report**\nsee a report about commitee\n
    **/list_ids**\nlist ids of all members in a comittee\n
    **/leaderboard**\ncheck the leaderboard for a committee\n
    **/leaderboard_all**\ncheck the leaderboard for all committees\n
    **/all_tasks**\nview all tasks\n
    **/add_task**\nadd a new task\n
    **/remove_task**\nremove a task"""
    
    #set admin_role as "Upper Board" role
    admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
    #set board_role as "Board" role
    board_role = discord.utils.find(lambda r: r.name == 'Board', interaction.guild.roles)
    #set tech_role as technician role
    tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
    
    #check if user is admin/tech or regular member and set the correct help message
    if admin_role in interaction.user.roles or board_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
        help_string = admin_help
    else:
        help_string = member_help
    
    embed = discord.Embed(title="Commands:", description=help_string,colour=discord.Color.from_rgb(25, 25, 26))
    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(1)
    await interaction.followup.send(embed=embed)

@client.tree.command(name="my_xp", description="Check your xp")
async def my_xp(interaction: discord.Interaction):

    await interaction.response.defer()
    await asyncio.sleep(1)

    await log(interaction, "/my_xp")
    
    msg = ""

    try:
        #look for the member using discord id, if member not registered error, else calc xp report and send it 
        member = mongo.find_member_discord(interaction.user.id)
        if member is None:
            msg = f"Hi {interaction.user.mention}!\nYou are not registered yet, register yourself first."
        else:
            msg = mongo.calc_xp_report(member['member_id'])
        
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/my_xp", exc)
        
@client.tree.command(name="committee_report", description="See a report about committee")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=0),
    discord.app_commands.Choice(name="IT", value=1),
    discord.app_commands.Choice(name="FE", value=2),
    discord.app_commands.Choice(name="HR", value=3),
    discord.app_commands.Choice(name="CL", value=4),
    discord.app_commands.Choice(name="MD", value=5),
    discord.app_commands.Choice(name="SM", value=6),
    discord.app_commands.Choice(name="GAD", value=7),
    discord.app_commands.Choice(name="GDD", value=8),
    discord.app_commands.Choice(name="GSD", value=9)
])
async def committee_report(interaction: discord.Interaction, committee: discord.app_commands.Choice[int]):

    await interaction.response.defer()
    await asyncio.sleep(1)
    
    committee = committee.name

    await log(interaction, "/commitee_report " + str(committee))
    
    #get the time and fix the format for file saving
    datetime = await get_time()
    datetime = datetime.replace(" ", "-")
    datetime = datetime.replace(":", ".")

    msg = ""
    
    try:
        #if commitee empty or invalid then error, else calc commitee report and send it
        if committee is None:
            msg = f"Hi {interaction.user.mention}!\nYou must select a committee from the listed committees"
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
        else: 
            report = await mongo.get_committee_report(committee, client)
            if report is None:
                msg = f"Hi {interaction.user.mention}!\n{committee} is not a valid committee"
                embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
                await interaction.followup.send(embed=embed)
            else:
                os.makedirs(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\", exist_ok=True)
                with open(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_" + committee + ".txt", "w") as file:
                    file.write(report)
                file=discord.File(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_" + committee + ".txt", filename=str(datetime) + "_" + committee + ".txt")
                #embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
                await interaction.followup.send(file=file)
                file.close()
                os.remove(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_" + committee + ".txt")
        
    except Exception as exc:
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        print(exc)
        await excp(interaction, "/commitee_report " + str(committee), exc)

@client.tree.command(name="list_ids", description="List ids of all members in a comittee")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=0),
    discord.app_commands.Choice(name="IT", value=1),
    discord.app_commands.Choice(name="FE", value=2),
    discord.app_commands.Choice(name="HR", value=3),
    discord.app_commands.Choice(name="CL", value=4),
    discord.app_commands.Choice(name="MD", value=5),
    discord.app_commands.Choice(name="SM", value=6),
    discord.app_commands.Choice(name="GAD", value=7),
    discord.app_commands.Choice(name="GDD", value=8),
    discord.app_commands.Choice(name="GSD", value=9)
])
async def list_ids(interaction: discord.Interaction, committee: discord.app_commands.Choice[int]):

    await interaction.response.defer()
    await asyncio.sleep(1)
    
    committee = committee.name
    
    await log(interaction, "/list_ids " + str(committee))

    msg = ""

    try:    
        #if commitee invalid then error, else send members id from commitee
        if (ids := await mongo.list_ids(committee, client)) is not None:
            embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
            embed.add_field(name=f"{committee} Members:\n", value=ids, inline=False)
            await interaction.followup.send(embed=embed)
        else:
            msg = f"Hi {interaction.user.mention}!\n{committee} is not a valid committee"
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/list_ids " + str(committee), exc)
  
@client.tree.command(name="register_self", description="Register yourself as a member")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=0),
    discord.app_commands.Choice(name="IT", value=1),
    discord.app_commands.Choice(name="FE", value=2),
    discord.app_commands.Choice(name="HR", value=3),
    discord.app_commands.Choice(name="CL", value=4),
    discord.app_commands.Choice(name="MD", value=5),
    discord.app_commands.Choice(name="SM", value=6),
    discord.app_commands.Choice(name="GAD", value=7),
    discord.app_commands.Choice(name="GDD", value=8),
    discord.app_commands.Choice(name="GSD", value=9)
])
async def register_self(interaction: discord.Interaction, committee: discord.app_commands.Choice[int]):

    await interaction.response.defer()
    await asyncio.sleep(1)
    
    committee = committee.name
    
    await log(interaction, "/register_self ")

    msg = ""
    
    try:
        
        #register member or send error message
        exit_code = mongo.register(interaction.user.id, committee)
        if exit_code == 0:
            msg = f"Hi {interaction.user.mention}!\nYou are now registered!"
        elif exit_code == 1:
            msg = f"Hi {interaction.user.mention}!\nYou are already registered , you'll have to unregister before registering again."

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        print(exc)
        await excp(interaction, "/register_self " + committee, exc)
   
@client.tree.command(name="unregister_self", description="Unregister yourself as a member")
async def unregister_self(interaction: discord.Interaction):

    await interaction.response.defer()
    await asyncio.sleep(1)
    
    await log(interaction, "/unregister_self")

    msg = ""
    
    try:
        
        #unregister member or send error message
        exit_code = mongo.unregister(interaction.user.id)
        if exit_code == 0:
            msg = f"Hi {interaction.user.mention}!\nYou have been successfully unregistered!"
        else:
            msg = f"Hi {interaction.user.mention}!\nYou are not registered in the first place!"

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/unregister_self", exc)
   
@client.tree.command(name="register_member", description="Register a member")
@app_commands.describe(committee = "Enter a committee", member_mention = "Mention a member")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=0),
    discord.app_commands.Choice(name="IT", value=1),
    discord.app_commands.Choice(name="FE", value=2),
    discord.app_commands.Choice(name="HR", value=3),
    discord.app_commands.Choice(name="CL", value=4),
    discord.app_commands.Choice(name="MD", value=5),
    discord.app_commands.Choice(name="SM", value=6),
    discord.app_commands.Choice(name="GAD", value=7),
    discord.app_commands.Choice(name="GDD", value=8),
    discord.app_commands.Choice(name="GSD", value=9)
])
async def register_member(interaction: discord.Interaction, committee: discord.app_commands.Choice[int], member_mention: discord.Member):

    await interaction.response.defer()
    await asyncio.sleep(1)
    
    committee = committee.name
    
    await log(interaction, "/register_member " + committee + " " + str(member_mention.id))

    msg = ""
    
    try:
    
        #set admin_role as "Upper Board" role
        admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
        #set board_role as "Board" role
        board_role = discord.utils.find(lambda r: r.name == 'Board', interaction.guild.roles)
        #set tech_role as "Technician" role
        tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
        #check if user is admin/tech or regular member and set the correct help message    
        if admin_role in interaction.user.roles or board_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
        
            try:
                #set member_user as the member object from the input member_mention
                member_user = member_mention
            except IndexError:
                msg = f"Hi {interaction.user.mention}!\nIncorrect usage of the command, use /help for more information!"
                return

            #register member or send error message
            exit_code = mongo.register(
                committee, member_user.id, True)
            if exit_code == 0:
                msg = f"Hi {interaction.user.mention}!\nMember is now registered!"
            elif exit_code == 1:
                msg = f"Hi {interaction.user.mention}!\nMember is already registered"
                
        else:
            msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/register_member " + committee + " " + str(member_mention.id), exc)
   
@client.tree.command(name="unregister_member", description="Unregister a member")
@app_commands.describe(member_mention = "Mention a member")
async def unregister_member(interaction: discord.Interaction, member_mention: discord.Member):

    await interaction.response.defer()
    await asyncio.sleep(1)

    await log(interaction, "/unregister_member " + str(member_mention.id))

    msg = ""
    
    try:
        #set admin_role as "Upper Board" role
        admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
        #set board_role as "Board" role
        board_role = discord.utils.find(lambda r: r.name == 'Board', interaction.guild.roles)
        #set tech_role as technician role
        tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
        #check if user is admin/tech or regular member and set the correct help message    
        if admin_role in interaction.user.roles or board_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
            
            try:
                #set member_user as the member object from the input member_mention
                member_user = member_mention
            except IndexError:
                msg = f"Hi {interaction.user.mention}!\nIncorrect usage of the command, use /help for more information!"
                return

            #unregister member or send error message
            exit_code = mongo.unregister(member_user.id)
            if exit_code == 0:
                msg = f"Hi {interaction.user.mention}!\nMember has been successfully unregistered!"
            else:
                msg = f"Hi {interaction.user.mention}!\nMember isn't registered in the first place!"
                
        else:
            msg = f"Hi {interaction.user.mention}!\nYou don't have permission to use this command"

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/unregister_member " + str(member_mention.id), exc)

@client.tree.command(name="leaderboard", description="Check the leaderboard for a committee")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=0),
    discord.app_commands.Choice(name="IT", value=1),
    discord.app_commands.Choice(name="FE", value=2),
    discord.app_commands.Choice(name="HR", value=3),
    discord.app_commands.Choice(name="CL", value=4),
    discord.app_commands.Choice(name="MD", value=5),
    discord.app_commands.Choice(name="SM", value=6),
    discord.app_commands.Choice(name="GAD", value=7),
    discord.app_commands.Choice(name="GDD", value=8),
    discord.app_commands.Choice(name="GSD", value=9)
])
async def leaderboard(interaction: discord.Interaction, committee: discord.app_commands.Choice[int]):

    await interaction.response.defer()
    await asyncio.sleep(1)
    
    committee = committee.name

    await log(interaction, "/leaderboard")
    
    #get the time and fix the format for file saving
    datetime = await get_time()
    datetime = datetime.replace(" ", "-")
    datetime = datetime.replace(":", ".")
    
    msg = ""

    try:
        #look for the member using discord id, if member not registered error, else calc xp report and send it 
        member = mongo.find_member_discord(interaction.user.id)
        if member is None:
            msg = f"Hi {interaction.user.mention}!\nYou are not registered yet, register yourself first."
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
        else:
            img = await mongo.get_leaderboard(committee, datetime, client)
            file=discord.File(img, filename="image.png")
            embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
            embed.set_image(url="attachment://image.png")
            await interaction.followup.send(embed=embed, file=file)
            file.close()
            os.remove(img)

    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/leaderboard", exc)
        
@client.tree.command(name="leaderboard_all", description="Check the leaderboard for all committees")
async def leaderboard_all(interaction: discord.Interaction):

    await interaction.response.defer()
    await asyncio.sleep(1)

    await log(interaction, "/leaderboard_all")
    
    #get the time and fix the format for file saving
    datetime = await get_time()
    datetime = datetime.replace(" ", "-")
    datetime = datetime.replace(":", ".")
    
    msg = ""

    try:
        #look for the member using discord id, if member not registered error, else calc xp report and send it 
        member = mongo.find_member_discord(interaction.user.id)
        if member is None:
            msg = f"Hi {interaction.user.mention}!\nYou are not registered yet, register yourself first."
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
        else:
            img = await mongo.get_leaderboard_all(datetime, client)
            file=discord.File(img, filename="image.png")
            embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
            embed.set_image(url="attachment://image.png")
            await interaction.followup.send(embed=embed, file=file)
            file.close()
            os.remove(img)
            
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/leaderboard_all", exc)

@client.tree.command(name="all_tasks", description="View all tasks")
async def all_tasks(interaction: discord.Interaction):

    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(1)

    await log(interaction, "/all_tasks")
    
    #get the time and fix the format for file saving
    datetime = await get_time()
    datetime = datetime.replace(" ", "-")
    datetime = datetime.replace(":", ".")
    
    msg = ""

    try:
        #set admin_role as "Upper Board" role
        admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
        #set board_role as "Board" role
        board_role = discord.utils.find(lambda r: r.name == 'Board', interaction.guild.roles)
        #set tech_role as technician role
        tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
        #check if user is admin/tech or regular member and set the correct help message
        if admin_role in interaction.user.roles or board_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
            tasks = await mongo.get_all_tasks(client)
            if tasks:
                msg = tasks
                os.makedirs(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\tasks\\", exist_ok=True)
                with open(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\tasks\\" + str(datetime) + ".txt", "w") as file:
                    file.write(msg)
                file=discord.File(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\tasks\\" + str(datetime) + ".txt", filename=str(datetime) + ".txt")    
                await interaction.followup.send(file=file)
                file.close()
                os.remove(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\tasks\\" + str(datetime) + ".txt")
            else: 
                msg = f"There are no tasks."
                
                embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
                await interaction.followup.send(embed=embed)
        else:
            msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"
                
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
            
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/all_tasks", exc)

@client.tree.command(name="add_task", description="Add a task")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=0),
    discord.app_commands.Choice(name="IT", value=1),
    discord.app_commands.Choice(name="FE", value=2),
    discord.app_commands.Choice(name="HR", value=3),
    discord.app_commands.Choice(name="CL", value=4),
    discord.app_commands.Choice(name="MD", value=5),
    discord.app_commands.Choice(name="SM", value=6),
    discord.app_commands.Choice(name="GAD", value=7),
    discord.app_commands.Choice(name="GDD", value=8),
    discord.app_commands.Choice(name="GSD", value=9)
])
@app_commands.describe(attendance = "Is the xp for attendance?")
@app_commands.choices(attendance=[
    discord.app_commands.Choice(name="Yes", value=0),
    discord.app_commands.Choice(name="No", value=1)
])
async def add_task(interaction: discord.Interaction, xp: int, justification: str, committee: discord.app_commands.Choice[int], attendance: discord.app_commands.Choice[int]):
    
    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(1)

    try:
        committee = committee.name
    except:
        committee = None
        
    try:
        attendance = attendance.name
    except:
        attendance = "No"
        
    if attendance == "Yes":
        attendance = True
    elif attendance == "No":
        attendance = False

    await log(interaction, "/add_task")
    
    #get the time and fix the format for file saving
    datetime = await get_time()
    datetime = datetime.replace(" ", "-")
    datetime = datetime.replace(":", ".")
    
    msg = ""
    
    try:
        #set admin_role as "Upper Board" role
        admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
        #set board_role as "Board" role
        board_role = discord.utils.find(lambda r: r.name == 'Board', interaction.guild.roles)
        #set tech_role as technician role
        tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
        #check if user is admin/tech or regular member and set the correct help message
        if admin_role in interaction.user.roles or board_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
            
            # edit the message to show a view with one select menu that has the names and ids of all the members in that committee
            
            # get member_id of the user that used the command
            member_id = mongo.find_member_discord(interaction.user.id)["member_id"]
            
            committee_members = mongo.get_members_committee(committee)
            members = []
            for member in committee_members:
                members.append([await mongo.get_user_name(member["discord_id"], client), member["member_id"]])
                
            embed=None
            options = members
            
            text=f"Hi {interaction.user.mention}!\nPlease select the members that will be given the xp:\n"
            embed = discord.Embed(title="", description=text, colour=discord.Color.from_rgb(25, 25, 26))
            
            # create the select menu
            select = Select(
                custom_id="select",
                placeholder="Select members",
                min_values=1,
                max_values=len(options),
            )
            
            for option in options:
                option = f"{option[0]} - {option[1]}"
                select.append_option(discord.SelectOption(label=option, value=option))

            select.callback = lambda i: handle_select_add_task(i, member_id, xp, justification, committee, attendance)
            
            view = discord.ui.View(timeout=None)
            view.add_item(select)
        
            await interaction.followup.send(embed=embed, view=view)
    
        else:
            msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"
                
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)

    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg, colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/add_task", exc)

@client.tree.command(name="remove_task", description="Remove a task")
async def remove_task(interaction: discord.Interaction, task_id: str):

    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(1)

    await log(interaction, "/remove_task")
    
    #get the time and fix the format for file saving
    datetime = await get_time()
    datetime = datetime.replace(" ", "-")
    datetime = datetime.replace(":", ".")
    
    msg = ""

    try:
        #set admin_role as "Upper Board" role
        admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
        #set board_role as "Board" role
        board_role = discord.utils.find(lambda r: r.name == 'Board', interaction.guild.roles)
        #set tech_role as technician role
        tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
        #check if user is admin/tech or regular member and set the correct help message
        if admin_role in interaction.user.roles or board_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
            task = mongo.delete_task(int(task_id))
            if task:
                msg = f"Task {task_id} removed successfully!"
            else: 
                msg = f"Task {task_id} does not exist."
        else:
            msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"
                
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
            
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        await excp(interaction, "/remove_task", exc)



#keep the bot alive
keep_alive()
client.run(TOKEN)