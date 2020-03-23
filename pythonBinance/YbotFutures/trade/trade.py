#!/usr/bin/python3

"""Module summary
High level module built on top of python-binance

Exectute trades based on provided signals
    and current trade information.

"""
import sys
sys.path.append("..")
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

from APIpyBinance.client_futures import Client
from . import params as ini 
from .YbotUtils import initTradeFiles,\
        save_obj, load_obj, binFloat, \
        sendEmail,binStr, getBalance, appendToCsv
from .YbotUtils import *
from .YbotUtils import AutoVivification as av
from . import fetchHistorical as fetchH

# Strategy done in matlab
def TakeAction(TradeInfo,signal,SetUp):
    if signal == 1:
        BBstr = 'bullish' 
    elif signal == -1:
        BBstr = 'bearish'
    else:
        BBstr = 'neutral'
    print('-----')
    print('--- Market is *'+BBstr+'*.')

    print('-----')
    print('')

    #-------------
    #--Buy
    #-------------
    if TradeInfo['BTC Bought'].isnull()[0] and signal == 1:
        print('---Bullish!')
        print('------')
        print('---Going long...')
        TradeInfo=putOrder(SetUp,TradeInfo,'BUY',tpBol=True)
        TradeInfo=stopLoss(SetUp,TradeInfo,'SELL',SetUp['trade']['Stop'])
        TradeInfo=takeProfit(SetUp,TradeInfo,'SELL')
    #-------------
    #--Short
    #-------------
    elif TradeInfo['BTC Shorted'].isnull()[0] and  signal == -1: 
        print('---Bearish!')
        print('------')
        print('---Selling Short...')
        TradeInfo=putOrder(SetUp,TradeInfo,'SELL',tpBol=True)
        TradeInfo=stopLoss(SetUp,TradeInfo,'BUY',SetUp['trade']['Stop'])
        TradeInfo=takeProfit(SetUp,TradeInfo,'BUY')
    #-------------
    #--Close Long
    #-------------
    elif not TradeInfo['BTC Bought'].isnull()[0] and signal == -1:
        print('---Bearish!')
        print('------')
        print('---Closing all long position...')
        TradeInfo=updateStopLoss(SetUp,TradeInfo,'SELL',SetUp['trade']['StopClose'])
    #-------------
    #--Close Short
    #-------------
    elif not TradeInfo['BTC Shorted'].isnull()[0] and signal == 1:
        print('---Bullish!')
        print('------')
        print('---Closing all short position...')
        TradeInfo=updateStopLoss(SetUp,TradeInfo,'BUY',SetUp['trade']['StopClose'])
    else:
        print('---No action taken')
       
    # Displaying last price 
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    print('Latest price: '+SetUp['trade']['pairTrade'] + '=' +str(LastPrice))

    # Sending email if anything happens
    #sendEmail(TradeInfo)

    # Write trade journal
    LastInfo=load_obj(SetUp['paths']['LastInfo']) 
    TradeInfo['Close timestmp']=LastInfo['LastTimeStamp']
    TradeInfo['timestmp'] = int(time.time())
    TradeInfo=putOrder(SetUp,TradeInfo,'SELL',tpBol=True)    
    TradeInfo['Signal'] = signal
    appendToCsv(SetUp['paths']['TradeInfo'],TradeInfo)
    return TradeInfo


def reset_account(SetUp,TradeInfo):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    acc = getBalance(SetUp)
    if len(acc['openBuyOrders'])>0:
        for i in acc['openBuyOrders']:
            order = client.cancel_order(
                symbol=SetUp['trade']['pair'],
                orderId=i['orderId'])
    if len(acc['openSellOrders'])>0:
        for i in acc['openSellOrders']:
           order = client.cancel_order(
                symbol=SetUp['trade']['pair'],
                orderId=i['orderId'])
        if acc['BTC']['wBalance'] > 0:
            order = client.create_order(
        	symbol=SetUp['trade']['pair'],
        	side='SELL',
        	type='MARKET',
        	quantity=binFLoat(acc['BTC']['wbalance']),
        	)
    TradeInfo = initTradeFiles(SetUp)


 # # # # # # # # # 
