from andromeda import Andromeda
from dotenv import load_dotenv
import os

load_dotenv()

bot = Andromeda(os.getenv("AUTH_TOKEN"))

whitelisted = [
    "enter-giveaway",
    "test"
]

@bot.event
async def on_message(message):
    components = message.get("components", [])
    custom_id = None
    if components:
        nested_components = components[0].get("components", [])
        if nested_components:
            custom_id = nested_components[0].get("custom_id")

    if custom_id and custom_id in whitelisted:
        print(f"Custom ID '{custom_id}' is in the whitelist!")
        
        guild_id = message.get("guild_id")
        channel_id = message.get("channel_id")
        message_id = message.get("id")
        author_id = message.get('author', {}).get('id')
        
        if guild_id and channel_id and message_id:
            bot._interact(guild_id, channel_id, message_id, author_id, str(custom_id))
        else:
            print("Missing guild_id, channel_id, or message_id. Cannot interact.")
    else:
        pass

bot.start(debug=True)