from __future__ import print_function
from googleapiclient.discovery import build
from google.oauth2 import service_account
from bs4 import BeautifulSoup
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import smtplib
import os

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'keys.json'
API_KEY = os.environ["API_KEY"]
EMAIL = os.environ["EMAIL"]
EMAIL_PASS = os.environ["EMAIL"]


def get_latest_token_from_coinmarketcap():
    coin_market_cap_request = Session()
    coin_market_cap_response = coin_market_cap_request.get("https://coinmarketcap.com/new/").text
    soup = BeautifulSoup(coin_market_cap_response, "lxml")
    latest_token = soup.find(name="p", class_="sc-1eb5slv-0 iJjGCS").text
    return latest_token


def get_latest_token_from_coingecko():
    coin_gecko_request = Session()
    coin_gecko_response = coin_gecko_request.get("https://www.coingecko.com/en/coins/recently_added").text
    soup = BeautifulSoup(coin_gecko_response, "lxml")
    latest_token_url = soup.find(name="a", class_="d-lg-none").get("href")
    latest_token = latest_token_url.split("/")[-1]
    return latest_token


def check_binance_new_listings():
    binance_request = Session()
    binance_response = binance_request.get("https://www.binance.com/en/support/announcement/c-48?navId=48").text
    soup = BeautifulSoup(binance_response, "lxml")
    latest_news = soup.find(name="a", class_="css-1ej4hfo").text
    NEWS_ID = "1pxysYni0Hb0xq8-Cwwqnb9PXYnd4sKr0UQuJ6XwIiJI"
    news = get_from_sheet(NEWS_ID)
    all_news = [x[0] for x in news]
    if latest_news in all_news:
        print("ok")
    else:
        add_to_sheet([latest_news], NEWS_ID)
        connection = smtplib.SMTP("smtp.gmail.com")
        connection.starttls()
        connection.login(EMAIL, EMAIL_PASS)
        connection.sendmail(EMAIL, EMAIL,
                            f"Subject: New Listing On Binance!\n\n{latest_news}\nhttps://www.binance.com/en/support/announcement/c-48?navId=48")


def get_token_data_from_coinmarketcap():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
        'start': '1',
        'limit': '1',
        'sort': 'date_added',
        'sort_dir': 'asc'
        }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY
        }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)['data']
        token_name = data[0]['name']
        token_contract = data[0]['platform']['token_address']
        token_chain = data[0]['platform']['name']
        token_price = "{:.15f}".format(float(data[0]['quote']['USD']['price']))
        one_hour_change = data[0]['quote']['USD']['percent_change_1h']

        return [token_name, token_contract, token_chain, token_price, one_hour_change]

    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)


def get_token_data_from_coingecko(token):
    url = f"https://api.coingecko.com/api/v3/coins/{token}"
    session = Session()
    response = session.get(url)
    data = json.loads(response.text)
    token_name = data['id']
    token_contract = data['platforms']['binance-smart-chain']
    token_chain = data['asset_platform_id']
    token_price = "{:.15f}".format(float(data['market_data']['current_price']['usd']))
    one_hour_change = data['market_data']['price_change_percentage_24h']

    return [token_name, token_contract, token_chain, token_price, one_hour_change]


def send(data):
    token_name = data[0]
    token_contract = data[1]
    token_chain = data[2]
    price = data[3]
    one_hour_change = data[4]
    pancake_url="https://exchange.pancakeswap.finance/#/swap?outputCurrency="
    connection = smtplib.SMTP("smtp.gmail.com")
    connection.starttls()
    connection.login(EMAIL, EMAIL_PASS)
    connection.sendmail(EMAIL, EMAIL, f"Subject: Token: {token_name}\n\nContract: {pancake_url}{token_contract}\nChain: {token_chain}\nCurrent Price: {price}\nShift: {one_hour_change}")


creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
SPREADSHEET_ID = '1TX90DYIHB25HLfpWg_LFaH4gQMGjcmGjQMwLvWG3jGY'
range_name = 'A1:F99'


def get_from_sheet(ID):
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=ID, range=range_name).execute()
    values = result.get('values', [])
    return values


def add_to_sheet(data, ID):
    data_table = [data]

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    result = sheet.values().append(spreadsheetId=ID,
                                   range="A1:F2",
                                   valueInputOption='RAW',
                                   insertDataOption='INSERT_ROWS',
                                   body={"values": data_table}).execute()


def check_coinmarketcap():
    latest_token = get_latest_token_from_coinmarketcap()
    all_coins = get_from_sheet(SPREADSHEET_ID)
    coin_table = [x[0] for x in all_coins if x[0] != "TOKEN"]
    if latest_token not in coin_table:
        data = get_token_data_from_coinmarketcap()
        if data[2] == "Binance Smart Chain":
            add_to_sheet(data, SPREADSHEET_ID)
            send(data)


def check_coingecko():
    latest_token = get_latest_token_from_coingecko()
    print(latest_token)
    all_coins = get_from_sheet(SPREADSHEET_ID)
    coin_table = [x[0] for x in all_coins if x[0] != "TOKEN"]
    print(coin_table)
    if latest_token not in coin_table:
        data = get_token_data_from_coingecko(latest_token)
        if data[2] == "binance-smart-chain":
            add_to_sheet(data, SPREADSHEET_ID)
            send(data)