# Market Buy order 
# ----------------
def putOrder(SetUp,TradeInfo,side,tpBol=False):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    if side == 'BUY':
        TradeInfo['BTC Bought'] =binFloat(TradeInfo['Free Funds'
            ][0]*SetUp['trade']['PercentFunds']/LastPrice*SetUp['trade']['Leverage'])
    elif side == 'SELL':
        TradeInfo['BTC Shorted'] = binFloat(TradeInfo['Free Funds'
            ][0]*SetUp['trade']['PercentFunds']/LastPrice*SetUp['trade']['Leverage'])
    # Create a Long order
    if tpBol:
        qtytp1 = binFloat(TradeInfo['BTC Bought'][0]*SetUp['trade']['ftp']
            ) if side == 'BUY' else binFloat(TradeInfo['BTC Shorted'][0]*SetUp['trade']['ftp'])
        qtytp2 = binFloat(TradeInfo['BTC Bought'][0]*(1-SetUp['trade']['ftp']
            )) if side == 'BUY' else binFloat(TradeInfo['BTC Shorted'][0]*(1-SetUp['trade']['ftp']))
        tp1stop = binFloat(LastPrice*(SetUp['trade']['tp1']+1.0)
            ) if side == 'BUY' else binFloat(LastPrice*(1.0 - SetUp['trade']['tp1'])) 
        tp2stop = binFloat(LastPrice*(SetUp['trade']['tp2']+1.0)
            ) if side == 'BUY' else binFloat(LastPrice*(1.0 - SetUp['trade']['tp2']))

        ordertp1 = client.create_order(
        symbol=SetUp['trade']['pair'],
        side=side,
        type='MARKET',
        quantity=qtytp1,
        )    
        TradeInfo = checkMarketOrder(TradeInfo,SetUp,ordertp1,1)
        ordertp2 = client.create_order(
        symbol=SetUp['trade']['pair'],
        side=side,
        type='MARKET',
        quantity=qtytp2,
        )    
        TradeInfo = checkMarketOrder(TradeInfo,SetUp,ordertp2,2)
    else:
        qqty = binFloat(TradeInfo['BTC Bought'][0]
                ) if side == 'BUY' else binFloat(TradeInfo['BTC Shorted'][0])
        order = client.create_order(
        symbol=SetUp['trade']['pair'],
        side=side,
        type='MARKET',
        quantity=qqty,
        )    
        TradeInfo = checkMarketOrder(TradeInfo,SetUp,order,False)
    TradeInfo['Buy-BTC'] = True if side == 'BUY' else False
    TradeInfo['Short-BTC'] = True if side == 'SELL' else False
    acc=getBalance(SetUp)
    TradeInfo['Free Funds'] = acc['USDT']['wBalance']
    return TradeInfo

def stopLoss(SetUp,TradeInfo,side,stop):
    """  This submodule sets a stop loss order.

    Args:
        SetUp (dict): trading set-up set with SetUp = ini.initSetUp()
        TradeInfo (dict): Current state of trades
        side (str): side of transaction ('SELL' or 'BUY') 
        stop (float): fraction of price above or below current for the stop loss

    Returns:
        TradeInfo (dict): Current state of trades is updated
    """
    # Check arguments and raise exceptions if needed
    if side != 'SELL' and side != 'BUY':
        raise Exception('Error: set side to a valid value (SELL or BUY)')
        return TradeInfo

    if not TradeInfo['LongStopLossId'].isnull()[0] and side == 'SELL':
        print('Current stop loss (Id='+str(TradeInfo['LongStopLossId'][0])+') exists')
        print('No action taken')
        return TradeInfo
    elif not TradeInfo['ShortStopLossId'].isnull()[0] and side == 'BUY':
        print('Current stop loss (Id='+str(TradeInfo['ShortStopLossId'][0])+') exists')
        print('No action taken')
        return TradeInfo
    
    limit = SetUp["trade"]["Stoplimitadd"]

    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Calculate Stop loss value
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    if side == 'SELL':
        stopPrice = binFloat((1+float(stop))*LastPrice)
        limitPrice = binFloat((1+float(stop+limit))*LastPrice)
        TradeInfo['Sell Stop Price'] = stopPrice
        qqty = binFloat(TradeInfo['BTC Bought'][0])
    elif side == 'BUY':
        stopPrice = binFloat((1-float(stop+limit))*LastPrice)
        limitPrice = binFloat((1-float(stop-limit))*LastPrice)
        TradeInfo['Buy Stop Price'] = stopPrice
        qqty = binFloat(TradeInfo['BTC Shorted'][0])

    # Put in the order
    order = client.create_order(
    symbol=SetUp['trade']['pair'],
    side='SELL',
    type='STOP',
    timeInForce='GTC',
    reduceOnly = 'true',
    quantity=qqty,
    stopPrice=binFloat(stopPrice),
    price=binFloat(limitPrice),
    )

    if side == 'SELL':
        TradeInfo['LongStopLossId'] =int(order['orderId'])
    elif side == 'BUY':
        TradeInfo['ShortStopLossId'] =int(order['orderId'])
    print('Initiated Stop loss at: '+ SetUp['trade']['pairTrade'] + '=' + str(
        stopPrice))
    return TradeInfo



