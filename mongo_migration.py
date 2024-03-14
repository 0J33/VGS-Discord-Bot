from dotenv import load_dotenv
import os
from bson import json_util
import json
from pymongo import MongoClient

load_dotenv()

connection_string = os.getenv("connection_string")
    
client = MongoClient(connection_string)
db = client["vgs"]

# def import_logs_from_txt():    
#     collection = db["logs"]
    
#     f = open("logs.txt", "r")
#     logs = f.read()
#     line = 0
#     split_logs = logs.split("\n")
#     while line < len(split_logs):
#         user = split_logs[line]
#         command = split_logs[line + 1]
#         datetime = split_logs[line + 2]
        
#         collection.insert_one({'user': user, 'command': command, 'datetime': datetime})
#         if (line + 6) < len(split_logs):
#             line += 4
#     f.close()

def export_to_json():
    data = {}
    for collection in db.list_collection_names():
        data[collection] = list(db[collection].find({}))
        
    with open('vgs_db.json', 'w') as f:
        json.dump(data, f, default=json_util.default)
        
def import_from_json():
    with open('vgs_db.json', 'r') as f:
        data = json.load(f)
        for collection, docs in data.items():
            if len(docs) > 0:
                for doc in docs:
                    for key, value in doc.items():
                        if isinstance(value, dict) and "$oid" in value:
                            doc[key] = json_util.loads(json.dumps(value))
                    if not db[collection].find_one(doc):
                        db[collection].insert_one(doc)
    
