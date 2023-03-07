import gspread
import os
#from dotenv import load_dotenv
#load_dotenv()
    
from tabulate import tabulate

#get env vars from env.py (.env not working)
try:
    from env import str_type
    from env import str_project_id
    from env import str_private_key_id
    from env import str_private_key
    from env import str_client_email
    from env import str_client_id
    from env import str_auth_uri
    from env import str_token_uri
    from env import str_auth_provider_x509_cert_url
    from env import str_client_x509_cert_url
except:
    str_type = os.getenv("TYPE")
    str_project_id = os.getenv("PROJECT_ID")
    str_private_key_id = os.getenv("PRIVATE_KEY_ID")
    str_private_key = os.getenv("PRIVATE_KEY")
    str_client_email = os.getenv("CLIENT_EMAIL")
    str_client_id = os.getenv("CLIENT_ID")
    str_auth_uri = os.getenv("AUTH_URI")
    str_token_uri = os.getenv("TOKEN_URI")
    str_auth_provider_x509_cert_url = os.getenv("AUTH_PROVIDER_X509_CERT_URL")
    str_client_x509_cert_url = os.getenv("CLIENT_X509_CERT_URL")

# import datetime
# from gspread_formatting import *


credentials = {
  "type": str_type,
  "project_id": str_project_id,
  "private_key_id": str_private_key_id,
  "private_key": str_private_key,
  "client_email": str_client_email,
  "client_id": str_client_id,
  "auth_uri": str_auth_uri,
  "token_uri": str_token_uri,
  "auth_provider_x509_cert_url": str_auth_provider_x509_cert_url,
  "client_x509_cert_url": str_client_x509_cert_url,
}


gc = gspread.service_account_from_dict(credentials)
sh_members = gc.open("MEMBERS 2022")
sh_xp = gc.open("VGS XP Form (NEW) (Responses)")


def find_member(member_id):
    for sheet in sh_members.worksheets():
        if (member_cell := sheet.find(str(member_id))) is not None:
            name = sheet.cell(member_cell.row, 2).value
            committee = sheet.title
            return {"name": name, "committee": committee, "id": member_id}
    return None


def find_member_discord(discord_id):
    for sheet in sh_members.worksheets():
        if (member_cell := sheet.find(str(discord_id))) is not None:
            member_id = sheet.cell(member_cell.row, 1).value
            name = sheet.cell(member_cell.row, 2).value
            committee = sheet.title
            return {"name": name, "committee": committee, "id": member_id}
    return None


def list_ids(committee_name):
    members_parsed = "```"
    try:
        members = sh_members.worksheet(committee_name).get_all_values()
        for member in members:
            members_parsed = members_parsed + member[0] + "\t" + member[1] + "\n"
        members_parsed += "```"
        return members_parsed
    except gspread.exceptions.WorksheetNotFound:
        return None


def register(member_id, discord_id, admin):

    member = find_member_discord(discord_id)
    if member is not None:
        # this person is already registered with an id
        return 1

    for sheet in sh_members.worksheets():
        member_cell = sheet.find(str(member_id))
        if member_cell is None:
            # member id does not exist in this sheet
            continue

        if sheet.cell(member_cell.row, member_cell.col + 2).value is not None:
            if admin:
                sheet.update_cell(member_cell.row, member_cell.col + 2, str(discord_id))
                return 0
            # id already registered by another person
            return 2
        else:
            # successful registration
            sheet.update_cell(member_cell.row, member_cell.col + 2, str(discord_id))
            return 0

    # member id does not exist at all
    return 3


def unregister(discord_id):
    for sheet in sh_members.worksheets():
        member_cell = sheet.find(str(discord_id))
        if member_cell is None:
            # discord id does not exist in this sheet
            continue
        # delete discord id from this member
        sheet.update_cell(member_cell.row, member_cell.col, "")
        return 0

        # member didn't register in the first place
    return 1


