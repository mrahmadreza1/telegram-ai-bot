import json
import os

FILE="data/chat_history.json"

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(FILE):
    with open(FILE,"w") as f:
        json.dump({},f)

def load_history():
    with open (FILE) as f:
        return json.load(f)

def save_history(data):
    with open (FILE,"w")as f:
        json.dump(data,f,indent=4)

def add_message(user_id,role,text):
    data=load_history()

    uid=str(user_id)

    if uid not in data:
        data[uid]=[]

    data[uid].append(
        {
            "role":role,
            "content":text
        }
    )


    # faghat 20 payame akhar
    data[uid]=data[uid][-20:]

    save_history(data)

def get_history(user_id):
    data=load_history()
    return data.get(str(user_id),[])