def takeProfit(SetUp,TradeInfo,side):
    # use implicit Falsness of empty lists
    if not TradeInfo['TP1ID'].isnull()[0] and not TradeInfo['TP2ID'].isnull()[0]:
        print('TP1 order (Id='+str(TradeInfo['TP1ID'][0])+
            ') and TP2 order (Id=' + str(TradeInfo['TP2ID'][0])+') exists')
        print('No action taken')
        return TradeInfo
    limit1 =  SetUp["trade"]["tp1"] - SetUp["trade"]["TPlimitadd"
            ] if side == 'BUY' else SetUp["trade"]["tp1"] + SetUp["trade"]["TPlimitadd"]
    limit2 =  SetUp["trade"]["tp2"] - SetUp["trade"]["TPlimitadd"
            ] if side == 'BUY' else SetUp["trade"]["tp2"] + SetUp["trade"]["TPlimitadd"]
    stop1 =  SetUp["trade"]["tp1"] if side == 'BUY' else SetUp["trade"]["tp1"] 
    stop2 =  SetUp["trade"]["tp2"] if side == 'BUY' else SetUp["trade"]["tp2"] 
    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Calculate Stop loss value
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    if side == 'SELL':
        qtytp1 = binFloat(TradeInfo['BTC Bought'][0]*SetUp['trade']['ftp'])
        qtytp2 = binFloat(TradeInfo['BTC Bought'][0]*(1-SetUp['trade']['ftp']))
        tp1stop = binFloat(LastPrice*(1+stop1))
        tp2stop = binFloat(LastPrice*(1+stop2))
        tp1limit = binFloat(LastPrice*(1+limit1))
        tp2limit = binFloat(LastPrice*(1+limit2))
    else:
        qtytp1 = binFloat(TradeInfo['BTC Shorted'][0]*SetUp['trade']['ftp'])
        qtytp2 = binFloat(TradeInfo['BTC Shorted'][0]*(1-SetUp['trade']['ftp']))
        tp1stop = binFloat(LastPrice*(1-stop1))
        tp2stop = binFloat(LastPrice*(1-stop2))
        tp1limit = binFloat(LastPrice*(1-limit1))
        tp2limit = binFloat(LastPrice*(1-limit2))

    ordertp1 = client.create_order(
    symbol=SetUp['trade']['pair'],
    side=side,
    type='TAKE_PROFIT',
    timeInForce='GTC',
    reduceOnly = 'true',
    quantity = qtytp1,
    stopPrice = tp1stop,
    price = tp1limit
    )    
    ordertp2 = client.create_order(
    symbol=SetUp['trade']['pair'],
    side=side,
    type='TAKE_PROFIT',
    timeInForce='GTC',
    reduceOnly = 'true',
    quantity = qtytp2,
    stopPrice = tp2stop,
    price = tp2limit
    )    
    TradeInfo['TP1Id'] =int(ordertp1['orderId'])
    TradeInfo['TP2Id'] =int(ordertp2['orderId'])
    TradeInfo['TP1Price'] = tp1stop
    TradeInfo['TP2Price'] = tp2stop
    print('Initiated Take profit ('+side+') at: '+ SetUp['trade']['pairTrade'] + '=' + str(
        TradeInfo['TP1Price'][0])+'/'+str(TradeInfo['TP2Price'][0]))
    return TradeInfo


