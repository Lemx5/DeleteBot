import os
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
import asyncio
from threading import Thread
from flask import Flask


# Env vars
API_ID = os.getenv("API_ID") # Telegram API_ID , get it from my.telegram.org
API_HASH = os.getenv("API_HASH") # Telegram API_HASH , get it from my.telegram.org
STRING = os.getenv("STRING") # Pyrogram session string

# Bot
app = Client(
    "deletebot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING
)

# flask server
server = Flask(__name__)

# flask home route
@server.route("/")
def home():
    return "I'm alive"

# command to delete all messages
@app.on_message(filters.me & filters.command("clearchat", prefixes="."))
async def clearchat(_, message):
    chat_id = message.chat.id
    # get all messages
    async for msg in app.get_chat_history(chat_id):
        try:
            # delete message
            await app.delete_user_history(chat_id, msg.from_user.id)
        except FloodWait as e:
            # wait for a while
            print(e)
            await asyncio.sleep(e.x)
        except Exception as e:
            print(e)
            pass


def run():
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    app.run()