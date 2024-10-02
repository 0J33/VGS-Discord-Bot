# @client.tree.command(name="register_pw", description="Register as a PW member")
# async def register_pw(interaction: discord.Interaction, name: str):
    
#         await interaction.response.defer()
#         await asyncio.sleep(1)
    
#         await log(interaction, "/register_pw")
        
#         msg = ""
        
#         try:
            
#             pw = mongo.register_pw(interaction.user.id, name)
#             if pw:
#                 msg = f"Hi {interaction.user.mention}!\nYou are now registered as a PW member!"
#             else:
#                 msg = f"Hi {interaction.user.mention}!\nYou are already registered as a PW member!"
    
#             embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#             await interaction.followup.send(embed=embed)
                    
#         except Exception as exc:
#             print(exc)
#             msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
#             await interaction.followup.send(msg)
#             await excp(interaction, "/register_pw", exc)

# @client.tree.command(name="unregister_pw", description="Unregister as a PW member")
# async def unregister_pw(interaction: discord.Interaction):
        
#     await interaction.response.defer()
#     await asyncio.sleep(1)

#     await log(interaction, "/unregister_pw")
    
#     msg = ""
    
#     try:
        
#         pw = mongo.unregister_pw(interaction.user.id)
#         if pw:
#             msg = f"Hi {interaction.user.mention}!\nYou are now unregistered as a PW member!"
#         else:
#             msg = f"Hi {interaction.user.mention}!\nYou are not registered as a PW member!"

#         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
                
#     except Exception as exc:
#         print(exc)
#         msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
#         await interaction.followup.send(msg)
#         await excp(interaction, "/unregister_pw", exc)

# @client.tree.command(name="my_xp_pw", description="Check your xp as a PW member")
# async def my_xp_pw(interaction: discord.Interaction):
            
#     await interaction.response.defer()
#     await asyncio.sleep(1)

#     await log(interaction, "/my_xp_pw")
    
#     msg = ""
    
#     try:
        
#         member = mongo.find_member_pw(interaction.user.id)
#         if member:
#             level = member['level']
#             xp = member['xp']
#             to_next_level = 10 * (level ** 2) + (100 * level)
#             while xp >= to_next_level:
#                 level += 1
#                 to_next_level = 10 * (level ** 2) + (100 * level) # 10 * (lvl ^ 2) + (100 * lvl)
                
#             if level > member['level']:
#                 mongo.update_level_pw(interaction.user.id, level)    
                
#                 channel = client.get_channel(1165709063317880842)
#                 user = client.get_user(member['discord_id'])
#                 msg = f"Congratulations {user.mention}!\nYou have leveled up to level {level}!"
#                 # msg = f"Congratulations <@{member['discord_id']}>!\nYou have leveled up to level {level}!"
#                 embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#                 await channel.send(embed=embed)
                
#             msg = f"Hi {interaction.user.mention}!\nXP: {xp}/{to_next_level}\nLevel: {level}"
#         else:
#             msg = f"Hi {interaction.user.mention}!\nYou are not registered as a PW member!"

#         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
                
#     except Exception as exc:
#         print(exc)
#         msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
#         await interaction.followup.send(msg)
#         await excp(interaction, "/my_xp_pw", exc)

# @client.tree.command(name="leaderboard_pw", description="Check the leaderboard for PW members")
# async def leaderboard_pw(interaction: discord.Interaction):
    
#     await interaction.response.defer()
#     await asyncio.sleep(1)

#     await log(interaction, "/leaderboard_pw")
    
#     #get the time and fix the format for file saving
#     datetime = await get_time()
#     datetime = datetime.replace(" ", "-")
#     datetime = datetime.replace(":", ".")
    
#     msg = ""

#     try:
#         #look for the member using discord id, if member not registered error, else calc xp report and send it 
#         member = mongo.find_member_discord_pw(interaction.user.id)
#         if member is None:
#             msg = f"Hi {interaction.user.mention}!\nYou are not registered as a PW member, register yourself first."
#             embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#             await interaction.followup.send(embed=embed)
#         else:            
#             members = mongo.get_members_pw()
            
