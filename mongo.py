import os
from dotenv import load_dotenv
import pathlib
from pymongo import MongoClient
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageFont
from urllib.request import urlopen

load_dotenv()

connection_string = os.getenv("connection_string")
    
mongo_client = MongoClient(connection_string)
db = mongo_client["vgs"]

def log(user, message, datetime):
    collection = db['logs']
    collection.insert_one({'user': user, 'command': message, 'datetime': datetime})
    
def excp(user, message, exception, datetime):
    collection = db['excp']
    collection.insert_one({'user': user, 'command': message, 'exception': exception, 'datetime': datetime})

def find_member(member_id):
    collection = db["members"]
    member = collection.find_one({"member_id": member_id})
    return member

def find_member_discord(discord_id):
    collection = db["members"]
    member = collection.find_one({"discord_id": discord_id})
    return member

async def list_ids(committee_name, client):
    collection = db["members"]
    members = collection.find({"committee": committee_name})
    members_parsed = "```"
    for member in members:
        members_parsed = members_parsed + member["member_id"] + "\t" + await get_user_name(member["discord_id"], client) + "\n"
    members_parsed += "```"
    return members_parsed

def register(discord_id, committee):
    collection = db["members"]
    member = collection.find_one({"discord_id": discord_id})
    if member is not None:
        if member["unregistered"] == True:
            # this person was registered before but unregistered
            collection.update_one({"discord_id": discord_id}, {"$set": {"unregistered": False}})
            return 0
        else:
            # this person is already registered
            return 1

    member_id = get_new_member_id(committee)
    # successful registration
    collection.insert_one({"member_id": member_id, "committee": committee, "discord_id": discord_id})
    return 0

def unregister(discord_id):
    member = find_member_discord(discord_id)
    if member is None:
        # this person is not registered
        return 1
    
    collection = db["members"]
    # add an attribute "unregistered" to the member
    collection.update_one({"discord_id": discord_id}, {"$set": {"unregistered": True}})
    return 0

def calc_xp_report(member_id):
    collection = db["xp"]
    all_tasks = collection.find({})
    tasks = []
    for task in all_tasks:
        if member_id in task["member_ids"]:
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
        
async def get_committee_report(committee, client):
    report = f"=========== {committee} COMMITTEE REPORT ===========\n\n"
    collection = db["members"]
    members = collection.find({"committee": committee})

    for member in members:
        report += member["member_id"] + " " + await get_user_name(member["discord_id"], client) + "\n"
        report += calc_xp_report(member["member_id"])
    return report

def calc_xp_report_leaderboard(member_id):
    xp = 0
    
    collection = db["xp"]
    all_tasks = collection.find({})
    tasks = []
    for task in all_tasks:
        if member_id in task["member_ids"]:
            tasks.append(task)
    
    for task in tasks:
        xp += task["xp"]
        
    return xp

async def get_leaderboard(committee_name, datetime, client):
    collection = db["members"]
    members = collection.find({"committee": committee_name})
    leaderboard = []
    for member in members:
        xp = calc_xp_report_leaderboard(member["member_id"])
        leaderboard.append([member["member_id"], await get_user_name(member["discord_id"], client), xp])
    
    leaderboard.sort(key=lambda x: x[2], reverse=True)

    for i, member in enumerate(leaderboard):
        leaderboard[i].insert(0, i+1)
        
    text = tabulate(leaderboard, headers=["Position", "ID", "Name", "XP"], tablefmt="fancy_grid")
    res = make_img(text, datetime)
    
    return res

async def get_leaderboard_all(datetime, client):
    collection = db["members"]
    members = collection.find({})
    leaderboard = []
    for member in members:
        xp = calc_xp_report_leaderboard(member["member_id"])
        leaderboard.append([member["member_id"], await get_user_name(member["discord_id"], client), member["committee"], xp])
    
    leaderboard.sort(key=lambda x: x[3], reverse=True)

    for i, member in enumerate(leaderboard):
        leaderboard[i].insert(0, i+1)
    
    text = tabulate(leaderboard, headers=["Position", "ID", "Name", "Committee", "XP"], tablefmt="fancy_grid")
    res = make_img(text, datetime)
    
    return res

async def get_user_name(discord_id, client):
    user = await client.fetch_user(discord_id)
    username = user.name
    nickname = user.global_name
    if nickname is not None:
        return nickname
    else:
        return username
    

def get_new_member_id(member_committee):
    committees_list = {
        "BOARD": "1",
        "CL": "2",
        "SM": "3",
        "FR": "4",
        "EP": "5",
        "MD": "6",
        "GAD": "7",
        "GDD": "8",
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
    
async def get_all_tasks(client):
    collection = db["xp"]
    tasks = collection.find({})
    msg = "=========== ALL TASKS ===========\n\n"
    for task in tasks:
        msg += f"Task ID: {task['id']}\n"
        msg += f"Member ID: {task['member_id']}\n"
        members = []
        for member_id in task["member_ids"]:
            member = find_member(member_id)
            members.append([await get_user_name(member["discord_id"], client), member["member_id"]])
        msg += f"Members: \n{tabulate(members, headers=['Name', 'ID'], tablefmt='grid')}\n"
        msg += f"Justification: {task['justification']}\n"
        msg += f"XP: {task['xp']}\n"
        msg += f"Attendance: {task['attendance']}\n"
        msg += "----------------------------------\n\n"
    return msg
    
def add_task(member_id, xp, justification, member_ids, attendance):
    collection = db["xp"]
    try:
        docs = collection.find({})
        max_id = 0
        for doc in docs:
            if doc["id"] > max_id:
                max_id = doc["id"]
        id = max_id + 1
        collection.insert_one({"id": id, "member_id": member_id, "member_ids": member_ids, "xp": xp, "justification": justification, "attendance": attendance})
        return 1
    except:
        return 0

def delete_task(task_id):
    collection = db["xp"]
    if collection.find_one({"id": task_id}) is not None:
        collection.delete_one({"id": task_id})
        return 1
    else:
        return 0
    
def get_members_committee(committee):
    collection = db["members"]
    members = collection.find({"committee": committee})
    return members

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

