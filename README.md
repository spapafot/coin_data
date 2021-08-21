# New Cryptocurrency Data

Noticed a pattern with new crypto tokens, mostly on Binance Chain

As soon as they enter coinmarketcap, coingecko or binance they double or triple in value in a matter of hours

I wrote a script and had it running on pythonanywhere every 5 minutes

It scrapes coinmarketcap and coingecko for new listings, if it finds one it calls the API and sends me the token address (had to do it this way because of the free API key restrictions) so i can immediately buy on Pancakeswap

I also used the Google Sheets API to track one hour price shifts and make sure that the token wasn't already listed 

Did the same to get any new announcement from Binance new listings

If anyone wants to use it, have fun.