#             for member in members:
#                 level = member['level']
#                 xp = member['xp']
#                 to_next_level = 10 * (level ** 2) + (100 * level)
#                 while xp >= to_next_level:
#                     level += 1
#                     to_next_level = 10 * (level ** 2) + (100 * level) # 10 * (lvl ^ 2) + (100 * lvl)
                    
#                 if level > member['level']:
#                     mongo.update_level_pw(member['discord_id'], level)    
            
#                     channel = client.get_channel(1165709063317880842)
#                     user = client.get_user(member['discord_id'])
#                     msg = f"Congratulations {user.mention}!\nYou have leveled up to level {level}!"
#                     # msg = f"Congratulations <@{member['discord_id']}>!\nYou have leveled up to level {level}!"
#                     embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#                     await channel.send(embed=embed)
            
#             img = mongo.get_leaderboard_pw(datetime)
#             file=discord.File(img, filename="image.png")
#             embed = discord.Embed(title="", description=" ",colour=discord.Color.from_rgb(25, 25, 26))
#             embed.set_image(url="attachment://image.png")
#             await interaction.followup.send(embed=embed, file=file)
#             file.close()
#             os.remove(img)
            
#     except Exception as exc:
#         print(exc)
#         msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
#         embed = discord.Embed(title="", description=msg, colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
#         await excp(interaction ,"/leaderboard_pw", exc)

# @client.tree.command(name="add_xp_pw", description="Add XP to a PW member")
# async def add_xp_pw(interaction: discord.Interaction, xp: int, member_mention: discord.Member):
    
#     await interaction.response.defer(ephemeral=True)
#     await asyncio.sleep(1)
    
#     await log(interaction, "/add_pw_xp")
    
#     msg = ""
    
#     try:
#         #check if user is admin/tech or regular member and set the correct help message    
#         if interaction.user.id == 611941090429239306 or interaction.user.id == 529356422484590633:
        
#             try:
#                 #set member_user as the member object from the input member_mention
#                 member_user = member_mention
#             except IndexError:
#                 msg = f"Hi {interaction.user.mention}!\nIncorrect usage of the command, use /help for more information!"
#                 return

#             #register member or send error message
#             exit_code = mongo.add_xp_pw(member_user.id, xp)
#             if exit_code == 0:
                
#                 members = mongo.get_members_pw()
                
#                 for member in members:
#                     level = member['level']
#                     xp = member['xp']
#                     to_next_level = 10 * (level ** 2) + (100 * level)
#                     while xp >= to_next_level:
#                         level += 1
#                         to_next_level = 10 * (level ** 2) + (100 * level) # 10 * (lvl ^ 2) + (100 * lvl)
                        
#                     if level > member['level']:
#                         mongo.update_level_pw(member['discord_id'], level)
                        
#                         channel = client.get_channel(1165709063317880842)
#                         user = client.get_user(member['discord_id'])
#                         msg = f"Congratulations {user.mention}!\nYou have leveled up to level {level}!"
#                         # msg = f"Congratulations <@{member['discord_id']}>!\nYou have leveled up to level {level}!"
#                         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#                         await channel.send(embed=embed)
                        
#                 msg = f"Hi {interaction.user.mention}!\nXP added successfully!"
                
#             elif exit_code == 1:
#                 msg = f"Hi {interaction.user.mention}!\nMember is not registered as a PW member!"

#         else:
#             msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"

#         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
        
#     except Exception as exc:
#         print(exc)
#         msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
#         embed = discord.Embed(title="", description=msg, colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
#         await excp(interaction, "/add_pw_xp", exc)

