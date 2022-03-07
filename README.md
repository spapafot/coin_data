# New Cryptocurrency Data

Scrapes coinmarketcap and coingecko for new listings, sends the token address on Pancakeswap

Uses Google Sheets API to track one hour price shifts and make sure that the token wasn't already listed 

Notifies about new Binance listings announcement

### Requirements

- Coinmarketcap API Key
- Google Sheets API key
- beautifulsoup4~=4.9.3
- requests~=2.25.1

NOTE: After you register a service worker you will need to add keys.json to your project root to use google sheets

### Usage

Add to __name__ == '__main__' any of the functionality you want to use and run
