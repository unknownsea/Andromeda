# andromeda/client.py
import websocket
import json
import threading
import time
import asyncio
from datetime import datetime
from colorama import Fore, Style

from .utils import Utils
from .handlers import Handlers

GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"
intents = 53608447

class Andromeda:
    def __init__(self, token, start_time):
        self.token = token
        self.start_time = start_time
        self.ws = None
        self.heartbeat_interval = None
        self.event_handlers = {}
        self._initialize_user_data()

    def _initialize_user_data(self):
        response = Utils._get("https://discord.com/api/v10/users/@me", self.token)
        if response.status_code == 200:
            user_data = response.json()
            for key, value in user_data.items():
                setattr(self, key, value)
        else:
            raise RuntimeError(f"Failed to fetch user info: {response.status_code} {response.text}")

    def event(self, coro):
        self.event_handlers[coro.__name__] = coro
        return coro

    def start(self, debug=True):
        if debug:
            print(f"{Fore.BLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL} Starting client : {GATEWAY_URL}")

        self.ws = websocket.WebSocketApp(
            GATEWAY_URL,
            on_message=self._on_message,
            on_close=self.on_close,
        )

        if debug:
            print(f"{Fore.BLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL} Client Initialized.")
            print(f"{Fore.BLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL} Starting Client Thread...")

        threading.Thread(target=self.ws.run_forever).start()

        if debug:
            print(f"{Fore.BLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL} Thread Initialized.\n")

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

    def _on_message(self, _, message):
        try:
            data = json.loads(message)
            if data.get("op") == 10:
                self.heartbeat_interval = data["d"]["heartbeat_interval"]
                threading.Thread(target=self.heartbeat).start()
                self.identify()
            else:
                asyncio.run(self._handle_event(f"on_{data['t'].lower()}", data.get("d")))
        except Exception as e:
            pass


    def on_close(self, _, close_status_code, close_msg):
        print("Disconnected from Discord. Attempting to reconnect...")
        self.start()

    async def _handle_event(self, event_name, data):
        if event_name in self.event_handlers:
            await self.event_handlers[event_name](data)
        else:
            pass


