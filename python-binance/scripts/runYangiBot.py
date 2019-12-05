#!/usimport os.pathr/bin/env python

"""Module summary
This script runs the incredible Yangino Bot, hoping to 
make some cash instead of ruining his creator. 

26 Nov 2019
Currently set-up to trade hourly BTC-USDT candle sticks on Binance.
    -The model used is a simple Random Forest trained over the
    past 6 months
    -It takes as input ~30 technical indicators and fires Buy and Sell
    signals
    -The bot starts trades based on those signals.
    -The bot starts trailing limit and stop orders based on those signals
        limit and stops orders are updated at every candle stick
"""


from binance.client import Client
from datetime import datetime
import sys
sys.path.append('/Users/yangsi/Box Sync/Crypto/scripts/python-binance/scripts')
import csv
import os.path
import argparse
import pickle
from datetime import datetime
from threading import Timer
import fetch_historical
import time
import matlab.engine
import pandas as pd


def initSetUp():
    # Case name
    Exchange = "Binch"

    # Paths
    SetUp={"paths":{},"trade":{}};
    SetUp['paths']["secure"]="/Users/yangsi/Box Sync/Crypto/secure/"+Exchange+"API.txt"
    SetUp['paths']["csvwrite"]="/Users/yangsi/Box Sync/Crypto/scripts/python-binance/Data/"
    SetUp['paths']["trade"]="/Users/yangsi/Box Sync/Crypto/scripts/python-binance/tradeData/"
    SetUp['paths']["matlab"]="/Users/yangsi/Box Sync/Crypto/scripts/functions/"
    SetUp['paths']["model"]="/Users/yangsi/Box Sync/Crypto/scripts/models/fre_26Nov2019.mat"

    # General Parameters
    SetUp["trade"]["pairTrade"]="BTC"
    SetUp["trade"]["pairRef"]="USDT"
    SetUp["trade"]["pair"]="BTCUSDT"
    SetUp["trade"]["tickDt"]="1h"
    SetUp["trade"]["MFee"]=0.075
    SetUp["trade"]["TFee"]=0.075

    # Trading parameters
    SetUp["trade"]["StartFunds"]=100
    SetUp["trade"]["PercentFunds"]=0.5
    SetUp["trade"]["SLTresh"]=0.02
    SetUp["trade"]["LOTresh"]=0.02

    # Dependant Paths
    # CSVs
    ffile=Exchange + SetUp["trade"]["pair"] + SetUp["trade"]["tickDt"] + ".csv"
    SetUp['paths']["Hist"]=SetUp["paths"]["csvwrite"] + ffile
    ffile=Exchange + SetUp["trade"]["pair"] + SetUp["trade"]["tickDt"]+"_Journal.csv"
    SetUp['paths']["Journal"]=SetUp["paths"]["csvwrite"] + ffile
    # Pickles
    SetUp['paths']["LastInfo"]=SetUp["paths"]["csvwrite"] + "Binance" + SetUp["trade"]["tickDt"]
    SetUp['paths']["TradeInfo"]=SetUp["paths"]["trade"] + "CurrTradeBinance" + SetUp["trade"]["tickDt"]

    return SetUp


