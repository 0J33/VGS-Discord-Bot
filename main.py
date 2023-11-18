import asyncio
import os
#import re
#import sys
import discord
from discord import app_commands
from discord.ext import commands
from time import time, ctime
#from datetime import datetime
#import datetime
import pathlib

import gspread
#from dotenv import load_dotenv
#load_dotenv()
# import mongo
import mongo


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
  **/list_ids**\nlist ids of all members in a comittee"""
  #help command list for admins
  admin_help = """**/help**\nshows command list\n
  **/register_member**\nregister a member\n
  **/unregister_member**\nunregister a member\n
  **/register_self**\nregister yourself as a member\n
  **/unregister_self**\nunregister yourself as a member\n
  **/my_xp**\ncheck your xp\n
  **/commitee_report**\nsee a report about commitee\n
  **/list_ids**\nlist ids of all members in a comittee"""
  #set admin_role as "Upper Board" role
  admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
  #set tech_role as technician role
  tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
  
  #check if user is admin/tech or regular member and set the correct help message
  if admin_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
    help_string = admin_help
  else:
    help_string = member_help
  
  embed = discord.Embed(title="Commands:", description=help_string,colour=discord.Color.from_rgb(25, 25, 26))
  await interaction.response.defer()
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
    discord.app_commands.Choice(name="LIT", value=2),
    discord.app_commands.Choice(name="MRKT", value=3),
    discord.app_commands.Choice(name="FR", value=4),
    discord.app_commands.Choice(name="HR", value=5),
    discord.app_commands.Choice(name="MD", value=6),
    discord.app_commands.Choice(name="EP", value=7),
    discord.app_commands.Choice(name="GAD", value=8),
    discord.app_commands.Choice(name="GDD", value=9),
    discord.app_commands.Choice(name="GSD", value=10)
])
async def committee(interaction: discord.Interaction, committee: discord.app_commands.Choice[int]):

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
            msg = f"Hi {interaction.user.mention}!\nYou must select a committee from [BOARD] [LIT] [MRKT] [FR] [HR] [MD] [EP] [GAD] [GDD] [GSD]\nexample: /committee_report CL"
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

@client.tree.command(name="list_ids", description="list ids of all members in a comittee")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=1),
    discord.app_commands.Choice(name="LIT", value=2),
    discord.app_commands.Choice(name="MRKT", value=3),
    discord.app_commands.Choice(name="FR", value=4),
    discord.app_commands.Choice(name="HR", value=5),
    discord.app_commands.Choice(name="MD", value=6),
    discord.app_commands.Choice(name="EP", value=7),
    discord.app_commands.Choice(name="GAD", value=8),
    discord.app_commands.Choice(name="GDD", value=9),
    discord.app_commands.Choice(name="GSD", value=10)
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
        #set tech_role as technician role
        tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
        #check if user is admin/tech or regular member and set the correct help message    
        if admin_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
        
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
        #set tech_role as technician role
        tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
        #check if user is admin/tech or regular member and set the correct help message    
        if admin_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
            
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

@client.tree.command(name="leaderboard", description="Check the leaderboard")
@app_commands.describe(committee = "Enter a committee")
@app_commands.choices(committee=[
    discord.app_commands.Choice(name="BOARD", value=1),
    discord.app_commands.Choice(name="LIT", value=2),
    discord.app_commands.Choice(name="MRKT", value=3),
    discord.app_commands.Choice(name="FR", value=4),
    discord.app_commands.Choice(name="HR", value=5),
    discord.app_commands.Choice(name="MD", value=6),
    discord.app_commands.Choice(name="EP", value=7),
    discord.app_commands.Choice(name="GAD", value=8),
    discord.app_commands.Choice(name="GDD", value=9),
    discord.app_commands.Choice(name="GSD", value=10)
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
        
@client.tree.command(name="leaderboard_all", description="Check the leaderboard")
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



#keep the bot alive
keep_alive()
client.run(TOKEN)