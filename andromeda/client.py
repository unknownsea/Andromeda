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

class Andromeda:
    def __init__(self, token, start_time):
        self.token = token
        self.intents = 53608447
        self.GATEWAY_URL = "wss://gateway.discord.gg/?v=10&encoding=json"

        self.start_time = start_time
        self.ws = None
        self.heartbeat_interval = None
        self.message_cache = {}

        self.event_handlers = {}
        self.command_handlers = {}
        self._initialize_user_data()

    def _initialize_user_data(self):
        response = Utils._get("https://discord.com/api/v10/users/@me", self.token)
        if response.status_code == 200:
            user_data = response.json()
            for key, value in user_data.items():
                setattr(self, key, value)
        else:
            raise RuntimeError(f"Failed to fetch user info: {response.status_code} {response.text}")

    def command(self, func):
        self.command_handlers[func.__name__] = func
        return func

    def event(self, coro):
        self.event_handlers[coro.__name__] = coro
        return coro

    def start(self, debug=True):
        if debug:
            print(f"{Fore.BLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{Style.RESET_ALL} Starting client : {self.GATEWAY_URL}")

        self.ws = websocket.WebSocketApp(
            self.GATEWAY_URL,
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
                "intents": self.intents,
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
                try:
                    if "id" in data["d"] and "content" in data["d"]:
                        if len(self.message_cache) > 10000:
                            oldest_message_id = next(iter(self.message_cache))
                            del self.message_cache[oldest_message_id]
                        self.message_cache[data["d"]["id"]] = data["d"]["content"]
                except Exception as e:
                    pass
                asyncio.run(self._handle_message(f"on_{data['t'].lower()}", data["d"]))
        except Exception as e:
            pass


    def on_close(self, _, close_status_code, close_msg):
        print("Disconnected from Discord. Attempting to reconnect...")
        self.start()

    async def _handle_message(self, name, *args):
        if name in self.event_handlers:
            await self.event_handlers[name](*args)
        elif name in self.command_handlers:
            await self.command_handlers[name](*args)
        else:
            pass


