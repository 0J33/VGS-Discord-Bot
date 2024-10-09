import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select
import mongo

async def handle_select_add_task(interaction: discord.Interaction, discord_id, xp, justification, committee, attendance):
    
    selected_option = interaction.data['values']
    
    members = selected_option
        
    discord_ids = []
        
    for member in members:
        member = mongo.find_member(member.split(" - ")[1])["discord_id"]
        discord_ids.append(member)
    
    task = mongo.add_task(discord_id, xp, justification, discord_ids, attendance)
    if task:
        msg = f"Task {task} added successfully!"
    else: 
        msg = f"Task {task} does not exist."
        
    embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
    await interaction.response.edit_message(embed=embed, view=None)