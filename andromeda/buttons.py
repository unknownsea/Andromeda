# andromeda/buttons.py
import requests

from .utils import Utils

class Buttons:
    def __init__(self, token):
        self.token = token
    
    def _interact(self, guild_id, channel_id, message_id, author_id, custom_id):
        gen_digits = Utils._generate_digits(19)
        print(gen_digits)
        url = f"https://discord.com/api/v9/interactions"
        payload = {
            "type": 3,
            "nonce": gen_digits,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "message_flags": 0,
            "message_id": message_id,
            "application_id": author_id,
            "session_id": "0",
            "data": {
                "component_type": 2,
                "custom_id": custom_id
            }
        }
        Utils._post(url, payload, self.token)