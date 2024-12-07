import logging
import requests

from .utils import Utils

class Message:
    def __init__(self, token):
        self.token = token

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
        )
        self.logger = logging.getLogger(__name__)

    def _get_channel_history(self, channel_id, limit=100, before=None, after=None, around=None):
        """Fetch message history for a specific channel."""
        url = f"https://discord.com/api/v10/channels/{channel_id}/messages?limit={limit}"
        
        if before:
            url += f"&before={before}"
        if after:
            url += f"&after={after}"
        if around:
            url += f"&around={around}"

        response = Utils._get(url, self.token)
        if response.status_code == 200:
            return response.json()
        else:
            self.logger.error(f"Failed to fetch channel history: {response.status_code} {response.text}")
            return None

    def _fetch_message_until_found(self, channel_id, message_id, limit=100):
        """Fetch channel history until a specific message ID is found."""
        self.logger.info(f"Starting to fetch message history for channel ID: {channel_id}")
        last_message_id = None

        while True:
            self.logger.info(f"Fetching messages with limit={limit} before={last_message_id}")
            history = self._get_channel_history(channel_id, limit=limit, before=last_message_id)

            if not history:
                self.logger.warning("No more messages to fetch or failed to fetch history.")
                break

            self.logger.info(f"Fetched {len(history)} messages. Checking for message ID: {message_id}")
            for msg in history:
                if msg["id"] == message_id:
                    self.logger.info(f"Message with ID {message_id} found.")
                    return msg  # Return the specific message once found

            # Continue fetching older messages
            last_message_id = history[-1]["id"]
            self.logger.debug(f"Setting last_message_id to {last_message_id} for the next fetch.")

        self.logger.error(f"Message with ID {message_id} not found in channel history.")
        return None