def updateStopLoss(SetUp,TradeInfo,side,stop):
    if TradeInfo['LongStopLossId'][0
            ] == np.nan or  TradeInfo['ShortStopLossId'][0] == np.nan:
        print('No stop loss found...')
        print('--> No action taken')
        return TradeInfo
    
    orderId = TradeInfo['LongStopLossId'][0
            ] if side == 'SELL' else TradeInfo['ShortStopLossId'][0]
    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Check Order status
    order = client.get_order(
    symbol=SetUp['trade']['pair'],
    orderId=int(orderId)
    )
    if order['status'] == 'FILLED':
        print('Stop loss has been hit')
        # Check order
        a=client.get_my_trades(symbol=SetUp['trade']['pair'],limit=1)
        a=a[0]
        if a['commissionAsset']=='BNB':
            TradeInfo['Commission (BNB)'] =float(a['commission'])
        if side == 'BUY':
            TradeInfo['Closed Buy Sell-Price'] =float(a['price'])
            ExecQty=float(a['qty'])
            TradeInfo['Closed Buy Profit'] = a['realizedPnl']
            acc=getBalance(SetUp)
            TradeInfo['Free Funds'] = acc['USDT']['wBalance']        
            TradeInfo['BTCUSDT Buy Price'] = np.nan
            TradeInfo['BTC Bought'] = np.nan
            TradeInfo['LongStopLossId'] = np.nan
            TradeInfo['Sell Stop Price'] = np.nan
            TradeInfo['Close-BTC-Buy']=True
        elif side == 'SELL':
            TradeInfo['Closed Short Sell-Price'] =float(a['price'])
            ExecQty=float(a['qty'])
            TradeInfo['Closed Short Profit'] = a['realizedPnl']
            acc=getBalance(SetUp)
            TradeInfo['Free Funds'] = acc['USDT']['wBalance']        
            TradeInfo['BTCUSDT Short Price'] = np.nan
            TradeInfo['BTC Shorted'] = np.nan
            TradeInfo['ShortStopLossId'] = np.nan
            TradeInfo['Sell Stop Price'] = np.nan
            TradeInfo['Close-BTC-Short']=True

        print('---' + side + ': ' + str(ExecQty) + SetUp['trade']['pairTrade'])
        print('---for '+str(float(a['price'])*ExecQty)+'USDT')
        print('------------')
        print('---Profit: '+str(a['realizedPnl']))
    elif order['status'] == 'PARTIALLY_FILLED':
        print('Stop Loss is getting filled...')
        print('--> do nothing for now...')
    elif any(order['status'] == s for s in ['NEW', 'CANCELED','REJECTED','EXPIRED','PENDING_CANCEL']):
        print('Stop loss status is '+order['status'])
        if order['status'] == 'NEW' or order['status'] == 'CANCELED':
            # Check if a stop loss update is needed (new>old)
            # Calculate Limit order value
            LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
            tmpstop = binFloat((1+float(stop))*LastPrice
                    ) if side == 'BUY' else binFloat((1-float(stop))*LastPrice)
            currstop = binFloat(TradeInfo['Buy Stop Price'][0]
                ) if side == 'BUY' else binFloat(TradeInfo['Sell Stop Price'][0])
            if (currstop < tmpstop and side == 'BUY'
                ) or (currstop > tmpstop and side == 'SELL'):
                print('Updating stop loss...')
                # Cancel Order and accordingly update currStopLossId
                if order['status'] != 'CANCELED':
                    cancelOut = client.cancel_order(
                        symbol=SetUp['trade']['pair'],
                        orderId=int(orderId)
                        )
                if side == 'SELL': TradeInfo['LongStopLossId'] = np.nan
                if side == 'SELL': TradeInfo['Sell Stop Price'] = np.nan
                if side == 'BUY': TradeInfo['ShortStopLossId'] = np.nan
                if side == 'BUY': TradeInfo['Buy Stop Price'] = np.nan

                print('Stop loss cancelled. Starting new stop loss order...')
                # Set new stop loss
                TradeInfo['Update-SL-Sell'] =True if side == 'SELL' else False
                TradeInfo['Update-SL-Buy'] =True if side == 'BUY' else False
                TradeInfo= stopLoss(SetUp,TradeInfo,side,stop)
            else:
                print('Keeping current Stop loss...')
    else:
        print('Error:could not update')
    return TradeInfo

def checkMarketOrder(TradeInfo,SetUp,order,tp=False):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
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
    if a['side'] == 'BUY':
        if tp == 1:
            TradeInfo['LongOrderID1'] = int(order['orderId'])
        elif tp == 2:
            TradeInfo['LongOrderID2'] = int(order['orderId'])
        else:    
            TradeInfo['LongOrderID'] = int(order['orderId'])
            
        if tp == 2:
            TradeInfo['BTC Bought'] = TradeInfo['BTC Bought'][0]+binFloat(a['executedQty'])
        else:
            TradeInfo['BTC Bought'] = binFloat(a['executedQty'])
        TradeInfo['BTCUSDT Buy Price'] = binFloat(LastPrice)
    else:
        if tp == 1:
            TradeInfo['ShortOrderID1'] = int(order['orderId'])
        elif tp == 2:
            TradeInfo['ShortOrderID2'] = int(order['orderId'])
        else:
            TradeInfo['ShortOrderID'] = int(order['orderId'])
        if tp == 2:
            TradeInfo['BTC Shorted'] = TradeInfo['BTC Shorted'][0] + binFloat(a['executedQty'])
        else:
            TradeInfo['BTC Shorted'] = binFloat(a['executedQty'])
        TradeInfo['BTCUSDT Short Price'] = binFloat(LastPrice)
    return TradeInfo 
