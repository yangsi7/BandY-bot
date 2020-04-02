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
def TakeAction(TradeInfo,sig,SetUp,unconfirmed=0):
    signal = float(sig[0][0])
    if signal == 1:
        BBstr = 'bullish' 
    elif signal == -1:
        BBstr = 'bearish'
    else:
        BBstr = 'neutral'
    if unconfirmed==0 or BBstr!='neutral':
        print('-----')
        print('--- Market is *'+BBstr+'*.')
        print('-----')
        print('')
    
    TradeInfo = initTradeFiles(SetUp)
    act=0
    if unconfirmed==0:
        #-------------
        #--Close Long
        #-------------
        if not TradeInfo['btclO'].isnull()[0] and signal == -1:
            print('---Bearish!')
            print('------')
            print('---Closing all long position...')
            TradeInfo=closeAllOrders(SetUp,TradeInfo)
            act=1
        #-------------
        #--Close Short
        #-------------
        if not TradeInfo['btcsO'].isnull()[0] and signal == 1:
            print('---Bullish!')
            print('------')
            print('---Closing all short position...')
            TradeInfo=closeAllOrders(SetUp,TradeInfo)
            act=1
    #-------------
    #--Strategy 1 - with take profits
    #-------------
    if SetUp['strategy'] == 1:
        #-------------
        #--Check if SL or TPs were hit
        #-------------
        if not TradeInfo['btcsO'].isnull()[0]:
            TradeInfo=updateStopLoss(SetUp,TradeInfo,'BUY',0.1)
            TradeInfo=checkTakeProfit(SetUp,TradeInfo,'BUY')
            act=1

        if not TradeInfo['btclO'].isnull()[0]:
            TradeInfo=updateStopLoss(SetUp,TradeInfo,'SELL',0.1)
            TradeInfo=checkTakeProfit(SetUp,TradeInfo,'SELL')
            act=1
        #-------------
        #--Buy
        #-------------
        if TradeInfo['btclO'].isnull()[0] and signal == 1:
            print('---Bullish!')
            print('------')
            print('---Going long...')
            TradeInfo=putOrder(SetUp,TradeInfo,'BUY',tpBol=True)
            TradeInfo=stopLoss(SetUp,TradeInfo,'SELL',SetUp['trade']['Stop'])
            TradeInfo=takeProfit(SetUp,TradeInfo,'SELL')
            act=1
        #-------------
        #--Short
        #-------------
        if TradeInfo['btcsO'].isnull()[0] and  signal == -1: 
            print('---Bearish!')
            print('------')
            print('---Selling Short...')
            TradeInfo=putOrder(SetUp,TradeInfo,'SELL',tpBol=True)
            TradeInfo=stopLoss(SetUp,TradeInfo,'BUY',SetUp['trade']['Stop'])
            TradeInfo=takeProfit(SetUp,TradeInfo,'BUY')
            act=1

        if act==0:
            print('---No action taken')
    #-------------
    #--Strategy 2 - with dynamic SL
    #-------------
    elif SetUp['strategy'] == 2:
        # calculate dynamics stop loss
        lo = float(sig[0][1])
        up = float(sig[0][2])

        lsl = SetUp['trade']['lslBase'] + SetUp['trade'
                ]['slScale1']*(lo**SetUp['trade']['slScale2'])
        lsl = min(lsl,SetUp['trade']['slMax'])
        ssl = SetUp['trade']['sslBase'] + SetUp['trade'
                ]['slScale3']*(up**SetUp['trade']['slScale4'])
        ssl = min(ssl,SetUp['trade']['slMax'])
        
        if unconfirmed==0:
            dsl = 0
        else:
            dsl = 0.5
        
        #-------------
        #--Check if SL or TPs were hit
        #-------------
        if not TradeInfo['btcsO'].isnull()[0]:
            TradeInfo=updateStopLoss(SetUp,TradeInfo,'BUY',ssl+dsl,unconfirmed=unconfirmed)
            act=1

        if not TradeInfo['btclO'].isnull()[0]:
            act=1
            TradeInfo=updateStopLoss(SetUp,TradeInfo,'SELL',lsl+dsl,unconfirmed=unconfirmed)

                
        #-------------
        #--Buy
        #-------------
        if TradeInfo['btclO'].isnull()[0] and signal == 1:
            print('---Bullish!')
            print('------')
            print('---Going long...')
            TradeInfo=putOrder(SetUp,TradeInfo,'BUY')
            TradeInfo=stopLoss(SetUp,TradeInfo,'SELL',lsl)
            act=1
        #-------------
        #--Short
        #-------------
        elif TradeInfo['btcsO'].isnull()[0] and  signal == -1: 
            print('---Bearish!')
            print('------')
            print('---Selling Short...')
            TradeInfo=putOrder(SetUp,TradeInfo,'SELL')
            TradeInfo=stopLoss(SetUp,TradeInfo,'BUY',ssl)
            act=1

        if act==0:
            print('---No action taken')
       
    # Displaying last price 
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    print('Latest price: '+SetUp['trade']['pairTrade'] + '=' +str(LastPrice))

    # Sending email if anything happens
    #sendEmail(TradeInfo)

    # Write trade journal
    if act==1:
        LastInfo=load_obj(SetUp['paths']['LastInfo']) 
        TradeInfo['Close timestmp']=LastInfo['LastTimeStamp']
        TradeInfo['timestmp'] = int(time.time())
        TradeInfo['Signal'] = signal
        appendToCsv(SetUp['paths']['TradeInfo'],TradeInfo)
    plotBot(SetUp)
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
def putOrder(SetUp,TradeInfo,side):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    if side == 'BUY':
        TradeInfo['btclO'] = binFloat(TradeInfo['Free Funds'
            ][0]*SetUp['trade']['PercentFunds']/LastPrice*SetUp['trade']['Leverage'])
    elif side == 'SELL':
        TradeInfo['btcsO'] = binFloat(TradeInfo['Free Funds'
            ][0]*SetUp['trade']['PercentFunds']/LastPrice*SetUp['trade']['Leverage'])
    # Create a Long order
