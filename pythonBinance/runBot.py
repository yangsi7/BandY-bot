#!/usr/bin/python3

rroot="/home/euphotic_/yangino-bot/"
import sys
sys.path.append(rroot+'/pythonBinance/scripts/')
import YBotInit as ini
import os
from binance.client import Client
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import csv
import os.path
import argparse
import pickle
from datetime import datetime
from threading import Timer
import YBotFetchHistorical as fetchH
import YBotFetchRecent as fetchR
import time
import matlab.engine
import YBotCurrTrade as currTrade
import YBotPlot
import YBotFunctions as ybf
from YBotFunctions import waitForTicker, fireSig, CheckNew, \
        save_obj, load_obj, TickerStruct
#import logging
#logging.getLogger(__name__).addHandler(logging.NullHandler())

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
    # Root
#    import __init__    
    # Initialiaze paths and parameters

    SetUp = ini.initSetUp()

    # Update Tickers
    lrow = fetchH.main(['-pair', SetUp["trade"]["pair"],'-tickDt',SetUp["trade"]["tickDt"]])

    # Initialize Trade history files or get last
    TradeInfo=currTrade.initTradeFiles(SetUp)

    NewTicker = True
    while True:
        if not TradeInfo['CloseTimeStamp'].isnull()[0] and not NewTicker:
            # Wait for next ticker
            waitForTicker()
            # Start checking
            NewTicker,TradeInfo=CheckNew(SetUp,TradeInfo)
            if not NewTicker:
                print('Error: did not find new ticks')
                break
        else:

            signal,BB = fireSig(SetUp)
            TradeInfo=currTrade.TakeAction(TradeInfo,signal,BB,SetUp)
            sys.stdout.flush()
            save_obj(TradeInfo,SetUp['paths']['TradeInfo'])
            NewTicker = False
            YBotPlot.plotBot()
            sys.stdout.flush()
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

if __name__ == "__main__":
    main()
