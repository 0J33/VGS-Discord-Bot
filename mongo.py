# import the required libraries
import os
from unidecode import unidecode
from dotenv import load_dotenv
import pathlib
from pymongo import MongoClient
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlopen

# load the environment variables
load_dotenv()

# get the connection string from the environment variables
connection_string = os.getenv("connection_string")

# connect to the MongoDB database
mongo_client = MongoClient(connection_string)
db = mongo_client["vgs"]

# function to log the user's command
def log(user, message, datetime):
    collection = db['logs']
    collection.insert_one({'user': user, 'command': message, 'datetime': datetime})

# function to log the user's exception 
def excp(user, message, exception, datetime):
    collection = db['excp']
    collection.insert_one({'user': user, 'command': message, 'exception': exception, 'datetime': datetime})

# function to find a member by their member ID
def find_member(member_id):
    collection = db["members"]
    member = collection.find_one({"member_id": member_id})
    return member

# function to find a member by their Discord ID
def find_member_discord(discord_id):
    collection = db["members"]
    member = collection.find_one({"discord_id": discord_id})
    return member

# function to list all the members in a committee
async def list_ids(committee_name, client):
    collection = db["members"]
    members = collection.find({"committee": committee_name})
    members_parsed = "```"
    for member in members:
        members_parsed = members_parsed + member["member_id"] + "\t" + await get_user_name(member["discord_id"], client) + "\n"
    members_parsed += "```"
    return members_parsed

# function to register a member
def register(discord_id, committee):
    collection = db["members"]
    member = collection.find_one({"discord_id": discord_id})
    
    if member is not None:
        # if member has unregistered attribute
        if "unregistered" not in member:
            # this person is already registered
            return 1
        else:
            if member["unregistered"] == True:
                # this person was registered before but unregistered
                member_id = get_new_member_id(committee)
                collection.update_one({"discord_id": discord_id}, {"$set": {"unregistered": False}, "$set": {"committee": committee}, "$set": {"member_id": member_id}})
                return 0
            else:
                # this person is already registered
                return 1

    member_id = get_new_member_id(committee)
    # successful registration
    collection.insert_one({"member_id": member_id, "committee": committee, "discord_id": discord_id})
    return 0

# function to unregister a member
def unregister(discord_id):
    member = find_member_discord(discord_id)
    if member is None:
        # this person is not registered
        return 1
    
    collection = db["members"]
    # add an attribute "unregistered" to the member
    collection.update_one({"discord_id": discord_id}, {"$set": {"unregistered": True}})
    return 0

# function to calculate the XP report of a member
def calc_xp_report(discord_id):
    collection = db["xp"]
    all_tasks = collection.find({})
    tasks = []
    for task in all_tasks:
        if discord_id in task["discord_ids"]:
            tasks.append(task)
    xp = 0
    attendance = 0
    report = ""
    for task in tasks:
        xp += task["xp"]
        if task["attendance"] == True:
            attendance += 1
        report += f"{task['justification']}: {task['xp']} XP" + "\n"
        
    report += f"--------\nAttended {attendance} sessions/meetings\n"
    report += f"Total XP is {xp}\n\n\n"
    return report

# function to get calculate the XP report of a committee
async def get_committee_report(committee, client):
    report = f"=========== {committee} COMMITTEE REPORT ===========\n\n"
    collection = db["members"]
    members = collection.find({"committee": committee})

    for member in members:
        report += member["member_id"] + " " + await get_user_name(member["discord_id"], client) + "\n"
        report += calc_xp_report(member["discord_id"])
    report = unidecode(report)
    return report

# function to calculate the XP of a member
def calc_xp_report_leaderboard(discord_id):
    xp = 0
    
    collection = db["xp"]
    all_tasks = collection.find({})
    tasks = []
    for task in all_tasks:
        if discord_id in task["discord_ids"]:
            tasks.append(task)
    
    for task in tasks:
        xp += task["xp"]
        
    return xp

# function to get the leaderboard of a committee
async def get_leaderboard(committee_name, datetime, client):
    collection = db["members"]
    members = collection.find({"committee": committee_name})
    leaderboard = []
    for member in members:
        xp = calc_xp_report_leaderboard(member["discord_id"])
        leaderboard.append([member["member_id"], await get_user_name(member["discord_id"], client), xp])
    
    leaderboard.sort(key=lambda x: x[2], reverse=True)

    for i, member in enumerate(leaderboard):
        leaderboard[i].insert(0, i+1)
        
    text = tabulate(leaderboard, headers=["Position", "ID", "Name", "XP"], tablefmt="fancy_grid")
    res = make_img(text, datetime)
    
    return res

