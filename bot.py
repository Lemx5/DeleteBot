import os
import asyncio
from threading import Thread
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait

# Environment variables for Pyrogram
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Pyrogram setup
bot = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Flask setup
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running"

async def is_user_admin(chat_id, user_id):
    # Check if a user is an admin or owner in a specific chat
    chat_member = await bot.get_chat_member(chat_id, user_id)
    return chat_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.CREATOR]

@bot.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply("Hello! I'm simple ClearChatBot. Use /clearchat in a group to delete all messages!")


@bot.on_message(filters.command("clearchat") & filters.group)
async def clear_chat(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    # Check if the user is an admin in the group
    if not await is_user_admin(chat_id, user_id):
        await message.reply("You must be an admin to use this command!")
        return

    m = await message.reply("Starting to delete messages...")

    # Delete messages using the direct delete method
    count = 0
    async for msg in app.iter_history(chat_id):
        try:
            await msg.delete()
            print(f"Deleted message {msg.message_id}")
            count += 1
            
            # Update the user for every 100 messages deleted
            if count % 100 == 0:
                await m.edit(f"Deleted {count} messages so far...")
        except FloodWait as e:
            print(f"Rate limit exceeded. Sleeping for {e.x} seconds.")
            await asyncio.sleep(e.x)

    await m.edit(f"Deleted a total of {count} messages from {message.chat.title}!")


def run():
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 8080)))

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    bot.run()