#    if tpBol:
#        qtytp1 = binFloat(TradeInfo['btclO'][0]*SetUp['trade']['ftp']
#            ) if side == 'BUY' else binFloat(TradeInfo['btcsO'][0]*SetUp['trade']['ftp'])
#        qtytp2 = binFloat(TradeInfo['btclO'][0]*(1-SetUp['trade']['ftp']
#            )) if side == 'BUY' else binFloat(TradeInfo['btcsO'][0]*(1-SetUp['trade']['ftp']))
#        tp1stop = binFloat(LastPrice*(SetUp['trade']['tp1']+1.0)
#            ) if side == 'BUY' else binFloat(LastPrice*(1.0 - SetUp['trade']['tp1'])) 
#        tp2stop = binFloat(LastPrice*(SetUp['trade']['tp2']+1.0)
#            ) if side == 'BUY' else binFloat(LastPrice*(1.0 - SetUp['trade']['tp2']))
#
#        ordertp1 = client.create_order(
#        symbol=SetUp['trade']['pair'],
#        side=side,
#        type='MARKET',
#        quantity=qtytp1,
#        )    
#        TradeInfo = checkMarketOrder(TradeInfo,SetUp,ordertp1,1)
#        ordertp2 = client.create_order(
#        symbol=SetUp['trade']['pair'],
#        side=side,
#        type='MARKET',
#        quantity=qtytp2,
#        )    
#        TradeInfo = checkMarketOrder(TradeInfo,SetUp,ordertp2,2)
#    else:
    qqty = binFloat(TradeInfo['btclO'][0]
            ) if side == 'BUY' else binFloat(TradeInfo['btcsO'][0])
    order = client.create_order(
    symbol=SetUp['trade']['pair'],
    side=side,
    type='MARKET',
    quantity=qqty,
    )    
    TradeInfo = checkMarketOrder(TradeInfo,SetUp,order,False)
    TradeInfo['BlO'] = True if side == 'BUY' else False
    TradeInfo['BsO'] = True if side == 'SELL' else False
    acc=getBalance(SetUp)
    TradeInfo['Free Funds'] = acc['USDT']['wBalance']
    return TradeInfo

