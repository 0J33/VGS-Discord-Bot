import os
from pymongo import MongoClient
from tabulate import tabulate

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

def get_leaderboard(committee_name):
    collection = db["members"]
    members = collection.find({"committee": committee_name})
    leaderboard = []
    for member in members:
        xp = calc_xp_report_leaderboard(member["member_id"])
        leaderboard.append([member["member_id"], member["name"], xp])
    
    leaderboard.sort(key=lambda x: x[2], reverse=True)

    for i, member in enumerate(leaderboard):
        leaderboard[i].insert(0, i+1)
        
    return tabulate(leaderboard, headers=["Position", "ID", "Name", "XP"], tablefmt="grid")

def get_leaderboard_all():
    collection = db["members"]
    members = collection.find({})
    leaderboard = []
    for member in members:
        xp = calc_xp_report_leaderboard(member["member_id"])
        leaderboard.append([member["member_id"], member["name"], xp])
    
    leaderboard.sort(key=lambda x: x[2], reverse=True)

    for i, member in enumerate(leaderboard):
        leaderboard[i].insert(0, i+1)
    
    return tabulate(leaderboard, headers=["Position", "ID", "Name", "XP"], tablefmt="grid")

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