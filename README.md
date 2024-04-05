# trading-212-fun

Program that allows for creation of pies, that allows you to get recent stock data from a given stock. You can create as many pies as you want and add/remove whatever stock you want from them.

## How to run
`python stock_searcher.py`

## Commands
- 'h': Brings up a list of all commands

- 's {ticker}': Search for a stock by its ticker returning a table with its Ticker, Name, CCY, Price, 1M%, 3M%, 6M%, 1Y%, 5Y%, Industry

- 'n {newPieName}': Creates a new pie for the specified name
- 'd {existingPieName}': Deletes the pie with the given name

- 'l': Lists out the names of all the pies the user has made
- 'v {existingPieName}':  Returns a table with each stock in a pie with its Ticker, Name, CCY, Price, 1M%, 3M%, 6M%, 1Y%, 5Y%, Industry
- 'a {ticker}': Adds the given stock to the currently selected pie
- 'r {ticker}': Removes the given stock from the currently selected pie

- 'b': Deselects the current pie
- 'q': Terminates the program

# External Libraries Needed
yfinance: `pip install yfinance`
tabulate: `pip install tabulate`

Made by Junaid Mohammad :)