def calc_xp_report(member_id):
    return calc_xp_report_helper(member_id,
    sh_xp.worksheet("Form Responses 1").get_all_values()
    )


def calc_xp_report_helper(member_id, xp_ws):
    xp = 0
    total_xp = 0
    attendance = 0
    report = ""

    worksheet = xp_ws
    for response in worksheet:
        response = [s for s in response if s]
        if str(member_id) in response[4]:
            reason = response[5] # increase in xp
            if "Attendance" in reason:
                attendance += 1
            xp = int(reason[reason.find("[")+1:reason.find("XP]")])
            total_xp += xp
            justification = response[6] # justification
            report += f"{justification}: {xp}XP\n"

    report += f"--------\nAttended {attendance} sessions/meetings\n"
    report += f"Total XP is {total_xp}\n\n\n"
    return report


def get_committee_report(committee):
    report = f"=========== {committee} COMMITTEE REPORT ===========\n\n"
    try:
        committee_ws = sh_members.worksheet(committee).get_all_values()
        xp_ws = sh_xp.worksheet("Form Responses 1").get_all_values()
        for member in committee_ws:
            report += member[0] + "\t" + member[1] + "\n" # [ID, Name]
            report += calc_xp_report_helper(member[0], xp_ws)
        return report
    except gspread.exceptions.WorksheetNotFound:
        return None    

def calc_xp_report_helper_leaderboard(member_id, xp_ws):
    xp = 0
    total_xp = 0
    attendance = 0
    report = ""

    worksheet = xp_ws
    for response in worksheet:
        response = [s for s in response if s]
        if str(member_id) in response[4]:
            reason = response[5] # increase in xp
            if "Attendance" in reason:
                attendance += 1
            xp = int(reason[reason.find("[")+1:reason.find("XP]")])
            total_xp += xp
            justification = response[6] # justification
            report += f"{justification}: {xp}XP\n"

    report += f"--------\nAttended {attendance} sessions/meetings\n"
    report += f"Total XP is {total_xp}\n\n\n"
    return total_xp

def get_leaderboard(committee_name):
  # Get the first worksheet in the members spreadsheet
  sheet = sh_members.worksheet(committee_name)

  # Create an array of member objects with their ids, names, and xp values
  members = []
  for row in sheet.get_all_values():
    members.append({"id": row[0], "name": row[1], "xp": calc_xp_report_helper_leaderboard(row[0], sh_xp.worksheet("Form Responses 1").get_all_values())})

  # Sort the members array by ascending xp
  members.sort(key=lambda x: x["xp"])

  # Reverse the order of the members array to sort by descending xp
  members.reverse()

# Create a table with the members' data
  table = []
  for i, member in enumerate(members):
    table.append([i + 1, member["id"], member["name"], member["xp"]])

  # Return the table as a string
  return tabulate(table, headers=["Position", "ID", "Name", "XP"], tablefmt="grid")

# def get_leaderboard_all():
    
#     members = []
#     committees = ["BOARD","LIT","MRKT","FR","HR","MD","EP","GAD","GDD","GSD"]
    
#     for committee_name in committees: 
#         # Get the first worksheet in the members spreadsheet
#         sheet = sh_members.worksheet(committee_name)

#         # Create an array of member objects with their ids, names, and xp values

#         for row in sheet.get_all_values():
#             members.append({"id": row[0], "name": row[1], "xp": calc_xp_report_helper_leaderboard(row[0], sh_xp.worksheet("Form Responses 1").get_all_values())})

#     # Sort the members array by ascending xp
#     members.sort(key=lambda x: x["xp"])

#     # Reverse the order of the members array to sort by descending xp
#     members.reverse()

#     # Create a table with the members' data
#     table = []
#     for i, member in enumerate(members):
#         table.append([i + 1, member["id"], member["name"], member["xp"]])

#     # Return the table as a string
#     return tabulate(table, headers=["Position", "ID", "Name", "XP"], tablefmt="grid")

# print(get_leaderboard_all())