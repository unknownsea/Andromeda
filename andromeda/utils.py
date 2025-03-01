# andromeda/utils.py
import requests
import random

class Utils:
    def _post(url, payload, token):
        headers = {
            "Authorization": f"{token}",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"POST : {response.status_code} {response.text}")
        return response

    def _get(url, token):
        """Helper method to send GET requests with authorization."""
        headers = {
            "Authorization": f"{token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"GET : {response.status_code} {response.text}")
        return response
    
    def _generate_digits(amount=int):
        return ''.join(random.choices('0123456789', k=amount))