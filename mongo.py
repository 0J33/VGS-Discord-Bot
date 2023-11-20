import os
import pathlib
from pymongo import MongoClient
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageFont

try:
    from env import connection_string
except:
    connection_string = os.getenv("CONNECTION_STRING")
    
client = MongoClient(connection_string)
db = client["vgs"]

def find_member(member_id):
    collection = db["members"]
    member = collection.find_one({"member_id": member_id})
    return member

def find_member_discord(discord_id):
    collection = db["members"]
    member = collection.find_one({"discord_id": discord_id})
    return member

def list_ids(committee_name):
    collection = db["members"]
    members = collection.find({"committee": committee_name})
    members_parsed = "```"
    for member in members:
        members_parsed = members_parsed + member["member_id"] + "\t" + member["name"] + "\n"
    members_parsed += "```"
    return members_parsed

def register(member_id, discord_id, admin):
    member = find_member_discord(discord_id)
    if member is not None:
        # this person is already registered with an id
        return 1
    
    collection = db["members"]
    member = collection.find_one({"member_id": member_id})
    if member is None:
        # member id does not exist at all
        return 3
    
    if member["discord_id"] is not None:
        if admin:
            collection.update_one({"member_id": member_id}, {"$set": {"discord_id": discord_id}})
            return 0
        # id already registered by another person
        return 2
    
    # successful registration
    collection.update_one({"member_id": member_id}, {"$set": {"discord_id": discord_id}})
    return 0

def unregister(discord_id):
    member = find_member_discord(discord_id)
    if member is None:
        # this person is not registered
        return 1
    
    collection = db["members"]
    collection.update_one({"discord_id": discord_id}, {"$set": {"discord_id": None}})
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
        if "attendance" in task["justification"].lower():
            attendance += 1
        report += f"{task['justification']}: {task['xp']} XP" + "\n"
        
    report += f"--------\nAttended {attendance} sessions/meetings\n"
    report += f"Total XP is {xp}\n\n\n"
    return report
        
def get_committee_report(committee):
    report = f"=========== {committee} COMMITTEE REPORT ===========\n\n"
    collection = db["members"]
    members = collection.find({"committee": committee})

    for member in members:
        report += member["member_id"] + "\t" + member["name"] + "\n"
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

def get_leaderboard(committee_name, datetime):
    collection = db["members"]
    members = collection.find({"committee": committee_name})
    leaderboard = []
    for member in members:
        xp = calc_xp_report_leaderboard(member["member_id"])
        leaderboard.append([member["member_id"], member["name"], xp])
    
    leaderboard.sort(key=lambda x: x[2], reverse=True)

    for i, member in enumerate(leaderboard):
        leaderboard[i].insert(0, i+1)
        
    text = tabulate(leaderboard, headers=["Position", "ID", "Name", "XP"], tablefmt="fancy_grid")
    res = make_img(text, datetime)
    
    return res

def get_leaderboard_all(datetime):
    collection = db["members"]
    members = collection.find({})
    leaderboard = []
    for member in members:
        xp = calc_xp_report_leaderboard(member["member_id"])
        leaderboard.append([member["member_id"], member["name"], member["committee"], xp])
    
    leaderboard.sort(key=lambda x: x[2], reverse=True)

    for i, member in enumerate(leaderboard):
        leaderboard[i].insert(0, i+1)
    
    text = tabulate(leaderboard, headers=["Position", "ID", "Name", "Committee", "XP"], tablefmt="fancy_grid")
    res = make_img(text, datetime)
    
    return res

def add_member(member_id, name, committee):
    collection = db["members"]
    if find_member(member_id) is not None:
        return 1
    else:
        collection.insert_one({"member_id": member_id, "name": name, "committee": committee, "discord_id": None})
        return 0

def edit_member(member_id, name, committee):
    collection = db["members"]
    if find_member(member_id) is not None:
        collection.update_one({"member_id": member_id}, {"$set": {"name": name, "committee": committee}})
        return 1
    else:
        return 0

