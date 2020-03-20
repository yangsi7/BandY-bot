#!/usr/bin/python3

"""Module summary
High level module built on top of python-binance

Exectute trades based on provided signals
    and current trade information.

"""

import numpy as np
import pandas as pd
from datetime import datetime
import csv
import sys
import os.path
import argparse
import pickle
from datetime import datetime
from threading import Timer
import time
import matlab.engine
import collections

from .binanceFutures.client_futures import Client
from . import params as ini 
from .YbotUtils import initTradeFiles,\
        save_obj, load_obj, binFloat, \
        sendEmail,binStr, getBalance, appendToCsv
from .YbotUtils import AutoVivification as av
from . import fetchHistorical as fetchH

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
#       # Consider switching to mySQL instead of CSV 
#       # Need to test Class that triggers orders
#       # Need to retrain model on newer dates
#   # 29 Nov 2019
#        # Need to go through Class CurrentTrade
#          and check that all selfs are updated 
#    # 5 Dec 2019
#        # Using module with functions instead of a class
#        # Each function is called with dicts "SetUp" and 
#         "TradeInfo" as arguments
#        # SetUp contains all the paths and parameters specific
#          to this set-up and is initialized in runYanginoBot.py
#        # TradeInfo contains information about any current trades
#          and is initialized or set to its value in a saved pickle
#        # strategy has changed: now using stop-limit for both 
#          buys and sells. 
#        # Tested subfunctions:
#            # buyOrder
#            # stopLoss
#            # updateStopLoss (need to see if it fails or not when limit is hit)
#            # shortrder
def TakeAction(TradeInfo,signal,BB,SetUp):
    BBstr = 'bullish' if BB else 'bearish'
    print('-----')
    print('---Hotness index is .......'+str(round(signal,2))+' and market is *'+BBstr+'*.')

    print('-----')
    print('')
    if (TradeInfo['Buy Stop-Limit Id'].isnull()[0] and 
            TradeInfo['Sell Stop-Limit Id'].isnull()[0] and
            (SetUp['trade']['Long']<signal < SetUp['trade']['Short'] or 
                (signal < SetUp['trade']['Long'] and (not TradeInfo['BTC Bought'].isnull()[0] or BB == 0)) or
                (signal > SetUp['trade']['Short'] and (not TradeInfo['BTC Shorted'].isnull()[0] or BB == 1)))):
        print('--> No action taken')
    #-------------
    #--Update Stop-limit-sell
    #-------------
    if not TradeInfo['BTC Bought'].isnull()[0] and not TradeInfo['Sell Stop-Limit Id'].isnull()[0]:
        print('---Updating the existing stop-limit sell order...')
        if signal < SetUp["trade"]["CloseLong"]:
            print('Loosening trailing Stop --> '+str(SetUp["trade"]["StopSell"][0]))
            print('')
            TradeInfo=updateStopLimitSell(SetUp,TradeInfo, SetUp["trade"]["StopSell"][0], 
                    SetUp["trade"]["StopLimitSell"][0])
        else:
            print('Tightening trailing Stop --> '+str(SetUp["trade"]["StopSell"][1]))
            print('')
            TradeInfo=updateStopLimitSell(SetUp,TradeInfo, SetUp["trade"]["StopSell"][1], 
                    SetUp["trade"]["StopLimitSell"][1])

    #-------------
    #--Update Stop-limit-buy
    #-------------
    if not TradeInfo['BTC Shorted'].isnull()[0] and not TradeInfo['Buy Stop-Limit Id'].isnull()[0]:
        print('---Updating the existing stop-limit buy order...')
        if signal > SetUp["trade"]["CloseShort"]:
            print('Loosening trailing Stop --> '+str(SetUp["trade"]["StopBuy"][0]))
            print('')
            TradeInfo=updateStopLimitBuy(SetUp,TradeInfo, SetUp["trade"]["StopBuy"][0],
                    SetUp["trade"]["StopLimitBuy"][0])
        else:
            print('Tightening trailing Stop --> '+str(SetUp["trade"]["StopBuy"][1]))
            print('')
            TradeInfo=updateStopLimitBuy(SetUp,TradeInfo, SetUp["trade"]["StopBuy"][1],
                    SetUp["trade"]["StopLimitBuy"][1])
    #-------------
    #--Buy
    #-------------
    if TradeInfo['BTC Bought'].isnull()[0] and signal <= SetUp['trade']['Long'] and BB == 1:
        print('---BB is bullish and index is getting hot!')
        print('------')
        print('---Starting a buy order...')
        TradeInfo=buyOrder(SetUp,TradeInfo)
        TradeInfo=stopLimitSell(SetUp,TradeInfo,SetUp["trade"]["StopSell"][0],
                    SetUp["trade"]["StopLimitSell"][0])
    #-------------
    #--Short
    #-------------
    if TradeInfo['BTC Shorted'].isnull()[0] and signal>=SetUp['trade']['Short'] and BB == 0:
        print('---BB is bearish and Index is getting cold!')
        print('------')
        print('---Starting a short order...')
        TradeInfo=shortOrder(SetUp,TradeInfo)
        TradeInfo=stopLimitBuy(SetUp,TradeInfo,SetUp["trade"]["StopBuy"][0],
                    SetUp["trade"]["StopLimitBuy"][0])

    # Displaying last price 
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    print('Latest price: '+SetUp['trade']['pairTrade'] + '=' +str(LastPrice))

    # Sending email if anything happens
    sendEmail(TradeInfo)

    # Write trade journal
    LastInfo=load_obj(SetUp['paths']['LastInfo']) 
    TradeInfo['Close timestmp']=LastInfo['LastTimeStamp']
    TradeInfo['timestmp'] = int(time.time())
    TradeInfo['Signal'] = signal
    TradeInfo['BB'] = BB    
    appendToCsv(SetUp['paths']['TradeInfo'],TradeInfo)
    return TradeInfo

 # # # # # # # # # 
