import json
import os

FILE_NAME = "chat_history.json"


def load_chats():

    if not os.path.exists(FILE_NAME):
        return {}

    with open(FILE_NAME, "r") as file:
        return json.load(file)


def save_chats(chats):

    with open(FILE_NAME, "w") as file:
        json.dump(chats, file, indent=4)