def closeAllOrders(SetUp,TradeInfo):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    acc = getBalance(SetUp)
    if len(acc['openBuyOrders'])>0:
        for i in acc['openBuyOrders']:
            print('Closing open buy order ('+str(i['orderId'])+')')
            order = client.cancel_order(
                symbol=SetUp['trade']['pair'],
                orderId=i['orderId'])
    if len(acc['openSellOrders'])>0:
        for i in acc['openSellOrders']:
            print('Closing open sell order ('+str(i['orderId'])+')')
            order = client.cancel_order(
                symbol=SetUp['trade']['pair'],
                orderId=i['orderId'])
    # Calculate Stop loss value
    LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
    if not TradeInfo['btclO'].isnull()[0]:
        print('Closing long position ('+str(TradeInfo['btclO'][0])+')')
        qqty = binFloat(TradeInfo['btclO'][0])
        # Put in the order
        order = client.create_order(
        symbol=SetUp['trade']['pair'],
        side='SELL',
        type='MARKET',
        quantity=qqty,
        )
        TradeInfo['btclO'] = np.nan
        TradeInfo['BprlO'] = np.nan
        TradeInfo['BlSLh']=True

    if not TradeInfo['btcsO'].isnull()[0]:
        print('Closing short position ('+str(TradeInfo['btcsO'][0])+')')
        qqty = binFloat(TradeInfo['btcsO'][0])
        # Put in the order
        order = client.create_order(
        symbol=SetUp['trade']['pair'],
        side='BUY',
        type='MARKET',
        quantity=qqty,
        )
        TradeInfo['btcsO'] = np.nan
        TradeInfo['BprsO'] = np.nan
        TradeInfo['BsSLh']=True

    TradeInfo = initTradeFiles(SetUp)
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
        stopPrice = binFloat((1-float(stop))*LastPrice)
        limitPrice = binFloat((1-float(stop+limit))*LastPrice)
        TradeInfo['Sell Stop Price'] = stopPrice
        qqty = binFloat(TradeInfo['btclO'][0])
    elif side == 'BUY':
        stopPrice = binFloat((1+float(stop))*LastPrice)
        limitPrice = binFloat((1+float(stop-limit))*LastPrice)
        TradeInfo['Buy Stop Price'] = stopPrice
        qqty = binFloat(TradeInfo['btcsO'][0])

    # Put in the order
    order = client.create_order(
    symbol=SetUp['trade']['pair'],
    side=side,
    type='STOP_MARKET',
    reduceOnly = 'true',
    quantity=qqty,
    stopPrice=binFloat(stopPrice),
#    price=binFloat(limitPrice),
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
    if side == 'SELL':
        if not TradeInfo['lTP2ID'].isnull()[0] and not TradeInfo['lTP2ID'].isnull()[0]:
            print('TP1 order (Id='+str(TradeInfo['lTP1ID'][0])+
                ') and TP2 order (Id=' + str(TradeInfo['lTP2ID'][0])+') exists')
            print('No action taken')
            return TradeInfo
    elif side == 'BUY':
        if not TradeInfo['sTP2ID'].isnull()[0] and not TradeInfo['sTP2ID'].isnull()[0]:
            print('TP1 order (Id='+str(TradeInfo['sTP1ID'][0])+
                ') and TP2 order (Id=' + str(TradeInfo['sTP2ID'][0])+') exists')
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
        qtytp1 = binFloat(TradeInfo['btclO'][0]*SetUp['trade']['ftp'])
        qtytp2 = binFloat(TradeInfo['btclO'][0]*(1-SetUp['trade']['ftp']))
        tp1stop = binFloat(LastPrice*(1+stop1))
        tp2stop = binFloat(LastPrice*(1+stop2))
        tp1limit = binFloat(LastPrice*(1+limit1))
        tp2limit = binFloat(LastPrice*(1+limit2))
    else:
        qtytp1 = binFloat(TradeInfo['btcsO'][0]*SetUp['trade']['ftp'])
        qtytp2 = binFloat(TradeInfo['btcsO'][0]*(1-SetUp['trade']['ftp']))
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
    TradeInfo['lTP1ID'] =int(ordertp1['orderId']) if side == "SELL" else None
    TradeInfo['lTP2ID'] =int(ordertp2['orderId'])  if side == "SELL" else None
    TradeInfo['CprlTP1'] = tp1stop if side == "SELL" else None
    TradeInfo['CprlTP2'] = tp2stop if side == "SELL" else None

    TradeInfo['sTP1ID'] =int(ordertp1['orderId']) if side == "BUY" else None
    TradeInfo['sTP2ID'] =int(ordertp2['orderId'])  if side == "BUY" else None
    TradeInfo['CprsTP1'] = tp1stop if side == "SELL" else None
    TradeInfo['CprsTP2'] = tp2stop if side == "SELL" else None

    print('Initiated Take profit ('+side+') at: '+ SetUp['trade']['pairTrade'] + '=' + str(
        tp1stop)+'/'+str(tp2stop))
    return TradeInfo

def checkTakeProfit(SetUp,TradeInfo,side):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    tp1id = TradeInfo['lTP1ID'][0] if side == "SELL" else TradeInfo['sTP1ID'][0]
    tp2id = TradeInfo['lTP2ID'][0] if side == "SELL" else TradeInfo['sTP2ID'][0]
    if tp1id != None:
        ordertp1 = client.get_order(
        symbol=SetUp['trade']['pair'],
        orderId=int(tp1id)
        )
        if ordertp1['status'] == 'FILLED':
            print('TP1 was hit!')
            if side == "BUY":
                TradeInfo['BprsTP1h']=binFloat(ordertp1['avgPrice'])
                TradeInfo['BbtcsTP1h']=binFloat(ordertp1['executedQty'])
                TradeInfo['BsTP1h']=True
                TradeInfo['Bsprofit'] = SetUp['ftp']*TradeInfo['BprsO'][0]-TradeInfo['BprsTP1h'
                        ][0]*TradeInfo['BbtcsTP1h'][0]
                TradeInfo['sTP1ID'] = np.nan
                TradeInfo['CprsTP1'] = np.nan
                TradeInfo['btcsO'] = TradeInfo['btcsO']*(1-SetUp['ftp'])
                updateStopLoss(SetUp,TradeInfo,'BUY',SetUp['trade']['Stop'])
            elif side == "SELL":
                TradeInfo['BprlTP1h']=binFloat(ordertp1['avgPrice'])
                TradeInfo['BbtclTP1h']=binFloat(ordertp1['executedQty'])
                TradeInfo['BlTP1h']=True
                TradeInfo['Blprofit'] = TradeInfo['BprlTP1h']*TradeInfo['BbtclTP1h'
                        ][0] - SetUp['ftp']*TradeInfo['BprlO'][0]
                TradeInfo['btclO'] = TradeInfo['btclO']*(1-SetUp['ftp'])
                TradeInfo['lTP1ID'] = np.nan
                TradeInfo['CprlTP1'] = np.nan
                updateStopLoss(SetUp,TradeInfo,'SELL',SetUp['trade']['Stop'])
    if tp2id != None:
        ordertp2 = client.get_order(
        symbol=SetUp['trade']['pair'],
        orderId=int(tp2id)
        )
        if ordertp2['status'] == 'FILLED':
            print('TP2 was hit!')
            if side == "BUY":
                TradeInfo['BprsTP2h']=binFloat(ordertp2['avgPrice'])
                TradeInfo['BbtcsTP2h']=binFloat(ordertp2['executedQty'])
                TradeInfo['BsTP2h']=True
                TradeInfo['Bsprofit'] = TradeInfo['Bsprofit'][0] + (1-SetUp['ftp'
                    ])*TradeInfo['BprsO']-TradeInfo['BprsTP2h'][0]*TradeInfo['BbtcsTP2h'][0]
                TradeInfo['sTP2ID'] = np.nan
                TradeInfo['CprsTP2'] = np.nan
                cancelOut = client.cancel_order(
                    symbol=SetUp['trade']['pair'],
                    orderId=int(TradeInfo['ShortStopLossId'][0])
                    )
                TradeInfo['ShortStopLossId'] = np.nan
            elif side == "SELL":
                TradeInfo['BprlTP2h']=binFloat(ordertp2['avgPrice'])
                TradeInfo['BbtclTP2h']=binFloat(ordertp2['executedQty'])
                TradeInfo['BlTP2h']=True 
                TradeInfo['Blprofit'] = TradeInfo['Blprofit'][0] + TradeInfo['BprlTP2h'
                        ][0]*TradeInfo['BbtclTP2h'][0] - (1-SetUp['ftp'])*TradeInfo['BprlO'][0]
                TradeInfo['lTP2ID'] = np.nan
                TradeInfo['CprlTP2'] = np.nan
                TradeInfo['BprlO'] = np.nan
                TradeInfo['BbtclO'] = np.nan
                cancelOut = client.cancel_order(
                    symbol=SetUp['trade']['pair'],
                    orderId=int(TradeInfo['LongStopLossId'][0])
                    )
                TradeInfo['LongStopLossId'] = np.nan
        acc=getBalance(SetUp)
        TradeInfo['Free Funds'] = acc['USDT']['wBalance']
        print('TP1 and TP2 status is: '+ ordertp1['status']+'/'+ ordertp2['status'])
    return TradeInfo

def updateStopLoss(SetUp,TradeInfo,side,stop,unconfirmed=0):
    if TradeInfo['LongStopLossId'][0
            ] == np.nan or  TradeInfo['ShortStopLossId'][0] == np.nan:
        print('No stop loss found...')
        print('--> No action taken')
        return TradeInfo
    oppSide = 'SELL' if side == 'BUY' else 'BUY'
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
        if side == 'SELL':
            TradeInfo['Closed Buy Sell-Price'] =float(a['price'])
            ExecQty=float(a['qty'])
            TradeInfo['Closed Buy Profit'] = a['realizedPnl']
            acc=getBalance(SetUp)
            TradeInfo['Free Funds'] = acc['USDT']['wBalance']        
            TradeInfo['BprlO'] = np.nan
            TradeInfo['btclO'] = np.nan
            TradeInfo['LongStopLossId'] = np.nan
            TradeInfo['Sell Stop Price'] = np.nan
            TradeInfo['BlSLh']=True
        elif side == 'BUY':
            TradeInfo['Closed Short Sell-Price'] =float(a['price'])
            ExecQty=float(a['qty'])
            TradeInfo['Closed Short Profit'] = a['realizedPnl']
            acc=getBalance(SetUp)
            TradeInfo['Free Funds'] = acc['USDT']['wBalance']        
            TradeInfo['BprsO'] = np.nan
            TradeInfo['btcsO'] = np.nan
            TradeInfo['ShortStopLossId'] = np.nan
            TradeInfo['Sell Stop Price'] = np.nan
            TradeInfo['BsSLh']=True

        print('---' + side + ': ' + str(ExecQty) + SetUp['trade']['pairTrade'])
        print('---for '+str(float(a['price'])*ExecQty)+'USDT')
        print('------------')
        print('---Profit: '+str(a['realizedPnl']))
    elif order['status'] == 'PARTIALLY_FILLED':
        print('Stop Loss is getting filled...')
        print('--> do nothing for now...')
    elif any(order['status'] == s for s in ['NEW', 'CANCELED','REJECTED','EXPIRED','PENDING_CANCEL']):
        currstop = binFloat(TradeInfo['Buy Stop Price'][0]
            ) if side == 'BUY' else binFloat(TradeInfo['Sell Stop Price'][0])
        if unconfirmed == 0:
            originprice = TradeInfo['BprlO'][0] if side =='SELL' else TradeInfo['BprsO'][0]
            print('Stop loss status is '+ order['status']+' (Stop-loss '+side+': '
                +str(currstop)+' to close order '+oppSide+': '+str(originprice)+')')
        if order['status'] == 'NEW' or order['status'] == 'CANCELED':
            # Check if a stop loss update is needed (new>old)
            # Calculate Limit order value
            LastPrice=float(client.get_symbol_ticker(symbol=SetUp['trade']['pair'])['price'])
            tmpstop = binFloat((1+float(stop))*LastPrice
                    ) if side == 'BUY' else binFloat((1-float(stop))*LastPrice)
            if (currstop > tmpstop and side == 'BUY'
                ) or (currstop < tmpstop and side == 'SELL'):
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
                if unconfirmed == 0:
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
            TradeInfo['btclO'] = TradeInfo['btclO'][0]+binFloat(a['executedQty'])
        else:
            TradeInfo['btclO'] = binFloat(a['executedQty'])
        TradeInfo['BprlO'] = binFloat(LastPrice)
    else:
        if tp == 1:
            TradeInfo['ShortOrderID1'] = int(order['orderId'])
        elif tp == 2:
            TradeInfo['ShortOrderID2'] = int(order['orderId'])
        else:
            TradeInfo['ShortOrderID'] = int(order['orderId'])
        if tp == 2:
            TradeInfo['btcsO'] = TradeInfo['btcsO'][0] + binFloat(a['executedQty'])
        else:
            TradeInfo['btcsO'] = binFloat(a['executedQty'])
        TradeInfo['BprsO'] = binFloat(LastPrice)
    return TradeInfo 