# Market Buy order 
# ----------------
def buyOrder(SetUp,TradeInfo):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    TradeInfo['BTC Bought'] =binFloat(TradeInfo['Free Funds'][0]*SetUp['trade']['PercentFunds']/LastPrice*SetUp['trade']['Leverage'])
    # Create a Long order
    order = client.create_order(
    symbol=SetUp['trade']['pair'],
    side='BUY',
    type='MARKET',
    quantity=binFloat(TradeInfo['BTC Bought'][0]),
    )    
    # Check order
    i=0
    while 1:
        i=i+1
        try:
            a=client.get_order(symbol=SetUp['trade']['pair'],orderId=int(order['orderId']))
            if a['status']=='FILLED':
                break
        except:
            print('Buy has not yet been filled')
            if i == 50:
                print('Failed to retreive status')
    TradeInfo['BTC Bought'] = binFloat(a['executedQty'])
    TradeInfo['BTCUSDT Buy Price'] = binFloat(TradeInfo['BTC Bought'][0]) 
#    if a['commissionAsset']=='BNB':
#        TradeInfo['Commission (BNB)'] =float(a['commission'])
#        BTCcomm=0
#    else:
#        BTCcomm=binFloat(a['commission'])
    TradeInfo['Buy-BTC'] = True
    acc=getBalance(SetUp)
    TradeInfo['Free Funds'] = acc['USDT']['wBalance']
    return TradeInfo

 # # # # # # # 
# Market short  
# ------------
def shortOrder(SetUp,TradeInfo):
    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')        
    client = Client(apiK[0], apiK[1])

    # calculate ammount to short
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])    
    TradeInfo['BTC Shorted'] = binFloat(TradeInfo['Free Funds'][0]*
            SetUp['trade']['PercentFunds']/LastPrice*SetUp['trade']['Leverage'])
    # Short at market price    
    order = client.create_order(
    symbol=SetUp['trade']['pair'],
    side='SELL',
    type='MARKET',
    quantity=binFloat(TradeInfo['BTC Shorted'][0]),
    )
    # Check order
    i=0
    while 1:
        i=i+1
        try:
            a=client.get_order(symbol=SetUp['trade']['pair'],orderId=int(order['orderId']))
            if a['status']=='FILLED':
                break
        except:
            print('Short has not yet been filled')
            if i == 50:
                print('Failed to retreive status')
    TradeInfo['BTC Shorted'] = binFloat(a['executedQty'])
    TradeInfo['BTCUSDT Short Price'] = binFloat(TradeInfo['BTC Shorted'][0])
#    if a['commissionAsset']=='BNB':
#        TradeInfo['Commission (BNB)'] =float(a['commission'])
#        BTCcomm=0
#    else:
#        BTCcomm=binFloat(a['commission'])
    TradeInfo['Short-BTC'] = True
    acc=getBalance(SetUp)
    TradeInfo['Free Funds'] = acc['USDT']['wBalance']
    return TradeInfo
    