def main():
    # Initialiaze paths and parameters
    SetUp = initSetUp()

    # Update Tickers
    lrow = fetch_historical.main(['-update', '-GetcsvLast','-pair', SetUp["trade"]["pair"],'-tickDt',SetUp["trade"]["tickDt"]])

    # Initialize Trade history files
    TradeInfo=initTradeFiles(SetUp)
    if TradeInfo['Funds']==None:
        TradeInfo['Funds']=SetUp['trade']['StartFunds']

    while True:
        # Start 2 minutes before next ticker (hours for now) 
        x=datetime.today()
        y=x.replace(day=x.day, hour=x.hour, minute=58, second=0, microsecond=0)
        delta_t=y-x
        secs=delta_t.seconds+1
        
        t = Timer(secs, CheckNew(SetUp)
        out = t.start()
        if not NewTicker:
            print('Error: did not find new ticks')
            break
        print("New tick is "+ str(out(2)))
        signal = fireSig(SetUp["paths"]["model"])

    # Test CurrTrade
    SetUp = initSetUp()
    TradeInfo=initTradeFiles(SetUp)
    if TradeInfo['Funds']==None:
        TradeInfo['Funds']=SetUp['trade']['StartFunds']    

    # Buy 
    TradeInfo=currTrade.buyOrder(SetUp,TradeInfo)

    # Initiate Stop Loss
    TradeInfo=currTrade.stopLoss(SetUp,TradeInfo)
    
# Strategy done in matlab
# Now need function to
    # (1) Check for existing trades()
    # (2) Start orders if needed
    # (3) Set Stop-loses / Limit orders of needed
    # (4) Close orders if needed
    # (5) Keep track of trades / profits 
    # (6) Trigger plotting routine
    # (7) upload to browser
    # (8) update automatically?

# Notes
    # 28 Nov 2019
        ## Consider switching to mySQL instead of CSV 
        ## Need to test Class that triggers orders
        ## Need to retrain model on newer dates
    # 29 Nov 2019
        ## Need to go through Class CurrentTrade
         # and check that all selfs are updated 

def unpackOrder(order):
    p
def fireSig(SetUp):
    # call matlab scripts
    eng = matlab.engine.start_matlab()
    eng.addpath(SetUp["paths"]["matlab"])
    nrows = int(eng.getMaxWinForPython('model',SetUp["paths"]["model"]))
    rows = fetch_recent.main(['-window',str(nrows+1)])
    rows = [[float(i) for i in j] for j in rows]
    try:
        # Fire Buy/Short/Sell signals
        signal = eng.fireSigForPython(matlab.double(rows),'model',SetUp["paths"]["model"])
    except:
        print("Unexpected error:", sys.exc_info()[0])
    eng.quit()
    return signal

    qty=0
    comm=0
    for i in order['fills']:
        price = price + i['price']
        qty = qty + i['qty']
        comm= comm + i['comm']
    AdjPrice = Price-comm
    return AdjPrice,qty,comm

def fireSig(SetUp):
    # call matlab scripts 
    eng = matlab.engine.start_matlab()
    eng.addpath(SetUp["paths"]["matlab"])
    nrows = int(eng.getMaxWinForPython('model',SetUp["paths"]["model"]))
    rows = fetch_recent.main(['-window',str(nrows+1)])
    rows = [[float(i) for i in j] for j in rows]
    try:
        # Fire Buy/Short/Sell signals
        signal = eng.fireSigForPython(matlab.double(rows),'model',SetUp["paths"]["model"])
    except:
        print("Unexpected error:", sys.exc_info()[0])
    eng.quit()
    return signal

def CheckNew(pathInfo, pathTrade):
    NewTicker=False
    iter=0
    starttime=time.time()
    while time.time()-starttime < 240:
        iter=iter+1
        try:
            Tick = fetch_historical.main(['-update','-GetcsvLast',
                '-pair', SetUp["trade"]["pair"],'-tickDt',SetUp["trade"]["tickDt"],'-no-verbose'])
        finally:
            LastInfo = load_obj(SetUp['paths']["LastInfo"])
            TradeInfo = load_obj(pathTrade)
        if LastInfo['LastTimeStamp'] == TradeInfo['CloseTimeStamp']:
            if iter == 1: 
                print("Start checking for new ticker")
                print("No new ticker yet",end='')
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
            time.sleep(10.0 - ((time.time() - starttime) % 10.0))
        else:
            print("")
            print("Found new Ticker!")
            NewTicker=True
            break
    if not NewTicker:
        print("")
        print("No Ticker found... exiting")
    return NewTicker,Tick         

def initTradeFiles(SetUp):
    # Initialize or load trade Information (pickle)
    if not os.path.isfile(SetUp['paths']["LastInfo"]):
        CurrTradeInfo = {'CloseTimeStamp':None,'Funds':None,'chfBuy':None,'shareBuy':None,
                'chfShort':None, 'shareShort':None, 'currStopLoss':None,'currStopLossLimit':None, 
                'currStopLossId':None,'currLimit':None,'currLimitId':None,'BNBcomm':0}
        save_obj(CurrTradeInfo,SetUp['paths']["TradeInfo"])
    else:
        CurrTradeInfo = load_obj(SetUp['paths']["LastInfo"])
    if not os.path.isfile(SetUp['paths']["Journal"]):
        # Write data to file
        writeOption = 'w'
        f = open(SetUp['paths']["Journal"], writeOption)
        wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        wr.writerow(["CloseTimeStamp","Funds","Shares","Close","Signal","Buys-action","Short-action","CurrChfBuy","CurrChfShort","CurrSharesBuy","CurrSharesShort","CloseBuy","CloseShort", "Curr Stop loss","Curr limit"])
        f.close()
    return CurrTradeInfo

def unpackTradeInfo(CurrTradeInfo):
    Funds=CurrTradeInfo['Funds']
    chfBuy=CurrTradeInfo['chfBuy']
    chfShort=CurrTradeInfo['chfShort']
    shareBuy=CurrTradeInfo['shareBuy']
    shareShort=CurrTradeInfo['shareShort']
    currStopLoss=CurrTradeInfo['currStopLoss']
    currLimit=CurrTradeInfo['currLimit']
    return (Funds,chfBuy,chfShort,shareBuy,shareShort,currStopLoss,currLimit)


def writetTosv(path,row):
    # Write data to file
    writeOption = 'a' 
    f = open(path, writeOption)
    wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
    for item in tick.contlist:
        wr.writerow(item)
    f.close()
    
def save_obj(obj, path):
    with open(path + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(path):
    with open(path + '.pkl', 'rb') as f:
        return pickle.load(f)

class TickerStruct:
    pass

if __name__ == "__main__":
    main()
