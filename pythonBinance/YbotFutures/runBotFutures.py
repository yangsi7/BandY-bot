#!/usr/bin/python3

rroot="/home/euphotic_/yangino-bot/pythonBinance/YbotFutures"
import sys
sys.path.append(rroot)
from trade import *

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
    tries = 0
    while True:
        if tries > 10:
            print('10 errors in a row... exiting')
            break
        try:
            SetUp = ini.initSetUp()

            # Update Tickers
            lrow = fetchH.main(['-pair', SetUp["trade"]["pair"],'-tickDt',SetUp["trade"]["tickDt"]])

            # Initialize Trade history files or get last

            NewTicker = True
            while True:
                TradeInfo=YbotUtils.initTradeFiles(SetUp)
                if not TradeInfo['Close timestmp'].isnull()[0] and not NewTicker:
                    # Wait for next ticker
                    waitForTicker(SetUp,TradeInfo)
                    # Start checking
                    NewTicker,TradeInfo=CheckNew(SetUp,TradeInfo)
                    if not NewTicker:
                        print('Error: did not find new ticks')
                        break
                else:

                    signal,BB = fireSig(SetUp,0)
                    TradeInfo=trade.TakeAction(TradeInfo,signal,BB,SetUp)
                    sys.stdout.flush()
                    NewTicker = False
#                    plotOutput.plotBot()
                    sys.stdout.flush()
                    time.sleep(1*60)
                    tries = 0
        except:
            print('An unknown error occured, trying again')
            time.sleep(60)
            tries = tries + 1


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