# @client.tree.command(name="add_bounty", description="Add a bounty")
# @app_commands.describe(bounty_board = "Choose a bounty board")
# @app_commands.choices(bounty_board=[
#     discord.app_commands.Choice(name="General", value=1),
#     discord.app_commands.Choice(name="Dev", value=2),
#     discord.app_commands.Choice(name="IT", value=3),
#     discord.app_commands.Choice(name="Art", value=4),
#     discord.app_commands.Choice(name="Sound", value=5),
#     discord.app_commands.Choice(name="Design", value=6)
# ])
# async def add_bounty(interaction: discord.Interaction, bounty_name: str, xp_range: str, deadline: str, type: str, prerequisites: str, bounty_details: str, bounty_board: discord.app_commands.Choice[int]):
        
#         await interaction.response.defer(ephemeral=True)
#         await asyncio.sleep(1)
    
#         bounty_board = bounty_board.name
    
#         await log(interaction, "/add_bounty")
        
#         msg = ""
        
#         try:
#             #check if user is admin/tech or regular member and set the correct help message    
#             if interaction.user.id == 611941090429239306 or interaction.user.id == 529356422484590633:
                
#                 msg = f"# {bounty_name}\nXP: {xp_range}\nDeadline: {deadline}\nType: {type}\nPrerequisites: {prerequisites}\n\nDescription:\n{bounty_details}"

#                 if bounty_board == "General":
#                     channel = client.get_channel(1165711160360841296)
#                 elif bounty_board == "Dev":
#                     channel = client.get_channel(1165715735000125441)
#                 elif bounty_board == "IT":
#                     channel = client.get_channel(1171570041888710727)
#                 elif bounty_board == "Art":
#                     channel = client.get_channel(1165718818509828288)
#                 elif bounty_board == "Sound":
#                     channel = client.get_channel(1165724693895073833)
#                 elif bounty_board == "Design":
#                     channel = client.get_channel(1171569571115827210)
                
#                 message = await channel.send(msg)
#                 await message.add_reaction("✅")
            
#                 msg = f"Hi {interaction.user.mention}!\nBounty added successfully!"
#                 embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))

#                 await interaction.followup.send(embed=embed)
            
#             else:
#                 msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"
#                 embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#                 await interaction.followup.send(embed=embed)
        
#         except Exception as exc:
            
#             print(exc)
#             msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
#             embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#             await interaction.followup.send(embed=embed)
#             await excp(interaction, "/add_bounty", exc)
            
############################################################################################################

# def find_member_pw(discord_id):
#     collection = db["members_pw"]
#     member = collection.find_one({"discord_id": discord_id})
#     if member["name"] is None:
#         return None
#     return member

# def register_pw(discord_id, name):
#     collection = db["members_pw"]
#     # if record exists with the discord_id and name is not None, then return 1
#     if collection.find_one({"discord_id": discord_id}) is not None:
#         if collection.find_one({"discord_id": discord_id})["name"] is not None:
#             return 0
#         else:
#             collection.update_one({"discord_id": discord_id}, {"$set": {"name": name}})
#             return 1
#     else:
#         collection.insert_one({"discord_id": discord_id, "name": name, "level": 1, "xp": 0})
#         return 1
    
# def unregister_pw(discord_id):
#     collection = db["members_pw"]
#     if collection.find_one({"discord_id": discord_id}) is not None:
#         collection.update_one({"discord_id": discord_id}, {"$set": {"name": None}})
#         return 1
#     else:
#         return 0
    
# def get_leaderboard_pw(datetime):
#     collection = db["members_pw"]
#     members = collection.find({})
#     leaderboard = []
#     for member in members:
#         if member["name"] is not None:
#             level = member['level']
#             xp = member['xp']
#             to_next_level = 10 * (level ** 2) + (100 * level)
#             while xp >= to_next_level:
#                 level += 1
#                 to_next_level = 10 * (level ** 2) + (100 * level) # 10 * (lvl ^ 2) + (100 * lvl)
                
#             if level > member['level']:
#                 update_level_pw(member['discord_id'], level)    
                
#             leaderboard.append([member["name"], member["level"], member["xp"]])
    
#     leaderboard.sort(key=lambda x: x[2], reverse=True)