def stopLimitSell(SetUp,TradeInfo,stop,limit):
    # use implicit Falsness of empty lists
    if not TradeInfo['Sell Stop-Limit Id'].isnull()[0]:
        print('Current stop loss (Id='+str(TradeInfo['Sell Stop-Limit Id'][0])+') exists')
        print('No action taken')
        return TradeInfo

    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Calculate Stop loss value
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    TradeInfo['Sell Stop Price'] = binFloat((1-float(stop))*LastPrice)
    TradeInfo['Sell Limit Price'] = binFloat((1-float(limit))*LastPrice)

    # Put in the order
    order = client.create_order(
    symbol=SetUp['trade']['pair'],
    side='SELL',
    type='STOP',
    timeInForce='GTC',
    reduceOnly = 'true',
    quantity=binFloat(TradeInfo['BTC Bought'][0]),
    stopPrice=binFloat(TradeInfo['Sell Stop Price'][0]),
    price=binFloat(TradeInfo['Sell Limit Price'][0])
    )

    TradeInfo['Sell Stop-Limit Id'] =int(order['orderId'])
    print('Initiated Stop loss limit at: '+ SetUp['trade']['pairTrade'] + '=' + str(
        TradeInfo['Sell Stop Price'][0])+'/'+str(TradeInfo['Sell Limit Price'][0]))
    return TradeInfo


def stopLimitBuy(SetUp,TradeInfo,stop,limit):
    # use implicit Falsness of empty lists
    if not TradeInfo['Buy Stop-Limit Id'].isnull()[0]:
        print('Current Limit Order (Id='+str(TradeInfo['Buy Stop-Limit Id'][0])+') exists')
        print('No action taken')
        return TradeInfo

    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Calculate Limit order value
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])    
    TradeInfo['Buy Stop Price'] = binFloat((1+float(stop))*LastPrice)
    TradeInfo['Buy Limit Price'] = binFloat((1+float(limit))*LastPrice)

    # Put in the order
    order = client.create_order(
    symbol=SetUp['trade']['pair'],
    side='BUY',
    type='STOP',
    timeInForce='GTC',
    reduceOnly = 'true',
    quantity=binFloat(TradeInfo['BTC Shorted'][0]),
    stopPrice=binStr(TradeInfo['Buy Stop Price'][0]),
    price=binStr(TradeInfo['Buy Limit Price'][0])    
    )

    TradeInfo['Buy Stop-Limit Id'] =int(order['orderId'])
    print('Initiated stop-limit-buy order at: '+ SetUp['trade']['pairTrade'] + '=' + str(
        TradeInfo['Buy Stop Price'][0])+'/'+str(TradeInfo['Buy Limit Price'][0]))
    return TradeInfo

def updateStopLimitSell(SetUp,TradeInfo,stop,limit):
    if TradeInfo['Sell Stop-Limit Id'][0] == np.nan:
        print('No stop loss found...')
        print('--> No action taken')
        return TradeInfo
    
    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Check Order status
    order = client.get_order(
    symbol=SetUp['trade']['pair'],
    orderId=int(TradeInfo['Sell Stop-Limit Id'][0]))
    if order['status'] == 'FILLED':
        print('Stop loss has been hit')
        # Check order
        a=client.get_my_trades(symbol=SetUp['trade']['pair'],limit=1)
        a=a[0]
        if a['commissionAsset']=='BNB':
            TradeInfo['Commission (BNB)'] =float(a['commission'])
        TradeInfo['Closed Buy Sell-Price'] =float(a['price'])
        ExecQty=float(a['qty'])
        TradeInfo['Closed Buy Profit'] = a['realizedPnl']
        acc=getBalance(SetUp)
        TradeInfo['Free Funds'] = acc['USDT']['wBalance']        
        TradeInfo['BTCUSDT Buy Price'] = np.nan
        TradeInfo['BTC Bought'] = np.nan
        TradeInfo['Sell Stop-Limit Id'] = np.nan
        TradeInfo['Sell Stop Price'] = np.nan
        TradeInfo['Sell Limit Price'] =np.nan
        TradeInfo['Close-BTC-Buy']=True
        print('---Sold '+str(ExecQty)+SetUp['trade']['pairTrade'])
        print('---for '+str(TradeInfo['Closed Buy Sell-Price'][0]*ExecQty)+'USDT')
        print('------------')
        print('---Profit: '+str(TradeInfo['Closed Buy Profit'][0]))
    elif order['status'] == 'PARTIALLY_FILLED':
        print('Stop Loss is getting filled...')
        print('--> do nothing for now...')
    elif any(order['status'] == s for s in ['NEW', 'CANCELED','REJECTED','EXPIRED','PENDING_CANCEL']):
        print('Stop loss status is '+order['status'])
        if order['status'] == 'NEW' or order['status'] == 'CANCELED':
            # Check if a stop loss update is needed (new>old)
            # Calculate Limit order value
            LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
            tmpstop = binFloat((1-float(stop))*LastPrice)
            tmplimit = binFloat((1-float(limit))*LastPrice)            
            if binFloat(TradeInfo['Sell Stop Price'][0]) < tmpstop:
                print('Updating order...')
                # Cancel Order and accordingly update currStopLossId
                if order['status'] != 'CANCELED':
                    cancelOut = client.cancel_order(
                        symbol=SetUp['trade']['pair'],
                        orderId=int(TradeInfo['Sell Stop-Limit Id'][0]))
                TradeInfo['Sell Stop-Limit Id'] = np.nan
                TradeInfo['Sell Stop Price'] = np.nan
                TradeInfo['Sell Limit Price'] =np.nan                    
                print('Order cancelled. Starting new order...')
                # Set new stop loss-limit
                TradeInfo['Update-SL-Sell'] =True
                TradeInfo= stopLimitSell(SetUp,TradeInfo,stop,limit)
            else:
                print('Keeping current Stop loss...')
    else:
        print('Error:could not update')
    return TradeInfo

