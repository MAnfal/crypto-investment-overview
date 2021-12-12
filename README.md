# How To Run

1. Install [Python](https://www.python.org/downloads/).
2. Create [CoinMarketCap](https://coinmarketcap.com/api/) developer account and copy the API key.
3. Export an environment variable like the following: `export COIN_MARKET_CAP_KEY=[API_KEY]`.
4. In Crypto.com's app, click on the history icon on top, select crypto wallet and the maximum date range you want to get the insights for. Once the file is downloaded, place it in the same folder as `index.py` and rename it to `export.csv`
5. From the command line, run the following command: `python index.py`.
6. Provide the coin name you want the data for and press enter.

# Sample

```
~ python index.py

Please provide the name of currency to show results for: SOL

{
  "coin_amount": "1.0000 SOL",
  "coin_amount_outside_cdc": "0.0000 SOL",
  "fiat_invested": "255.63 CAD",
  "fiat_invested_outside_cdc": "0 CAD",
  "total_coins": "1.0000 SOL",
  "total_fiat_invested": "255.63 CAD",
  "current_fiat_value": "223.88 CAD",
  "total_percent_p/l_fiat": "-12.42%",
  "average_buying_price_per_coin": "255.63 CAD"
}
```
