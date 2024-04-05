import json
import yfinance as yf
from datetime import datetime
import pandas as pd
import warnings
from tabulate import tabulate
import sqlite3

warnings.filterwarnings("ignore", category=FutureWarning)

current_date = datetime.now().date()

connection = sqlite3.connect('Pies.db')
cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS pies (
            pieName VARCHAR(50) PRIMARY KEY,
            stocks JSON
                 )""")

def loadPies():
    pieDict = {}
    selectPieSql = """
        SELECT *
        FROM pies
    """

    cursor.execute(selectPieSql)
    pieSqlData = cursor.fetchall()
    for row in pieSqlData:
        pieName = row[0]
        pieDict[pieName] = {}
        for stock in json.loads(row[1]):
            pieDict[pieName][stock] = {}

    return pieDict

def loadStocks(currentPie):
    for stock in mainPieDict[currentPie]:
        myStockTable = getStockPrice(stock.upper())
        if myStockTable.at[0, 'Name'] != 'NOT FOUND':
            stockData = myStockTable.iloc[0].to_dict()
            ticker = stockData.pop('Ticker')
            mainPieDict[currentPie][ticker] = stockData

def savePie(stocksList, pieName):
    updatePieSql = """
        UPDATE pies
        SET stocks = ?
        WHERE pieName = ?
    """
    updatePieParams = [json.dumps(stocksList), pieName]
    cursor.execute(updatePieSql, updatePieParams)
    connection.commit()

def createPie(pieName):
    insertPieSql = """
        INSERT INTO pies
        (pieName, stocks)
        VALUES (?, ?)
    """
    insertPieParams = [pieName, json.dumps([])]
    cursor.execute(insertPieSql, insertPieParams)
    connection.commit()

def deletePie(pieName):
    deletePieSql = """
        DELETE FROM pies
        WHERE pieName = ?
    """

    deletePieParams = [pieName]
    cursor.execute(deletePieSql, deletePieParams)
    connection.commit()
    mainPieDict.pop(pieName)

def helpMethod():
    print("""  
        'h': help

        's': search a stock
          
        'n': new pie
        'd': delete pie
          
        'l': list all pies
        'v': view a pie
        'a': add to a pie
        'r': remove from a pie
             
        'b': back
        'q': quit 
    """)

def getStockPrice(ticker):
    monthlyPercentages = []
    timeFrames = ['1mo', '3mo', '6mo', '1y', '5y']

    columns = ['Ticker', 'Name', 'CCY', 'Current Price', '1M', '3M', '6M', '1Y', '5Y', 'Industry']
    stockTable = pd.DataFrame(columns=columns)
    stockTable.at[0, 'Ticker'] = ticker

    stock = yf.Ticker(ticker)

    try:
        for timePeriod in timeFrames:
            historicalData = stock.history(period = timePeriod) 
            startPrice = historicalData['Close'].iloc[0]
            endPrice = historicalData['Close'].iloc[-1] 

            percentChange = round((endPrice - startPrice)/ startPrice * 100,1)
            monthlyPercentages.append(percentChange)

        companyInfo = stock.info

        stockTable.at[0, 'Name'] = companyInfo.get('shortName', 'Name not found')
        stockTable.at[0, 'CCY'] = companyInfo.get('currency', 'Currency not found')
        stockTable.at[0, 'Current Price'] = companyInfo.get('currentPrice', 'Price not found')
        stockTable.at[0, '1M'] = monthlyPercentages[0]
        stockTable.at[0, '3M'] = monthlyPercentages[1]
        stockTable.at[0, '6M'] = monthlyPercentages[2]
        stockTable.at[0, '1Y'] = monthlyPercentages[3]
        stockTable.at[0, '5Y'] = monthlyPercentages[4]
        stockTable.at[0, 'Industry'] = companyInfo.get('industryDisp', 'Industry not found')
    
    except Exception as e:
        print(F"ERROR: {e}")
        stockTable.at[0, 'Name'] = 'NOT FOUND'
    
    return stockTable

def viewPie(pieName):
    pieTable = pd.DataFrame(mainPieDict[pieName]).T.reset_index()
    pieTable = pieTable.rename(columns={'index': 'Ticker'})
    print(tabulate(pieTable, headers='keys', tablefmt='grid'))

mainPieDict = {}

userInput = ""
currentPie = ""
mainPieDict = loadPies()

while userInput != "q":
    userInput = input(f"{currentPie}- ")

    # GENERAL
    if userInput == "h":
        helpMethod()
    
    elif userInput == "l":
        if not mainPieDict:
            print("No pies created yet")
        else:
            for pie in mainPieDict:
                print(pie)
    
    elif userInput == "b":
        currentPie = ""

    # COMPLEX COMMANDS
    splitUpInput = userInput.split(" ")
    if len(splitUpInput) == 1:
        continue
    
    # STOCKS
    if splitUpInput[0].startswith('s'):
        myStockTable = getStockPrice(splitUpInput[1].upper())
        print(tabulate(myStockTable, headers='keys', tablefmt='grid'))
    
    # PIES
    elif splitUpInput[0].startswith('a'):
        if not currentPie:
            print(f"ERROR: Select a pie first")
        else:
            myStockTable = getStockPrice(splitUpInput[1].upper())
            if myStockTable.at[0, 'Name'] != 'NOT FOUND':
                stockData = myStockTable.iloc[0].to_dict()
                ticker = stockData.pop('Ticker')
                mainPieDict[currentPie][ticker] = stockData

                viewPie(currentPie)
                savePie(list(mainPieDict[currentPie].keys()), currentPie)
    
    elif splitUpInput[0].startswith('r'):
        if not currentPie:
            print(f"ERROR: Select a pie first")
        else:
            stockToRemove = splitUpInput[1].upper()
            if stockToRemove in mainPieDict[currentPie]:
                mainPieDict[currentPie].pop(stockToRemove)
                viewPie(currentPie)
                savePie(list(mainPieDict[currentPie].keys()), currentPie)
            else:
                print(f"{stockToRemove} not found in {currentPie}")
    
    elif splitUpInput[0].startswith('n'):
        if ' '.join(splitUpInput[1:]) in mainPieDict:
            print(f"ERROR: {' '.join(splitUpInput[1:])} already exists")
        else:
            currentPie = ' '.join(splitUpInput[1:])
            mainPieDict[currentPie] = {}
            createPie(currentPie)
            print("Pie created")
    
    elif splitUpInput[0].startswith('d'):
        if ' '.join(splitUpInput[1:]) not in mainPieDict:
            print(f"ERROR: {' '.join(splitUpInput[1:])} not found")
        else:
            deletePie(' '.join(splitUpInput[1:]))
            print("Pie deleted")

    elif splitUpInput[0].startswith('v'):
        if ' '.join(splitUpInput[1:]) not in mainPieDict:
            print(f"ERROR: {' '.join(splitUpInput[1:])} not found")
        else:
            currentPie = ' '.join(splitUpInput[1:])
            loadStocks(currentPie)
            viewPie(currentPie)