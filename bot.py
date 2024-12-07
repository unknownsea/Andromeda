import websocket
import json
import threading
import time
import requests
import asyncio
import random

GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
intents = 53608447

class Andromeda:
    def __init__(self, token):
        self.token = token
        self.ws = None
        self.heartbeat_interval = None
        self.event_handlers = {}

    def event(self, coro):
        """Decorator to register an event handler."""
        self.event_handlers[coro.__name__] = coro
        return coro

    def start(self, debug=True):
        if debug:
            print("Starting WebSocket connection...")
            print(f"Gateway URL: {GATEWAY_URL}")

        self.ws = websocket.WebSocketApp(
            GATEWAY_URL,
            on_message=self._on_message_wrapper,
            on_close=self.on_close,
        )

        if debug:
            print("WebSocketApp initialized.")
            print("Starting WebSocket in a new thread...")

        threading.Thread(target=self.ws.run_forever).start()

        if debug:
            print("WebSocket thread started.")

    def identify(self):
        payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": intents,
                "properties": {
                    "os": "linux",
                    "browser": "selfbot",
                    "device": "selfbot",
                },
            },
        }
        self.ws.send(json.dumps(payload))

    def heartbeat(self):
        try:
            while self.ws:
                if self.heartbeat_interval:
                    self.ws.send(json.dumps({"op": 1, "d": None}))
                    time.sleep(self.heartbeat_interval / 1000)
        except websocket.WebSocketConnectionClosedException:
            print("WebSocket connection closed. Stopping heartbeat.")

    def _post(self, url, payload):
        """Helper method to send POST requests to Discord's API."""
        headers = {
            "Authorization": f"{self.token}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print(f"POST request failed: {response.status_code} {response.text}")
        return response
    
    def _get_api_ping(self):
        url = "https://discord.com/api/v10/users/@me"
        headers = {"Authorization": f"{self.token}"}

        start_time = time.time()
        response = requests.get(url, headers=headers)
        end_time = time.time()

        if response.status_code == 200:
            return round((end_time - start_time) * 1000)
        else:
            print(f"Failed to fetch API latency: {response.status_code} {response.text}")
            return None

    def _send_reply(self, channel_id, message_id, content):
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
        payload = {
            "content": content,
            "message_reference": {"message_id": message_id},
        }
        self._post(url, payload)

    def _generate_digits(self, amount=int):
        return ''.join(random.choices('0123456789', k=amount))

    def _interact(self, guild_id, channel_id, message_id, author_id, custom_id):
        gen_digits = self._generate_digits(19)
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
        self._post(url, payload)

    def _on_message_wrapper(self, _, message):
        data = json.loads(message)
        if data.get("op") == 10:  # Hello packet
            self.heartbeat_interval = data["d"]["heartbeat_interval"]
            threading.Thread(target=self.heartbeat).start()
            self.identify()
        elif data.get("t") == "MESSAGE_CREATE":
            asyncio.run(self._handle_event("on_message", data["d"]))

    def on_close(self, _, close_status_code, close_msg):
        print("Disconnected from Discord. Attempting to reconnect...")
        self.start()

    async def _handle_event(self, event_name, *args, **kwargs):
        if event_name in self.event_handlers:
            await self.event_handlers[event_name](*args, **kwargs)
