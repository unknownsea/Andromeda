from andromeda import Andromeda
from andromeda import Message
from andromeda import Utils
from andromeda import Buttons

import time
from dotenv import load_dotenv
import os
from colorama import Fore, Style

start_time = time.time()
load_dotenv()

bot = Andromeda(os.getenv("AUTH_TOKEN"), start_time=start_time)
message = Message(bot.token)

@bot.event
async def on_ready(payload):
    elapsed_time = round((time.time() - bot.start_time) * 1000)
    print(f"{Fore.RED}[{bot.username} ({bot.id})]{Style.RESET_ALL} Initialized in {elapsed_time}ms")

@bot.event
async def on_message_create(payload):
    content = payload["content"]
    print(f"Message received: {content}")
    
    prefix = "!"
    if content.startswith(prefix):
        parts = content[len(prefix):].split()
        command_name = parts[0]
        args = parts[1:]
        print(f"Command: {command_name}, Args: {args}")
        await bot._handle_message(command_name, payload, *args)

@bot.event
async def on_message_delete(payload):
    cached_message = bot.message_cache.pop(payload["id"], None)
    if cached_message:
        print(f'Message deleted: {cached_message}')
    else:
        print(f'Message deleted with ID: {payload["id"]}')

@bot.command
async def help(payload, *args):
    message.send_message(payload["channel_id"], f"```Help Command | {args}```")




bot.start(debug=True)