import logging
import requests

from .utils import Utils

class Message:
    def __init__(self, token):
        self.token = token

        

    def send_message(self, channel_id, content):
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        payload = {
            "content": content,
        }
        response = Utils._post(url, payload, self.token)
        if response.status_code == 200:
            pass
        else:
            print(f"Failed to send message: {response.status_code} {response.text}")