def delete_member(member_id):
    collection = db["members"]
    if find_member(member_id) is not None:
        collection.delete_one({"member_id": member_id})
        return 1
    else:
        return 0
    
def get_all_tasks():
    collection = db["xp"]
    tasks = collection.find({})
    msg = "=========== ALL TASKS ===========\n\n"
    for task in tasks:
        msg += f"Task ID: {task['id']}\n"
        msg += f"Member ID: {task['member_id']}\n"
        members = []
        for member_id in task["member_ids"]:
            member = find_member(member_id)
            members.append([member["name"], member["member_id"]])
        msg += f"Members: \n{tabulate(members, headers=['Name', 'ID'], tablefmt='grid')}\n"
        msg += f"Justification: {task['justification']}\n"
        msg += f"XP: {task['xp']}\n"
        msg += "----------------------------------\n\n"
    return msg
        
def add_task(member_id, xp, justification, member_ids):
    collection = db["xp"]
    try:
        docs = collection.find({})
        max_id = 0
        for doc in docs:
            if doc["id"] > max_id:
                max_id = doc["id"]
        id = max_id + 1
        collection.insert_one({"id": id, "member_id": member_id, "member_ids": member_ids, "xp": xp, "justification": justification})
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

def find_member_pw(discord_id):
    collection = db["members_pw"]
    member = collection.find_one({"discord_id": discord_id})
    return member

def register_pw(discord_id, name):
    collection = db["members_pw"]
    if collection.find_one({"discord_id": discord_id}) is not None:
        return 0
    else:
        collection.insert_one({"discord_id": discord_id, "name": name, "level": 1, "xp": 0})
        return 1
    
def unregister_pw(discord_id):
    collection = db["members_pw"]
    if collection.find_one({"discord_id": discord_id}) is not None:
        collection.delete_one({"discord_id": discord_id})
        return 1
    else:
        return 0
    
def get_leaderboard_pw(datetime):
    collection = db["members_pw"]
    members = collection.find({})
    leaderboard = []
    for member in members:
        level = member['level']
        xp = member['xp']
        to_next_level = 10 * (level ** 2) + (100 * level)
        while xp >= to_next_level:
            level += 1
            to_next_level = 10 * (level ** 2) + (100 * level) # 10 * (lvl ^ 2) + (100 * lvl)
            
        if level > member['level']:
            update_level_pw(member['discord_id'], level)    
            
        leaderboard.append([member["name"], member["level"], member["xp"]])
    
    leaderboard.sort(key=lambda x: x[2], reverse=True)

    for i, member in enumerate(leaderboard):
        leaderboard[i].insert(0, i+1)

    text = tabulate(leaderboard, headers=["Position", "Name", "Level", "XP"], tablefmt="fancy_grid")
    res = make_img(text, datetime)
    
    return res

def add_xp_pw(discord_id, xp):
    collection = db["members_pw"]
    member = collection.find_one({"discord_id": discord_id})
    if member is not None:
        collection.update_one({"discord_id": discord_id}, {"$set": {"xp": member["xp"] + xp}})
        return 0
    else:
        return 1
    
def update_level_pw(discord_id, level):
    collection = db["members_pw"]
    member = collection.find_one({"discord_id": discord_id})
    if member is not None:
        collection.update_one({"discord_id": discord_id}, {"$set": {"level": level}})
        return 0
    else:
        return 1
    
def get_members_pw():
    collection = db["members_pw"]
    members = collection.find({})
    return members

def find_member_discord_pw(discord_id):
    collection = db["members_pw"]
    member = collection.find_one({"discord_id": discord_id})
    return member



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
    except:
        font_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "fonts", "UBUNTUMONO-REGULAR.TTF")
        ubuntu_font = ImageFont.truetype(font_path, 60)
    consola_font = ImageFont.truetype("consola.ttf", 70)

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
            x += ubuntu_font.getsize(char)[0]
        y += line_height + line_spacing

    # Save the image
    img.save(r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\res\\" + datetime + ".png", "PNG")
    
    return r"" + str(pathlib.Path(__file__).parent.resolve()) + "\\res\\" + datetime + ".png"

