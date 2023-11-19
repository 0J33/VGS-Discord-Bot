import asyncio
import os
#import re
#import sys
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select
from time import time, ctime
#from datetime import datetime
#import datetime
import pathlib

# import gspread
#from dotenv import load_dotenv
#load_dotenv()
# import mongo
import mongo
import select_handle
from select_handle import *


#bot token
try:
    from env import str_TOKEN
    TOKEN = str_TOKEN
except:
    TOKEN = os.getenv("TOKEN")
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
    testf = open(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\logs.txt","a")
    testf.write('{}'.format(interaction.user.name) + "\n" + str(message) + "\n" + str(datetime) + "\n\n")
    testf.close()

#method that handles exception messages
async def excp(interaction, message, exc):
    #get the time
    datetime = await get_time()
    #log the command and exception
    excf = open(r"" + str(pathlib.Path(__file__).parent.resolve())+ "\\exc.txt","a")
    excf.write('{}'.format(interaction.user.name) + "\n" + str(message) + "\n" + str(exc) + "\n" + str(datetime) + "\n\n")
    excf.close()
    return

#bot activity and login message
@client.event
async def on_ready():
    #change the bot status
    await client.change_presence(status=discord.Status.online, activity=discord.Game('/help • vgsguc.ga'))
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
    **/leaderboard_all**\ncheck the leaderboard for all committees"""
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
    **/add_member**\nadd a new member\n
    **/edit_member**\nedit a member's details\n
    **/remove_member**\nremove a member
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
        exc(interaction, "/my_xp", exc)
        
@client.tree.command(name="committee_report", description="See a report about committee")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=1),
    discord.app_commands.Choice(name="CL", value=2),
    discord.app_commands.Choice(name="SM", value=3),
    discord.app_commands.Choice(name="FR", value=4),
    discord.app_commands.Choice(name="HR", value=5),
    discord.app_commands.Choice(name="MD", value=6),
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
            msg = f"Hi {interaction.user.mention}!\nYou must select a committee from [BOARD] [LIT] [SM] [FR] [HR] [MD] [EP] [GAD] [GDD] [GSD]\nexample: /committee_report CL"
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
        else: 
            report = mongo.get_committee_report(committee)
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
        exc(interaction, "/commitee_report " + str(committee), exc)

@client.tree.command(name="list_ids", description="List ids of all members in a comittee")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=1),
    discord.app_commands.Choice(name="CL", value=2),
    discord.app_commands.Choice(name="SM", value=3),
    discord.app_commands.Choice(name="FR", value=4),
    discord.app_commands.Choice(name="HR", value=5),
    discord.app_commands.Choice(name="MD", value=6),
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
        if (ids := mongo.list_ids(committee)) is not None:
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
        exc(interaction, "/list_ids " + str(committee), exc)
  
@client.tree.command(name="register_self", description="Register yourself as a member")
@app_commands.describe(member_id = "Enter your member id")
async def register_self(interaction: discord.Interaction, member_id: str):

    await interaction.response.defer()
    await asyncio.sleep(1)
    
    await log(interaction, "/register_self " + str(member_id))

    msg = ""
    
    try:
        
        #register member or send error message
        exit_code = mongo.register(
            member_id, interaction.user.id, False)
        if exit_code == 0:
            msg = f"Hi {interaction.user.mention}!\nYou are now registered with the ID {member_id}!"
        elif exit_code == 1:
            msg = f"Hi {interaction.user.mention}!\nYou are already registered , you'll have to unregister before registering again."
        elif exit_code == 2:
            msg = f"Hi {interaction.user.mention}!\nThis ID is already taken, if you believe it's yours please contact your supervisor."
        else:
            msg = f"Hi {interaction.user.mention}!\nThere is no record of this ID, list IDs to find your correct ID!"

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        print(exc)
        exc(interaction, "/register_self " + str(member_id), exc)
   
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
        exc(interaction, "/unregister_self", exc)
   
@client.tree.command(name="register_member", description="Register a member")
@app_commands.describe(member_id = "Enter a member id", member_mention = "Mention a member")
async def register_member(interaction: discord.Interaction, member_id: str, member_mention: discord.Member):

    await interaction.response.defer()
    await asyncio.sleep(1)
    
    await log(interaction, "/register_member " + str(member_id) + " " + str(member_mention.id))

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

            #register member or send error message
            exit_code = mongo.register(
                member_id, member_user.id, True)
            if exit_code == 0:
                msg = f"Hi {interaction.user.mention}!\nMember is now registered with the ID {member_id}!"
            elif exit_code == 1:
                msg = f"Hi {interaction.user.mention}!\nMember is already registered with this ID"
            else:
                msg = f"Hi {interaction.user.mention}!\nThere is no record of this ID, list IDs to find the correct ID!"
                
        else:
            msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        exc(interaction, "/register_member " + str(member_id) + " " + str(member_mention.id), exc)
   
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
        exc(interaction, "/unregister_member " + str(member_mention.id), exc)

@client.tree.command(name="leaderboard", description="Check the leaderboard for a committee")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=1),
    discord.app_commands.Choice(name="CL", value=2),
    discord.app_commands.Choice(name="SM", value=3),
    discord.app_commands.Choice(name="FR", value=4),
    discord.app_commands.Choice(name="HR", value=5),
    discord.app_commands.Choice(name="MD", value=6),
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
            msg = mongo.get_leaderboard(committee)
            embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
            # embed.add_field(name=f"{committee} Leaderboard:\n", value=msg, inline=False)
            # await interaction.followup.send(embed=embed)
            with open(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_" + committee + ".txt", "w") as file:
                file.write(msg)
            file=discord.File(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_" + committee + ".txt", filename=str(datetime) + "_" + committee + ".txt")
            #embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(file=file)
            file.close()
            os.remove(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_" + committee + ".txt")
            
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        exc(interaction, "/leaderboard", exc)
        
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
            msg = mongo.get_leaderboard_all()
            embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
            # embed.add_field(name=f"{committee} Leaderboard:\n", value=msg, inline=False)
            # await interaction.followup.send(embed=embed)
            os.makedirs(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\", exist_ok=True)
            with open(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_ALL" + ".txt", "w") as file:
                file.write(msg)
            file=discord.File(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_ALL" + ".txt", filename=str(datetime) + "_ALL" + ".txt")
            #embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(file=file)
            file.close()
            os.remove(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_ALL" + ".txt")
            
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        exc(interaction, "/leaderboard_all", exc)
        
@client.tree.command(name="add_member", description="Add a new member")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=1),
    discord.app_commands.Choice(name="CL", value=2),
    discord.app_commands.Choice(name="SM", value=3),
    discord.app_commands.Choice(name="FR", value=4),
    discord.app_commands.Choice(name="HR", value=5),
    discord.app_commands.Choice(name="MD", value=6),
    discord.app_commands.Choice(name="GAD", value=7),
    discord.app_commands.Choice(name="GDD", value=8),
    discord.app_commands.Choice(name="GSD", value=9)
])
async def add_member(interaction: discord.Interaction, member_id: str, name: str, committee: discord.app_commands.Choice[int]):
    
    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(1)

    committee = committee.name

    await log(interaction, "/add_member")
    
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
            member = mongo.add_member(member_id, name, committee)
            if member:
                msg = f"Member {member_id} already exists."
            else: 
                msg = f"Member {member_id} added successfully!"
        else:
            msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
                
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        exc(interaction, "/add_member", exc)
        
@client.tree.command(name="edit_member", description="Edit a member's details")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=1),
    discord.app_commands.Choice(name="CL", value=2),
    discord.app_commands.Choice(name="SM", value=3),
    discord.app_commands.Choice(name="FR", value=4),
    discord.app_commands.Choice(name="HR", value=5),
    discord.app_commands.Choice(name="MD", value=6),
    discord.app_commands.Choice(name="GAD", value=7),
    discord.app_commands.Choice(name="GDD", value=8),
    discord.app_commands.Choice(name="GSD", value=9)
])
async def edit_member(interaction: discord.Interaction, member_id: str, name: str = None, committee: discord.app_commands.Choice[int] = None):
    
    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(1)

    try:
        committee = committee.name
    except:
        committee = None

    await log(interaction, "/edit_member")
    
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
            member = mongo.edit_member(member_id, name, committee)
            if member:
                if name == None:
                    name = mongo.find_member(member_id)["name"]
                if committee == None:
                    committee = mongo.find_member(member_id)["committee"]
                    msg = f"Member {member_id} edited successfully!"
            else: 
                msg = f"Member {member_id} does not exist."
        else:
            msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"
        
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
            
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        exc(interaction, "/edit_member", exc)
        
@client.tree.command(name="remove_member", description="Remove a member")
async def remove_member(interaction: discord.Interaction, member_id: str):

    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(1)

    await log(interaction, "/remove_member")
    
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
            member = mongo.delete_member(member_id)
            if member:
                msg = f"Member {member_id} removed successfully!"
            else: 
                msg = f"Member {member_id} does not exist."
        else:
            msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"
                
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
            
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        exc(interaction, "/remove_member", exc)
        
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
            tasks = mongo.get_all_tasks()
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
        exc(interaction, "/all_tasks", exc)

@client.tree.command(name="add_task", description="Add a task")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=1),
    discord.app_commands.Choice(name="CL", value=2),
    discord.app_commands.Choice(name="SM", value=3),
    discord.app_commands.Choice(name="FR", value=4),
    discord.app_commands.Choice(name="HR", value=5),
    discord.app_commands.Choice(name="MD", value=6),
    discord.app_commands.Choice(name="GAD", value=7),
    discord.app_commands.Choice(name="GDD", value=8),
    discord.app_commands.Choice(name="GSD", value=9)
])
async def add_task(interaction: discord.Interaction, xp: int, justification: str, committee: discord.app_commands.Choice[int]):
    
    await interaction.response.defer(ephemeral=True)
    await asyncio.sleep(1)

    try:
        committee = committee.name
    except:
        committee = None

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
                members.append([member["name"], member["member_id"]])
                
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

            select.callback = lambda i: handle_select_add_task(i, member_id, xp, justification, committee)
            
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
        exc(interaction, "/add_task", exc)

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
        exc(interaction, "/remove_task", exc)

@client.tree.command(name="register_pw", description="Register as a PW member")
async def register_pw(interaction: discord.Interaction, name: str):
    
        await interaction.response.defer()
        await asyncio.sleep(1)
    
        await log(interaction, "/register_pw")
        
        msg = ""
        
        try:
            
            pw = mongo.register_pw(interaction.user.id, name)
            if pw:
                msg = f"Hi {interaction.user.mention}!\nYou are now registered as a PW member!"
            else:
                msg = f"Hi {interaction.user.mention}!\nYou are already registered as a PW member!"
    
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
                    
        except Exception as exc:
            print(exc)
            msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
            await interaction.followup.send(msg)
            exc(interaction, "/register_pw", exc)

@client.tree.command(name="unregister_pw", description="Unregister as a PW member")
async def unregister_pw(interaction: discord.Interaction):
        
    await interaction.response.defer()
    await asyncio.sleep(1)

    await log(interaction, "/unregister_pw")
    
    msg = ""
    
    try:
        
        pw = mongo.unregister_pw(interaction.user.id)
        if pw:
            msg = f"Hi {interaction.user.mention}!\nYou are now unregistered as a PW member!"
        else:
            msg = f"Hi {interaction.user.mention}!\nYou are not registered as a PW member!"

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
                
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        await interaction.followup.send(msg)
        exc(interaction, "/unregister_pw", exc)

@client.tree.command(name="my_xp_pw", description="Check your xp as a PW member")
async def my_xp_pw(interaction: discord.Interaction):
            
    await interaction.response.defer()
    await asyncio.sleep(1)

    await log(interaction, "/my_xp_pw")
    
    msg = ""
    
    try:
        
        member = mongo.find_member_pw(interaction.user.id)
        if member:
            level = member['level']
            xp = member['xp']
            to_next_level = 5 * (level ** 2) + (50 * level)
            while xp >= to_next_level:
                level += 1
                to_next_level = 5 * (level ** 2) + (50 * level) # 5 * (lvl ^ 2) + (50 * lvl)
                
            if level > member['level']:
                mongo.update_level_pw(interaction.user.id, level)    
                
                channel = client.get_channel(1165709063317880842)
                user = client.get_user(member['discord_id'])
                msg = f"Congratulations {user.mention}!\nYou have leveled up to level {level}!"
                # msg = f"Congratulations <@{member['discord_id']}>!\nYou have leveled up to level {level}!"
                embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
                await channel.send(embed=embed)
                
            msg = f"Hi {interaction.user.mention}!\nXP: {xp}/{to_next_level}\nLevel: {level}"
        else:
            msg = f"Hi {interaction.user.mention}!\nYou are not registered as a PW member!"

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
                
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        await interaction.followup.send(msg)
        exc(interaction, "/my_xp_pw", exc)

@client.tree.command(name="leaderboard_pw", description="Check the leaderboard for PW members")
async def leaderboard_pw(interaction: discord.Interaction):
    
    await interaction.response.defer()
    await asyncio.sleep(1)

    await log(interaction, "/leaderboard_pw")
    
    #get the time and fix the format for file saving
    datetime = await get_time()
    datetime = datetime.replace(" ", "-")
    datetime = datetime.replace(":", ".")
    
    msg = ""

    try:
        #look for the member using discord id, if member not registered error, else calc xp report and send it 
        member = mongo.find_member_discord(interaction.user.id)
        if member is None:
            msg = f"Hi {interaction.user.mention}!\nYou are not registered as a PW member, register yourself first."
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
        else:
            msg = mongo.get_leaderboard_pw()
            
            members = mongo.get_members_pw()
            
            for member in members:
                level = member['level']
                xp = member['xp']
                to_next_level = 5 * (level ** 2) + (50 * level)
                while xp >= to_next_level:
                    level += 1
                    to_next_level = 5 * (level ** 2) + (50 * level) # 5 * (lvl ^ 2) + (50 * lvl)
                    
                if level > member['level']:
                    mongo.update_level_pw(member['discord_id'], level)    
            
                    channel = client.get_channel(1165709063317880842)
                    user = client.get_user(member['discord_id'])
                    msg = f"Congratulations {user.mention}!\nYou have leveled up to level {level}!"
                    # msg = f"Congratulations <@{member['discord_id']}>!\nYou have leveled up to level {level}!"
                    embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
                    await channel.send(embed=embed)
            
            embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
            # embed.add_field(name=f"{committee} Leaderboard:\n", value=msg, inline=False)
            # await interaction.followup.send(embed=embed)
            os.makedirs(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\", exist_ok=True)
            with open(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_PW" + ".txt", "w") as file:
                file.write(msg)
            file=discord.File(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_PW" + ".txt", filename=str(datetime) + "_PW" + ".txt")
            #embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(file=file)
            file.close()
            os.remove(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\reports\\" + str(datetime) + "_PW" + ".txt")
            
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg, colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        exc(interaction ,"/leaderboard_pw", exc)

@client.tree.command(name="add_xp_pw", description="Add XP to a PW member")
async def add_xp_pw(interaction: discord.Interaction, xp: int, member_mention: discord.Member):
    
    await interaction.response.defer()
    await asyncio.sleep(1)
    
    await log(interaction, "/add_pw_xp")
    
    msg = ""
    
    try:
        #check if user is admin/tech or regular member and set the correct help message    
        if interaction.user.id == 611941090429239306 or interaction.user.id == 529356422484590633:
        
            try:
                #set member_user as the member object from the input member_mention
                member_user = member_mention
            except IndexError:
                msg = f"Hi {interaction.user.mention}!\nIncorrect usage of the command, use /help for more information!"
                return

            #register member or send error message
            exit_code = mongo.add_xp_pw(member_user.id, xp)
            if exit_code == 0:
                
                members = mongo.get_members_pw()
                
                for member in members:
                    level = member['level']
                    xp = member['xp']
                    to_next_level = 5 * (level ** 2) + (50 * level)
                    while xp >= to_next_level:
                        level += 1
                        to_next_level = 5 * (level ** 2) + (50 * level) # 5 * (lvl ^ 2) + (50 * lvl)
                        
                    if level > member['level']:
                        mongo.update_level_pw(member['discord_id'], level)
                        
                        channel = client.get_channel(1165709063317880842)
                        user = client.get_user(member['discord_id'])
                        msg = f"Congratulations {user.mention}!\nYou have leveled up to level {level}!"
                        # msg = f"Congratulations <@{member['discord_id']}>!\nYou have leveled up to level {level}!"
                        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
                        await channel.send(embed=embed)
                        
                msg = f"Hi {interaction.user.mention}!\nXP added successfully!"
                
            elif exit_code == 1:
                msg = f"Hi {interaction.user.mention}!\nMember is not registered as a PW member!"

        else:
            msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"

        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        
    except Exception as exc:
        print(exc)
        msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
        embed = discord.Embed(title="", description=msg, colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
        exc(interaction, "/add_pw_xp", exc)

@client.tree.command(name="add_bounty", description="Add a bounty")
@app_commands.describe(bounty_board = "Choose a bounty board")
@app_commands.choices(bounty_board=[
    discord.app_commands.Choice(name="General", value=1),
    discord.app_commands.Choice(name="Dev", value=2),
    discord.app_commands.Choice(name="IT", value=3),
    discord.app_commands.Choice(name="Art", value=4),
    discord.app_commands.Choice(name="Sound", value=5),
    discord.app_commands.Choice(name="Design", value=6)
])
async def add_bounty(interaction: discord.Interaction, bounty_name: str, xp_range: str, deadline: str, type: str, prerequesites: str, bounty_details: str, bounty_board: discord.app_commands.Choice[int]):
        
        await interaction.response.defer(ephemeral=True)
        await asyncio.sleep(1)
    
        bounty_board = bounty_board.name
    
        await log(interaction, "/add_bounty")
        
        msg = ""
        
        try:
            #check if user is admin/tech or regular member and set the correct help message    
            if interaction.user.id == 611941090429239306 or interaction.user.id == 529356422484590633:
                
                msg = f"# {bounty_name}\n\nXP: {xp_range}\nDeadline: {deadline}\nType: {type}\nPrerequisites: {prerequesites}\n\nDescription:\n{bounty_details}"

                if bounty_board == "General":
                    channel = client.get_channel(1165711160360841296)
                elif bounty_board == "Dev":
                    channel = client.get_channel(1165711160360841296)
                elif bounty_board == "IT":
                    channel = client.get_channel(1165711160360841296)
                elif bounty_board == "Art":
                    channel = client.get_channel(1165711160360841296)
                elif bounty_board == "Sound":
                    channel = client.get_channel(1165711160360841296)
                elif bounty_board == "Design":
                    channel = client.get_channel(1165711160360841296)
                
                embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
                await channel.send(embed=embed)
            
                msg = f"Hi {interaction.user.mention}!\nBounty added successfully!"

            else:
                msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"
            
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
        
        except Exception as exc:
            
            print(exc)
            msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
            embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
            await interaction.followup.send(embed=embed)
            exc(interaction, "/add_bounty", exc)



#keep the bot alive
keep_alive()
client.run(TOKEN)