def updateStopLimitBuy(SetUp,TradeInfo,stop,limit):
    # Need to think of double checking order book
    # Maybe another function?
    if TradeInfo['Buy Stop-Limit Id'][0] ==np.nan:
        print('No limit-buy order found...')
        print('--> No action taken')
        return TradeInfo
    
    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Check Order status
    order = client.get_order(
    symbol=SetUp['trade']['pair'],
    orderId=int(TradeInfo['Buy Stop-Limit Id'][0]))
    if order['status'] == 'FILLED':
        print('Limit buy has been hit')
        # Get last trade
        a=client.get_my_trades(symbol=SetUp['trade']['pair'],limit=1)
        a=a[0]
        # Gather trade data for the journal
        if a['commissionAsset']=='BNB':
            TradeInfo['Commission (BNB)'] =float(a['commission'])
        PriceBought=float(a['price'])
        ExecQty=float(a['qty'])
        TradeInfo['Closed Short Buy-Price'] =PriceBought
        TradeInfo['Closed Short Profit'] = a['realizedPnl'] 
        # Reset variables related to the closed trade
        acc=getBalance(SetUp)
        TradeInfo['Free Funds'] = acc['USDT']['wBalance']        
        TradeInfo['BTCUSDT Short Price'] = np.nan
        TradeInfo['BTC Shorted'] = np.nan
        TradeInfo['Close-BTC-Short'] = True
        TradeInfo['Buy Stop-Limit Id'] = np.nan
        TradeInfo['Buy Limit Price'] =np.nan
        TradeInfo['Buy Stop Price'] = np.nan                
    elif order['status'] == 'PARTIALLY_FILLED':
        print('Limit Order is getting filled')
        print('--> do nothing for now...')
    elif any(order['status'] == s for s in ['NEW', 'CANCELED','REJECTED','EXPIRED','PENDING_CANCEL']):
        if order['status'] == 'NEW' or order['status'] == 'CANCELED':
            # Check if a stop limit buy update is needed (new>old)
            LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
            tmpstop = binFloat((1+float(stop))*LastPrice)
            tmplimit = binFloat((1+float(limit))*LastPrice)            
            if binFloat(TradeInfo['Buy Stop Price'][0]) > tmpstop:            
                # Case where trailing stop is better than last one
                print('Updating order...')
                # Cancel Order and accordingly update Buy Stop-Limit Id
                if order['status'] != 'CANCELED':
                    # Cancel order
                    cancelOut = client.cancel_order(
                        symbol=SetUp['trade']['pair'],
                        orderId=int(TradeInfo['Buy Stop-Limit Id'][0])
                    )
                    print('Order cancelled. Starting new order...')
                # Reset related fields  
                TradeInfo['Buy Stop-Limit Id'] = np.nan
                TradeInfo['Buy Limit Price'] =np.nan
                TradeInfo['Buy Stop Price'] = np.nan      
                # Set new stop-limit-order       
                TradeInfo['Update-SL-Buy'] =True
                TradeInfo=stopLimitBuy(SetUp,TradeInfo,stop,limit)
            else:
                # Case where trailing stop is worse
                print('Keeping current limit-buy')
    else:
        print('Error:could not update')
    return TradeInfo        

