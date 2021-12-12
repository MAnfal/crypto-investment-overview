import csv
from types import resolve_bases
from csv_row import CSVRow
import json
from coin_market_cap import CoinMarketCap

processed_crypto_list = {}
liquidated_currency = {}
dca_dictionary = {}

currency_for_results = input("Please provide the name of currency to show results for: ")

coin_market_cap = CoinMarketCap()

csv_name = 'export.csv'

native_currency = None

def add_crypto_key_if_absent(crypto_key):
    if crypto_key not in processed_crypto_list:
        processed_crypto_list[crypto_key] = {
            'coin_amount': 0,
            'coin_amount_outside_cdc': 0,
            'fiat_invested': 0,
            'fiat_invested_outside_cdc': 0
        }

def add_liquidated_currency_key_if_absent(currency_key):
    if currency_key not in liquidated_currency:
        liquidated_currency[currency_key] = 0

def add_dca_key_if_absent(crypto_key):
    if crypto_key not in dca_dictionary:
        dca_dictionary[crypto_key] = {
            'fiat_invested': 0,
            'number_of_coins_purchased': 0
        }

def process_viban_purchase(row: CSVRow):
    crypto_currency_purchased = row.to_currency
    money_spent = row.native_amount
    total_crypto_bought = row.to_amount

    add_crypto_key_if_absent(crypto_currency_purchased)

    processed_crypto_list[crypto_currency_purchased]['coin_amount'] += total_crypto_bought
    processed_crypto_list[crypto_currency_purchased]['fiat_invested'] += money_spent

def process_normal_plus(row: CSVRow):
    crypto_currency_received = row.currency
    crypto_currency_amount = row.amount
    fiat_amount = row.native_amount

    add_crypto_key_if_absent(crypto_currency_received)

    processed_crypto_list[crypto_currency_received]['coin_amount'] += crypto_currency_amount
    processed_crypto_list[crypto_currency_received]['fiat_invested'] += fiat_amount

def process_crypto_liqudation(row: CSVRow):
    crypto_liquidated = row.currency
    amount_liquidated = row.amount
    fiat_currency = row.to_currency
    fiat_amount = row.to_amount

    add_crypto_key_if_absent(crypto_liquidated)
    add_liquidated_currency_key_if_absent(fiat_currency)

    # amount liquidated is in - so + will become auto minus
    processed_crypto_list[crypto_liquidated]['coin_amount'] += amount_liquidated
    processed_crypto_list[crypto_liquidated]['fiat_invested'] -= fiat_amount

    liquidated_currency[fiat_currency] += fiat_amount

def process_convert_one_crypto_to_another(row: CSVRow):
    from_currency = row.currency

    # We want this number to be positive.
    from_amount = -1 * row.amount

    to_currency = row.to_currency
    to_amount = row.to_amount

    fiat_amount = row.native_amount

    add_crypto_key_if_absent(from_currency)
    add_crypto_key_if_absent(to_currency)

    processed_crypto_list[from_currency]['coin_amount'] -= from_amount
    processed_crypto_list[from_currency]['fiat_invested'] -= fiat_amount

    processed_crypto_list[to_currency]['coin_amount'] += to_amount
    processed_crypto_list[to_currency]['fiat_invested'] += fiat_amount

def process_crypto_withdrawal(row: CSVRow):
    crypto_currency_received = row.currency

    # Amount is in negative in CSV
    crypto_currency_amount = -1 * row.amount

    # Amount is in negative in CSV
    fiat_amount = -1 * row.native_amount

    add_crypto_key_if_absent(crypto_currency_received)

    processed_crypto_list[crypto_currency_received]['coin_amount'] -= crypto_currency_amount

    processed_crypto_list[crypto_currency_received]['coin_amount_outside_cdc'] += crypto_currency_amount

    processed_crypto_list[crypto_currency_received]['fiat_invested'] -= fiat_amount

    processed_crypto_list[crypto_currency_received]['fiat_invested_outside_cdc'] += fiat_amount

def process_crypto_deposit(row: CSVRow):
    crypto_currency_received = row.currency

    crypto_currency_amount = row.amount

    fiat_amount = row.native_amount

    add_crypto_key_if_absent(crypto_currency_received)

    processed_crypto_list[crypto_currency_received]['coin_amount'] += crypto_currency_amount

    processed_crypto_list[crypto_currency_received]['coin_amount_outside_cdc'] -= crypto_currency_amount

    processed_crypto_list[crypto_currency_received]['fiat_invested'] += fiat_amount

    processed_crypto_list[crypto_currency_received]['fiat_invested_outside_cdc'] -= fiat_amount

def process_dca_record(row: CSVRow):
    # This value will be in - since it is deducted
    fiat_invested = -1 * row.amount

    crypto_purchased = row.to_currency
    coins_purchased = row.to_amount

    add_dca_key_if_absent(crypto_purchased)

    dca_dictionary[crypto_purchased]['fiat_invested'] += fiat_invested
    dca_dictionary[crypto_purchased]['number_of_coins_purchased'] += coins_purchased

