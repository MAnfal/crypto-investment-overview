import requests
from requests.api import head
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import os

class CoinMarketCap:
    def __init__(self) -> None:
        self.API_KEY = os.environ['COIN_MARKET_CAP_KEY']

    def get_current_coin_price(self, coin_name, fiat_currency):
        current_price = None

        parameters = {
            'symbol': coin_name,
            'convert': fiat_currency
        }

        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.API_KEY,
        }

        try:
            response = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest', params=parameters, headers=headers)
            response_json = response.json()

            current_price = response_json['data'][coin_name]['quote'][fiat_currency]['price']
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

        return current_price