import asyncio
import os
import re
import sys
import tracemalloc
import discord
from discord import app_commands
from discord.ext import commands
import random
import requests
import json
import seaborn as sns
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
import pandas as pd
from timple.timedelta import strftimedelta
from matplotlib.colors import ListedColormap
from matplotlib.collections import LineCollection
from matplotlib import cm
import numpy as np
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator
import matplotlib.font_manager as fm
from time import time, ctime
from datetime import datetime
import datetime
from matplotlib import dates
mpl.use('Agg')

import gspread
#from dotenv import load_dotenv
#load_dotenv()
import members_spreadsheet

from env import str_TOKEN
#bot token
TOKEN = str_TOKEN
#keep bot alive
from keep_alive import keep_alive

#enable discord intents
intents = discord.Intents.all()
client = commands.AutoShardedBot(command_prefix=";", help_command = None, intents = intents)



#get the time
async def get_time():
  return ctime(time())

#bot activity and login message
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('VGS'))
    print('We have logged in as {0.user}'.format(client))
    print(str(await get_time()))
    try:
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
  
  member_help = "/help - shows command list\n\n/register_self - register yourself as a member\n\n/unregister_self - unregister yourself as a member\n\n/my_xp - check your xp\n\n/list_ids - list ids of all members in a comittee\n\n"
  
  admin_help = "/help - shows command list\n\n/register_member - register a member\n\n/unregister_member - unregister a member\n\n/register_self - register yourself as a member\n\n/unregister_self - unregister yourself as a member\n\n/my_xp - check your xp\n\n/commitee_report - see a report about commitee\n\n/list_ids - list ids of all members in a comittee\n\n"
  admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
  tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
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

    msg = ""

    member = members_spreadsheet.find_member_discord(interaction.user.id)
    if member is None:
        msg = f"Hi {interaction.user.mention}!\nYou are not registered yet, register yourself first."
    else:
        msg = members_spreadsheet.calc_xp_report(member['id'])

    try:
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
        
@client.tree.command(name="committee_report", description="See a report about committee")
@app_commands.describe(committee = "Enter a committee")
async def committee(interaction: discord.Interaction, committee: str):

    await interaction.response.defer()
    await asyncio.sleep(1)

    datetime = await get_time()
    datetime = datetime.replace(" ", "-")
    datetime = datetime.replace(":", ".")

    msg = ""
    
    if committee is None:
        msg = f"Hi {interaction.user.mention}!\nYou must select a committee from [CL] [MRKT] [FR] [HR] [MD]\nexample: /committee_report CL"

    report = members_spreadsheet.get_committee_report(committee)
    if report is None:
        msg = f"Hi {interaction.user.mention}!\n{committee} is not a valid committee"
    else:
        with open(r"D:\Code\vgs-test\reports\\" + str(datetime) + "_" + committee + ".txt", "w") as file:
            file.write(report)

    try:
        file=discord.File(r"D:\Code\vgs-test\reports\\" + str(datetime) + "_" + committee + ".txt", filename=str(datetime) + "_" + committee + ".txt")
        #embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(file=file)
    except Exception as exc:
        print(exc)

@client.tree.command(name="list_ids", description="list ids of all members in a comittee")
@app_commands.describe(committee = "Enter a committee")
async def list_ids(interaction: discord.Interaction, committee: str):

    await interaction.response.defer()
    await asyncio.sleep(1)

    msg = ""
    embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
    
    if (ids := members_spreadsheet.list_ids(committee)) is not None:
        embed.add_field(name=f"{committee} Members:\n", value=ids, inline=False)
    else:
        msg = f"Hi {interaction.user.mention}!\n{committee} is not a valid committee"
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))

    try:
        #embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
  
@client.tree.command(name="register_self", description="Register yourself as a member")
@app_commands.describe(member_id = "Enter your member id")
async def register_self(interaction: discord.Interaction, member_id: str):

    await interaction.response.defer()
    await asyncio.sleep(1)

    msg = ""
    
    exit_code = members_spreadsheet.register(
        member_id, interaction.user.id, False)
    if exit_code == 0:
        msg = f"Hi {interaction.user.mention}!\nYou are now registered with the ID {member_id}!"
    elif exit_code == 1:
        msg = f"Hi {interaction.user.mention}!\nYou are already registered , you'll have to unregister before registering again."
    elif exit_code == 2:
        msg = f"Hi {interaction.user.mention}!\nThis ID is already taken, if you believe it's yours please contact your supervisor."
    else:
        msg = f"Hi {interaction.user.mention}!\nThere is no record of this ID, list IDs to find your correct ID!"

    try:
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
   
@client.tree.command(name="unregister_self", description="Unregister yourself as a member")
async def unregister_self(interaction: discord.Interaction):

    await interaction.response.defer()
    await asyncio.sleep(1)

    msg = ""
    
    exit_code = members_spreadsheet.unregister(interaction.user.id)
    if exit_code == 0:
        msg = f"Hi {interaction.user.mention}!\nYou have been successfully unregistered!"
    else:
        msg = f"Hi {interaction.user.mention}!\nYou are not registered in the first place!"

    try:
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
   
@client.tree.command(name="register_member", description="Register a member")
@app_commands.describe(member_id = "Enter a member id", member_mention = "Mention a member")
async def register_member(interaction: discord.Interaction, member_id: str, member_mention: discord.Member):

    await interaction.response.defer()
    await asyncio.sleep(1)

    msg = ""
    
    try:
        member_user = member_mention
    except IndexError:
        msg = f"Hi {interaction.user.mention}!\nIncorrect usage of the command, use /help for more information!"
        return

    exit_code = members_spreadsheet.register(
        member_id, member_user.id, True)
    if exit_code == 0:
        msg = f"Hi {interaction.user.mention}!\nMember is now registered with the ID {member_id}!"
    elif exit_code == 1:
        msg = f"Hi {interaction.user.mention}!\nMember is already registered with this ID"
    else:
        msg = f"Hi {interaction.user.mention}!\nThere is no record of this ID, list IDs to find the correct ID!"

    try:
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
   
@client.tree.command(name="unregister_member", description="Unregister a member")
@app_commands.describe(member_mention = "Mention a member")
async def unregister_member(interaction: discord.Interaction, member_mention: discord.Member):

    await interaction.response.defer()
    await asyncio.sleep(1)

    msg = ""
    
    try:
        member_user = member_mention
    except IndexError:
        msg = f"Hi {interaction.user.mention}!\nIncorrect usage of the command, use /help for more information!"
        return

    exit_code = members_spreadsheet.unregister(member_user.id)
    if exit_code == 0:
        msg = f"Hi {interaction.user.mention}!\nMember has been successfully unregistered!"
    else:
        msg = f"Hi {interaction.user.mention}!\nMember isn't registered in the first place!"

    try:
        embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
        await interaction.followup.send(embed=embed)
    except Exception as exc:
        print(exc)
   


#keep the bot alive
keep_alive()
client.run(TOKEN)