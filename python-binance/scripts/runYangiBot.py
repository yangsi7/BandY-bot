#!/usr/bin/python
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
import fetch_recent
import time
import matlab.engine
import pandas as pd
import initBot as ini
import currTrade
import plotYangino

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



def main():
    # Initialiaze paths and parameters
    SetUp = ini.initSetUp()

    # Update Tickers
    lrow = fetch_historical.main(['-pair', SetUp["trade"]["pair"],'-tickDt',SetUp["trade"]["tickDt"]])

    # Initialize Trade history files
    TradeInfo=currTrade.initTradeFiles(SetUp)
    if TradeInfo['Funds']==None:
        TradeInfo['Funds']=SetUp['trade']['StartFunds']
    else:
        TradeInfo = load_obj(SetUp['paths']['TradeInfo'])

    NewTicker = True
    while True:
        if TradeInfo['CloseTimeStamp'] != None and not NewTicker:
            # Wait for next ticker
            waitForTicker()
            # Start checking
            NewTicker,TradeInfo=CheckNew(SetUp,TradeInfo)
            if not NewTicker:
                print('Error: did not find new ticks')
                break
        else:

            signal = fireSig(SetUp)
            TradeInfo=currTrade.TakeAction(TradeInfo,signal,SetUp)
            save_obj(TradeInfo,SetUp['paths']['TradeInfo'])
            NewTicker = False
            plotYangino.plotBot()
            time.sleep(5*60)


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

def waitForTicker():
    x=datetime.today()
    y=x.replace(day=x.day, hour=x.hour, minute=59, second=30, microsecond=0)
    delta_t=y-x
    secs=delta_t.seconds+1
    secWakeUp=60 # Wake up this many seconds before
    minInterv=10
    secInterv=minInterv*60
    nInterval=int(max(0,(secs-secWakeUp)//secInterv))
    # Sleep and Wake up this one minute before
    print('* * * * Next ticker in about '+str(secs//60)+' minutes * * * *')
    print('---> Going to sleep')
    for tt in range(0,nInterval):
        time.sleep(secInterv)
        print('...'+str((secs-secWakeUp-(tt+1)*secInterv)//60)+'min left...',end = '')
        sys.stdout.flush()
    timeleft=(secs-secWakeUp-nInterval*secInterv)
    time.sleep(timeleft)

def fireSig(SetUp):
    # call matlab scripts 
    eng = matlab.engine.start_matlab()
    eng.addpath(SetUp["paths"]["matlab"])
    nrows = int(eng.getMaxWinForPython('model',SetUp["paths"]["model"]))
    rows = fetch_recent.main(SetUp,['-window',str(nrows+1)])
    rows = [[float(i) for i in j] for j in rows]
    try:
        # Fire Buy/Short/Sell signals
        signal = eng.fireSigForPython(matlab.double(rows),'model',SetUp["paths"]["model"])
    except:
        print("Unexpected error:", sys.exc_info()[0])
    eng.quit()
    return signal

def CheckNew(SetUp,TradeInfo):
    NewTicker=False
    iter=0
    starttime=time.time()
    while time.time()-starttime < 240:
        iter=iter+1
        Tick = fetch_historical.main([
            '-pair', SetUp["trade"]["pair"],'-tickDt',SetUp["trade"]["tickDt"]])
        LastInfo=load_obj(SetUp['paths']["LastInfo"])

        if TradeInfo['CloseTimeStamp'] == LastInfo['LastTimeStamp']:
            if iter == 1: 
                print("Start checking for new ticker")
                print("No new ticker yet",end='')
            else:
                sys.stdout.write('.')
                sys.stdout.flush()
            NewTicker=False    
            time.sleep(10.0 - ((time.time() - starttime) % 10.0))
        else:
            print("")
            print("Found new Ticker!")
            NewTicker=True
            break
    if not NewTicker:
        print("")
        print("No Ticker found... exiting")
    return NewTicker,TradeInfo         

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