#     for i, member in enumerate(leaderboard):
#         leaderboard[i].insert(0, i+1)

#     text = tabulate(leaderboard, headers=["Position", "Name", "Level", "XP"], tablefmt="fancy_grid")
#     res = make_img(text, datetime)
    
#     return res

# def add_xp_pw(discord_id, xp):
#     collection = db["members_pw"]
#     member = collection.find_one({"discord_id": discord_id})
#     if member is not None and member["name"] is not None:
#         collection.update_one({"discord_id": discord_id}, {"$set": {"xp": member["xp"] + xp}})
#         return 0
#     else:
#         return 1
    
# def update_level_pw(discord_id, level):
#     collection = db["members_pw"]
#     member = collection.find_one({"discord_id": discord_id})
#     if member is not None and member["name"] is not None:
#         collection.update_one({"discord_id": discord_id}, {"$set": {"level": level}})
#         return 0
#     else:
#         return 1
    
# def get_members_pw():
#     collection = db["members_pw"]
#     members = collection.find({})
#     for member in members:
#         if member["name"] is None:
#             members.remove(member)
#     return members

# def find_member_discord_pw(discord_id):
#     collection = db["members_pw"]
#     member = collection.find_one({"discord_id": discord_id})
#     if member["name"] is None:
#         return None
#     return member

# def add_task(member_id, xp, justification, member_ids):
#     collection = db["xp"]
#     try:
#         docs = collection.find({})
#         max_id = 0
#         for doc in docs:
#             if doc["id"] > max_id:
#                 max_id = doc["id"]
#         id = max_id + 1
#         collection.insert_one({"id": id, "member_id": member_id, "member_ids": member_ids, "xp": xp, "justification": justification})
#         return 1
#     except:
#         return 0

# def delete_task(task_id):
#     collection = db["xp"]
#     if collection.find_one({"id": task_id}) is not None:
#         collection.delete_one({"id": task_id})
#         return 1
#     else:
#         return 0
    
############################################################################################################

        
# @client.tree.command(name="add_member", description="Add a new member")
# @app_commands.describe(committee = "Enter a committee")
# @app_commands.choices(committee=[
#     discord.app_commands.Choice(name="BOARD", value=1),
#     discord.app_commands.Choice(name="CL", value=2),
#     discord.app_commands.Choice(name="SM", value=3),
#     discord.app_commands.Choice(name="FR", value=4),
#     discord.app_commands.Choice(name="EP", value=5),
#     discord.app_commands.Choice(name="MD", value=6),
#     discord.app_commands.Choice(name="GAD", value=7),
#     discord.app_commands.Choice(name="GDD", value=8),
#     discord.app_commands.Choice(name="GSD", value=9)
# ])
# async def add_member(interaction: discord.Interaction,committee: discord.app_commands.Choice[int], name: str, member_id: str = None):
    
#     await interaction.response.defer(ephemeral=True)
#     await asyncio.sleep(1)

#     committee = committee.name

#     await log(interaction, "/add_member")
    
#     #get the time and fix the format for file saving
#     datetime = await get_time()
#     datetime = datetime.replace(" ", "-")
#     datetime = datetime.replace(":", ".")
    
#     msg = ""
    
#     try:
        
#         #set admin_role as "Upper Board" role
#         admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
#         #set board_role as "Board" role
#         board_role = discord.utils.find(lambda r: r.name == 'Board', interaction.guild.roles)
#         #set tech_role as technician role
#         tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
#         #check if user is admin/tech or regular member and set the correct help message
#         if admin_role in interaction.user.roles or board_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
#             if member_id == None:
#                 member_id = mongo.get_new_member_id(committee)
#             member = mongo.add_member(member_id, name, committee)
#             if member:
#                 msg = f"Member {member_id} already exists."
#             else: 
#                 msg = f"Member {member_id} added successfully!"
#         else:
#             msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"

#         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
                
#     except Exception as exc:
#         print(exc)
#         msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
#         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
#         await excp(interaction, "/add_member", exc)
        