# function to get the leaderboard of all committees
async def get_leaderboard_all(datetime, client):
    collection = db["members"]
    members = collection.find({})
    leaderboard = []
    for member in members:
        xp = calc_xp_report_leaderboard(member["discord_id"])
        leaderboard.append([member["member_id"], await get_user_name(member["discord_id"], client), member["committee"], xp])
    
    leaderboard.sort(key=lambda x: x[3], reverse=True)

    for i, member in enumerate(leaderboard):
        leaderboard[i].insert(0, i+1)
    
    text = tabulate(leaderboard, headers=["Position", "ID", "Name", "Committee", "XP"], tablefmt="fancy_grid")
    res = make_img(text, datetime)
    
    return res

# function to get the username of a member
async def get_user_name(discord_id, client):
    user = await client.fetch_user(discord_id)
    username = user.name
    nickname = user.global_name
    if nickname is not None:
        return nickname
    else:
        return username

# function to get a new member ID for a member
def get_new_member_id(member_committee):
    committees_list = {
        "BOARD": "1",
        "CL": "2",
        "SM": "3",
        "FR": "4",
        "FE": "5",
        "MD": "6",
        "HR": "7",
        "IT": "8",
        "GAD": "9",
        "GDD": "9",
        "GSD": "9"
    }
    collection = db["members"]
    members = collection.find({"committee": member_committee})
    ids = []
    for member in members:
        ids.append(int(member["member_id"]))
    if len(ids) == 0:
        return committees_list[member_committee] + "01"
    else:
        ids.sort()
        return str(int(ids[-1]) + 1)
        # return committees_list[member_committee] + str(ids[-1] + 1).zfill(2)
    
# function to get all the tasks
async def get_all_tasks(client):
    collection = db["xp"]
    tasks = collection.find({})
    msg = "=========== ALL TASKS ===========\n\n"
    for task in tasks:
        msg += f"Task ID: {task['id']}\n"
        user = await get_user_name(task["discord_id"], client)
        msg += f"User: {user}\n"
        members = []
        for discord_id in task["discord_ids"]:
            member = find_member_discord(int(discord_id))
            members.append([await get_user_name(member["discord_id"], client), member["member_id"]])
        msg += f"Members: \n{tabulate(members, headers=['Name', 'ID'], tablefmt='grid')}\n"
        msg += f"Justification: {task['justification']}\n"
        msg += f"XP: {task['xp']}\n"
        msg += f"Attendance: {task['attendance']}\n"
        msg += "----------------------------------\n\n"
    return msg
    
# function to add a task/xp to a member(s)
def add_task(discord_id, xp, justification, discord_ids, attendance):
    collection = db["xp"]
    try:
        docs = collection.find({})
        max_id = 0
        for doc in docs:
            if doc["id"] > max_id:
                max_id = doc["id"]
        id = max_id + 1
        collection.insert_one({"id": id, "discord_id": discord_id, "discord_ids": discord_ids, "xp": xp, "justification": justification, "attendance": attendance})
        return 1
    except:
        return 0

# function to delete a task
def delete_task(task_id):
    collection = db["xp"]
    if collection.find_one({"id": task_id}) is not None:
        collection.delete_one({"id": task_id})
        return 1
    else:
        return 0
    
# function to get the members of a committee
def get_members_committee(committee):
    collection = db["members"]
    members = collection.find({"committee": committee})
    return members

# function to create an image of the leaderboard
def make_img(text, datetime):
    # Create a new image with a white background
    line_height = 50
    line_spacing = 10
    lines = text.split('\n')
    height = (len(lines) * line_height) + ((len(lines) - 1) * line_spacing) + 25
    width = max([len(line) for line in lines]) * 30 + 25

    # Create a new image with a white background
    img = Image.new('RGB', (width, height), color=(25, 25, 26))
    # Create a new ImageDraw object
    draw = ImageDraw.Draw(img)

    # Define the fonts to use (change to fonts installed on your system)
    try:
        ubuntu_font = ImageFont.truetype(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\fonts\\" + "UBUNTUMONO-REGULAR.TTF", 60)
        consola_font = ImageFont.truetype(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\fonts\\" + "CONSOLA.TTF", 70)
    except:
        ubuntu_font = ImageFont.truetype(r"" + str(pathlib.Path(__file__).parent.resolve()) + "/fonts/" + "UBUNTUMONO-REGULAR.TTF", 60)
        consola_font = ImageFont.truetype(r"" + str(pathlib.Path(__file__).parent.resolve()) + "/fonts/" + "CONSOLA.TTF", 70)

    # Draw the text on the image
    y = 10
    for line in lines:
        x = 10
        for char in line:
            # Use the "consola" font for characters that are not supported by the "Ubunutu Regular" font
            if not ubuntu_font.getmask(char).getbbox():
                draw.text((x, y), char, fill=(255, 255, 255), font=consola_font)
            else:
                draw.text((x, y), char, fill=(255, 255, 255), font=ubuntu_font)
            try:
                x += ubuntu_font.getsize(char)[0]
            except:
                x += 30
        y += line_height + line_spacing

    # Save the image
    img.save(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\res\\" + datetime + ".png", "PNG")
    
    return r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\res\\" + datetime + ".png"