def process_csv_row_object(row: CSVRow):
    if row.transaction_description == 'viban_purchase':
        process_viban_purchase(row)
    
    if row.transaction_description in [
        'referral_card_cashback', 
        'rewards_platform_deposit_credited', 
        'reimbursement', 
        'mco_stake_reward',
        'crypto_earn_interest_paid',
        'dust_conversion_credited',
        'dust_conversion_debited',
        'exchange_to_crypto_transfer',
        'crypto_to_exchange_transfer',
        'supercharger_reward_to_app_credited',
        'admin_wallet_credited',
        'reimbursement_reverted',
        'referral_gift'
    ]:
        process_normal_plus(row)

    if row.transaction_description == 'crypto_viban_exchange':
        process_crypto_liqudation(row)

    if row.transaction_description == 'crypto_exchange':
        process_convert_one_crypto_to_another(row)

    if row.transaction_description == 'crypto_withdrawal':
        process_crypto_withdrawal(row)

    if row.transaction_description == 'crypto_deposit':
        process_crypto_deposit(row)

    if row.transaction_description in ['viban_purchase']:
        process_dca_record(row)

with open(csv_name, newline='') as csv_file:
    spam_reader = csv.reader(csv_file, delimiter=',')

    next(spam_reader)

    for row in spam_reader:
        csv_row_object = CSVRow()

        csv_row_object.timestamp = row[0]
        csv_row_object.transaction_description = row[1]
        csv_row_object.currency = row[2]

        if row[3] != '':
            csv_row_object.amount = float(row[3])

        csv_row_object.to_currency = row[4]

        if row[5] != '':
            csv_row_object.to_amount = float(row[5])
        
        csv_row_object.native_currency = row[6]
        
        if row[7] != '':
            csv_row_object.native_amount = float(row[7])
        
        if row[8] != '':
            csv_row_object.native_amount_in_usd = float(row[8])
        
        csv_row_object.transaction_description = row[9]

        if native_currency is None:
            native_currency = csv_row_object.native_currency

        process_csv_row_object(csv_row_object)

current_coin_value = coin_market_cap.get_current_coin_price(currency_for_results, native_currency)

coin_results = processed_crypto_list[currency_for_results]
dca_results = dca_dictionary[currency_for_results]

# reformat values
coin_results['coin_amount'] = coin_results['coin_amount'] if coin_results['coin_amount'] > 0 else 0 
coin_results['coin_amount_outside_cdc'] = coin_results['coin_amount_outside_cdc'] if coin_results['coin_amount_outside_cdc'] > 0 else 0 
coin_results['fiat_invested'] = coin_results['fiat_invested'] if coin_results['fiat_invested'] > 0 else 0 
coin_results['fiat_invested_outside_cdc'] = coin_results['fiat_invested_outside_cdc'] if coin_results['fiat_invested_outside_cdc'] > 0 else 0 

# calculations
coin_results['total_coins'] = coin_results['coin_amount_outside_cdc'] + coin_results['coin_amount']
coin_results['total_fiat_invested'] = coin_results['fiat_invested_outside_cdc'] + coin_results['fiat_invested']
coin_results['current_fiat_value'] = coin_results['total_coins'] * current_coin_value
coin_results['total_percent_p/l_fiat'] = ((coin_results['current_fiat_value'] - coin_results['total_fiat_invested']) / coin_results['total_fiat_invested']) * 100

# Format the data to look pretty.
coin_results['coin_amount_outside_cdc'] = "{:.4f} {}".format(coin_results['coin_amount_outside_cdc'], currency_for_results)
coin_results['coin_amount'] = "{:.4f} {}".format(coin_results['coin_amount'], currency_for_results)
coin_results['fiat_invested'] = "{} {}".format(round(coin_results['fiat_invested'], 2), native_currency)
coin_results['fiat_invested_outside_cdc'] = "{} {}".format(round(coin_results['fiat_invested_outside_cdc'], 2), native_currency)
coin_results['total_coins'] = "{:.4f} {}".format(coin_results['total_coins'], currency_for_results)
coin_results['total_fiat_invested'] = "{} {}".format(round(coin_results['total_fiat_invested'], 2), native_currency)
coin_results['current_fiat_value'] = "{} {}".format(round(coin_results['current_fiat_value'], 2), native_currency)
coin_results['total_percent_p/l_fiat'] = "{}%".format(round(coin_results['total_percent_p/l_fiat'], 2))
coin_results['average_buying_price_per_coin'] = "{} {}".format(round((dca_results['fiat_invested'] / dca_results['number_of_coins_purchased']), 2), native_currency)

print(json.dumps(processed_crypto_list[currency_for_results], indent=2))

# print(json.dumps(liquidated_currency, indent=2))