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
buttons = Buttons(bot.token)

@bot.event
async def on_ready(data):
    elapsed_time = round((time.time() - bot.start_time) * 1000)
    print(f"{Fore.RED}[{bot.username} ({bot.id})]{Style.RESET_ALL} Initialized in {elapsed_time}ms")

@bot.event
async def on_message_create(message):
    whitelisted = [
        "enter-giveaway",
        "test"
    ]
    
    components = message["components"]
    custom_id = None
    if components:
        nested_components = components[0]["components"]
        if nested_components:
            custom_id = nested_components[0]["custom_id"]

    if custom_id and custom_id in whitelisted:
        print(f"{Fore.GREEN}{custom_id} found in whitelist!, Interacting...{Style.RESET_ALL}")
        
        guild_id = message["guild_id"]
        channel_id = message["channel_id"]
        message_id = message["id"]
        author_id = message['author']['id']
        
        if guild_id and channel_id and message_id:
            buttons._interact(guild_id, channel_id, message_id, author_id, str(custom_id))
        else:
            print(f"{Fore.RED}Missing guild_id, channel_id, or message_id. Cannot interact.{Style.RESET_ALL}")
    else:
        pass



bot.start(debug=True)