# @client.tree.command(name="edit_member", description="Edit a member's details")
# @app_commands.describe(committee = "Enter a committee")
# @app_commands.choices(committee=[
#     discord.app_commands.Choice(name="BOARD", value=1),
#     discord.app_commands.Choice(name="CL", value=2),
#     discord.app_commands.Choice(name="SM", value=3),
#     discord.app_commands.Choice(name="FR", value=4),
#     discord.app_commands.Choice(name="EP", value=5),
#     discord.app_commands.Choice(name="MD", value=6),
#     discord.app_commands.Choice(name="GAD", value=7),
#     discord.app_commands.Choice(name="GDD", value=8),
#     discord.app_commands.Choice(name="GSD", value=9)
# ])
# async def edit_member(interaction: discord.Interaction, member_id: str, name: str = None, committee: discord.app_commands.Choice[int] = None):
    
#     await interaction.response.defer(ephemeral=True)
#     await asyncio.sleep(1)

#     try:
#         committee = committee.name
#     except:
#         committee = None

#     await log(interaction, "/edit_member")
    
#     #get the time and fix the format for file saving
#     datetime = await get_time()
#     datetime = datetime.replace(" ", "-")
#     datetime = datetime.replace(":", ".")
    
#     msg = ""

#     try:
#         #set admin_role as "Upper Board" role
#         admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
#         #set board_role as "Board" role
#         board_role = discord.utils.find(lambda r: r.name == 'Board', interaction.guild.roles)
#         #set tech_role as technician role
#         tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
#         #check if user is admin/tech or regular member and set the correct help message
#         if admin_role in interaction.user.roles or board_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
#             member = mongo.edit_member(member_id, name, committee)
#             if member:
#                 if name == None:
#                     name = mongo.find_member(member_id)["name"]
#                 if committee == None:
#                     committee = mongo.find_member(member_id)["committee"]
#                     msg = f"Member {member_id} edited successfully!"
#             else: 
#                 msg = f"Member {member_id} does not exist."
#         else:
#             msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"
        
#         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
            
#     except Exception as exc:
#         print(exc)
#         msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
#         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
#         await excp(interaction, "/edit_member", exc)
        
# @client.tree.command(name="remove_member", description="Remove a member")
# async def remove_member(interaction: discord.Interaction, member_id: str):

#     await interaction.response.defer(ephemeral=True)
#     await asyncio.sleep(1)

#     await log(interaction, "/remove_member")
    
#     #get the time and fix the format for file saving
#     datetime = await get_time()
#     datetime = datetime.replace(" ", "-")
#     datetime = datetime.replace(":", ".")
    
#     msg = ""

#     try:
#         #set admin_role as "Upper Board" role
#         admin_role = discord.utils.find(lambda r: r.name == 'Upper Board', interaction.guild.roles)
#         #set board_role as "Board" role
#         board_role = discord.utils.find(lambda r: r.name == 'Board', interaction.guild.roles)
#         #set tech_role as technician role
#         tech_role = discord.utils.find(lambda r: r.name == 'Technician', interaction.guild.roles)
        
#         #check if user is admin/tech or regular member and set the correct help message
#         if admin_role in interaction.user.roles or board_role in interaction.user.roles or tech_role in interaction.user.roles or interaction.user.id == 611941090429239306:
#             member = mongo.delete_member(member_id)
#             if member:
#                 msg = f"Member {member_id} removed successfully!"
#             else: 
#                 msg = f"Member {member_id} does not exist."
#         else:
#             msg = f"Hi {interaction.user.mention}!\n You don't have permission to use this command"
                
#         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
            
#     except Exception as exc:
#         print(exc)
#         msg= f"Hi {interaction.user.mention}!\nAn error occured. Please try again."
#         embed = discord.Embed(title="", description=msg,colour=discord.Color.from_rgb(25, 25, 26))
#         await interaction.followup.send(embed=embed)
#         await excp(interaction, "/remove_member", exc)
        