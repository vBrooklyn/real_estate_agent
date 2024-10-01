import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

api_key = os.getenv("ATTOM_API_KEY")


class AttomApi:

    def get_property_type_api(self, address_street: str, address_city_state: str):
        url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail"
        # params = {
        #     "address1": "4529 Winona Court",
        #     "address2": "Denver, CO"
        # }
        params = {
            "address1": address_street,
            "address2": address_city_state
        }
        headers = {
            'accept': "application/json",
            'apikey': api_key  # Make sure 'api_key' is defined somewhere accessible
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()  # Raise an exception for bad HTTP status codes

            data = response.json()  # Automatically parse the JSON response
            print(data)  # Or process the data as needed
            return data


        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")