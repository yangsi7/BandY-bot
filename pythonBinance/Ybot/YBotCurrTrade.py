#!/usr/bin/python3

"""Module summary
High level module built on top of python-binance

Exectute trades based on provided signals
    and current trade information.

"""

import numpy as np
import pandas as pd
from binance.client import Client
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
import YBotInit as ini 
from YBotFunctions import initTradeFiles,writeTradeJournal,\
        save_obj, load_obj, binFloat, binStr
from YBotFunctions import AutoVivification as av
import YBotFetchHistorical_WIP as fetchR

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
    print('-----')
    print('---Hotness index is .......'+str(round(signal,2))+' and market is *'+BBstr+'*.')

    print('-----')
    print('')
    if (TradeInfo['Buy Stop-Limit Id'].isnull()[0] and 
            TradeInfo['Sell Stop-Limit Id'].isnull()[0] and
            (SetUp['trade']['buySig']<signal < SetUp['trade']['shortSig'] or 
                (signal < SetUp['trade']['buySig'] and (not TradeInfo['BTC Bought'].isnull()[0] or BB == 0)) or
                (signal > SetUp['trade']['shortSig'] and (not TradeInfo['BTC Shorted'].isnull()[0] or BB == 1)))):
        print('--> No action taken')
    #-------------
    #--Update Stop-limit-sell
    #-------------
    if not TradeInfo['BTC Bought'].isnull()[0] and not TradeInfo['Sell Stop-Limit Id'].isnull()[0]:
        print('---Updating the existing stop-limit sell order...')
        print('')
        TradeInfo['action'].append('Update stop-limit-sell')
        TradeInfo=updateStopLoss(SetUp,TradeInfo)
    #-------------
    #--Update Stop-limit-buy
    #-------------
    if not TradeInfo['BTC Shorted'].isnull()[0] and not TradeInfo['Buy Stop-Limit Id'].isnull()[0]:
        print('---Updating the existing stop-limit buy order...')
        print('')
        TradeInfo=updateLimitOrder(SetUp,TradeInfo)
    #-------------
    #--Buy
    #-------------
    if TradeInfo['BTC Bought'].isnull()[0] and signal <= SetUp['trade']['buySig'] and BB == 1:
        print('---BB is bullish and index is getting hot!')
        print('------')
        print('---Starting a buy order...')
        TradeInfo=buyOrder(SetUp,TradeInfo)
        TradeInfo=stopLoss(SetUp,TradeInfo)
    #-------------
    #--Short
    #-------------
    if TradeInfo['BTC Shorted'].isnull()[0] and signal>=SetUp['trade']['shortSig'] and BB == 0:
        print('---BB is bearish and Index is getting cold!')
        print('------')
        print('---Starting a short order...')
        TradeInfo=shortOrder(SetUp,TradeInfo)
        TradeInfo=LimitOrder(SetUp,TradeInfo)
    # Write trade journal
    lrow=fetchR.main(['-pair', SetUp["trade"]["pair"],'-tickDt',SetUp["trade"]["tickDt"],'-tail','2'])
    
    TradeInfo['CloseTimeStamp']=LastInfo['LastTimeStamp']
    TradeInfo['timestmp'][0] = int(time.time())
    TradeInfo['Signal'][0] = signal
    TradeInfo['BB'][0] = BB    
    writeTradeJournal(TradeInfo,SetUp)
    return TradeInfo

 # # # # # # # # # 
# Market Buy order 
# ----------------
def buyOrder(SetUp,TradeInfo):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    tmp=client.get_ticker(symbol=SetUp['trade']['pair'])
    LastPrice=float(tmp['lastPrice'])
    TradeInfo['BTC Bought'][0] =binFloat(TradeInfo['Free Funds'][0]*SetUp['trade']['PercentFunds']/LastPrice)
    order = client.order_market_buy(
    symbol=SetUp['trade']['pair'],
    quantity=binStr(TradeInfo['BTC Bought'][0]),
    newOrderRespType='RESULT'
    )
    # Check order
    a=client.get_my_trades(symbol=SetUp['trade']['pair'],limit=1)
    a=a[0]
    TradeInfo['BTC Bought'][0] = binFloat(a['qty'])
    TradeInfo['BTCUSDT Buy Price'][0] = float(a['price'])
    if a['commissionAsset']=='BNB':
        TradeInfo['Commission (BNB)'][0]=float(a['commission'])
        BTCcomm=0
    else:
        BTCcomm=binFloat(a['commission'])
    TradeInfo['Buy-BTC'] = True
    TradeInfo['Free Funds'][0]=float(
            client.get_asset_balance(asset='USDT')['free'])
    return TradeInfo

 # # # # # # # 
# Market short  
# ------------
def shortOrder(SetUp,TradeInfo):
    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')        
    client = Client(apiK[0], apiK[1])

    # calculate ammount to short
    tmp=client.get_ticker(symbol=SetUp['trade']['pair'])
    LastPrice=float(tmp['lastPrice'])        
    USDTtoTransfer = binFloat(TradeInfo['Free Funds'][0]*SetUp['trade']['PercentFunds'])    
    TradeInfo['BTC Shorted'][0] = binFloat(USDTtoTransfer/LastPrice)
    
    # -Transfer funds as collateral 
    # -Check that ammount to short < max margin loan 
    # -Initiate loan
    transfer = client.transfer_spot_to_margin(asset=SetUp['trade']['pairRef'], amount=binStr(USDTtoTransfer))
    maxLoanDets = client.get_max_margin_loan(asset=SetUp['trade']['pairTrade'])
    maxloan=binFloat(maxLoanDets['amount'])
    if TradeInfo['BTC Shorted'][0] > maxloan:
        print('Max possible loan to small, increase margin account funds')
        return TradeInfo
    else:    
        TradeInfo['BTC Borrowed Id'][0] = client.create_margin_loan(
                asset=SetUp['trade']['pairTrade'], amount=binStr(
                    TradeInfo['BTC Shorted'][0]))['tranId']
    # Check Loan and wait for it to execute
    loadStatus='init'
    loanTry=0
    while loadStatus != 'CONFIRMED':
        loanTry=loanTry+1
        try:
            loanDets = client.get_margin_loan_details(asset='BTC', 
                    txId=TradeInfo['BTC Borrowed Id'][0])
            loadStatus = loanDets['rows'][0]['status']
        except:
            print('An exception occurred getting Loan details')    
        time.sleep(1)
        # if the loan failed, initiate again
        if loadStatus == 'FAILED':
            print('Loan failed, initiating new load')
            TradeInfo['BTC Borrowed Id'][0] = client.create_margin_loan(
                    asset=SetUp['trade']['pairTrade'], amount=binStr(
                        TradeInfo['BTC Shorted'][0]))['tranId']            
        # After 10 tries, abandon
        if loanTry == 10:
            print('Loan failed 10 times, breaking')
            break

    # Sell loan ammount at market price    
    if loadStatus == 'CONFIRMED':
        TradeInfo['BTC Shorted'][0]=binFloat(loanDets['rows'][0]['principal'])
        order = client.create_margin_order(
        symbol=SetUp['trade']['pair'],
        side='SELL',
        type='MARKET',
        newOrderRespType='ACK',
        quantity=binFloat(TradeInfo['BTC Shorted'][0]))

    # Check order
    a=client.get_my_trades(symbol=SetUp['trade']['pair'],limit=1)
    a=a[0]
    TradeInfo['BTC Shorted'][0] = float(a['qty'])
    TradeInfo['BTCUSDT Short Price'] = float(a['price'])
    if a['commissionAsset']=='BNB':
        TradeInfo['Commission (BNB)'][0]=float(a['commission'])
        BTCcomm=0
    else:
        BTCcomm=float(a['commission'])
    TradeInfo['Short-BTC'] = True    
    TradeInfo['Free Funds'][0]=float(
            client.get_asset_balance(asset='USDT')['free'])
    return TradeInfo        

def stopLoss(SetUp,TradeInfo):
    # use implicit Falsness of empty lists
    if not TradeInfo['Sell Stop-Limit Id'].isnull()[0]:
        print('Current stop loss (Id='+str(TradeInfo['Sell Stop-Limit Id'][0])+') exists')
        print('No action taken')
        return TradeInfo

    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Calculate Stop loss value
    tmp=client.get_ticker(symbol=SetUp['trade']['pair'])
    LastPrice=float(tmp['lastPrice'])
    if not TradeInfo['Update-SL-Sell'][0]:
        TradeInfo['Sell Stop Price'][0] = binFloat((1-SetUp['trade']['SLTreshIni'])*LastPrice)
        TradeInfo['Sell Limit Price'][0] = binFloat((1-SetUp['trade']['SLlimitIni'])*LastPrice)
    else:
        TradeInfo['Sell Stop Price'][0] = binFloat((1-SetUp['trade']['SLTresh'])*LastPrice)
        TradeInfo['Sell Limit Price'][0] = binFloat((1-SetUp['trade']['SLlimit'])*LastPrice)

    # Put in the order
    order = client.create_order(
    symbol=SetUp['trade']['pair'],
    side='SELL',
    type='STOP_LOSS_LIMIT',
    timeInForce='GTC',
    quantity=binFloat(TradeInfo['BTC Bought'][0]),
    stopPrice=binStr(TradeInfo['Sell Stop Price'][0]),
    price=binStr(TradeInfo['Sell Limit Price'][0])
    )

    TradeInfo['Sell Stop-Limit Id'][0]=order['orderId']     
    print('Initiated Stop loss limit at: '+ SetUp['trade']['pairTrade'] + '=' + str(
        TradeInfo['Sell Stop Price'][0])+'/'+str(TradeInfo['Sell Limit Price'][0]))
    print('Latest price: '+SetUp['trade']['pairTrade'] + '=' +str(LastPrice))

    return TradeInfo


def LimitOrder(SetUp,TradeInfo):
    # use implicit Falsness of empty lists
    if not TradeInfo['Buy Stop-Limit Id'].isnull()[0]:
        print('Current Limit Order (Id='+str(TradeInfo['Buy Stop-Limit Id'][0])+') exists')
        print('No action taken')
        return TradeInfo

    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Calculate Limit order value
    tmp=client.get_ticker(symbol=SetUp['trade']['pair'])
    LastPrice=float(tmp['lastPrice'])
    if not TradeInfo['Update-SL-Buy']:
        TradeInfo['Buy Stop Price'][0] = (1+SetUp['trade']['LOTreshIni'])*LastPrice
        TradeInfo['Buy Limit Price'][0] = (1+SetUp['trade']['LOlimitIni'])*LastPrice
    else:
        TradeInfo['Buy Stop Price'][0] = (1+SetUp['trade']['LOTresh'])*LastPrice
        TradeInfo['Buy Limit Price'][0] = (1+SetUp['trade']['LOlimit'])*LastPrice

    # Put in the order
    order = client.create_margin_order(
    symbol=SetUp['trade']['pair'],
    side='BUY',
    type='STOP_LOSS_LIMIT',
    timeInForce='GTC',
    quantity=binFloat(TradeInfo['BTC Shorted'][0]),
    stopPrice=binStr(TradeInfo['Buy Stop Price'][0]),
    price=binStr(TradeInfo['Buy Limit Price'][0])
    )

    TradeInfo['Buy Stop-Limit Id'][0]=order['orderId']
    print('Initiated stop-limit-buy order at: '+ SetUp['trade']['pairTrade'] + '=' + str(
        TradeInfo['Buy Stop Price'][0])+'/'+str(TradeInfo['Buy Limit Price'][0]))
    print('Latest price: '+SetUp['trade']['pairTrade'] + '=' +str(LastPrice))

    return TradeInfo

def updateStopLoss(SetUp,TradeInfo):
    if TradeInfo['Sell Stop-Limit Id'][0]==np.nan:
        print('No stop loss found...')
        print('--> No action taken')
        return TradeInfo
    
    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Check last price
    tmp=client.get_ticker(symbol=SetUp['trade']['pair'])
    LastPrice=float(tmp['lastPrice'])

    # Check Order status
    order = client.get_order(
    symbol=SetUp['trade']['pair'],
    orderId=TradeInfo['Sell Stop-Limit Id'][0])
    if order['status'] == 'FILLED':
        print('Stop loss has been hit')
        # Check order
        a=client.get_my_trades(symbol=SetUp['trade']['pair'],limit=1)
        a=a[0]
        if a['commissionAsset']=='BNB':
            TradeInfo['Commission (BNB)'][0]=float(a['commission'])
            BTCcomm=0
        else:
            BTCcomm=binFloat(a['commission'])

        TradeInfo['Closed Buy Sell-Price'][0]=float(a['price'])
        ExecQty=float(order['executedQty'])
        TradeInfo['Closed Buy Profit'][0] = -TradeInfo['BTC Bought'][0]*TradeInfo['BTCUSDT Buy Price'
                ][0] + PriceSold * ExecQty 
        TradeInfo['Free Funds'][0]=float(
            client.get_asset_balance(asset='USDT')['free'])        
        TradeInfo['BTCUSDT Buy Price'][0] = np.nan
        TradeInfo['BTC Bought'][0] = np.nan
        TradeInfo['Sell Stop-Limit Id'][0] = np.nan
        TradeInfo['Sell Stop Price'][0] = np.nan
        TradeInfo['Sell Limit Price'][0]=np.nan
        TradeInfo['Close-BTC-Buy']=True
        print('---Sold '+str(ExecQty)+SetUp['trade']['pairTrade'])
        print('---for '+str(PriceSold*ExecQty)+'USDT')
        print('------------')
        print('---Profit: '+str(TradeInfo['Closed Buy Profit'][0]))
    elif order['status'] == 'PARTIALLY_FILLED':
        if SetUp['trade']['Slip']*LastPrice < order['price']:
            print('Stop Loss-limit was missed !!!')
            tmpsell=binFloat(order['origQty']-order['executedQty'])
            if tmpsell>0:
                print('Selling remainder '+str(tmpsell)+
                        SetUp['trade']['pair']+' at market price')
                orderMS = client.order_market_sell(
                    symbol=SetUp['trade']['pair'],
                    quantity=binStr(tmpsell))
                Price1Sold=float(order['price'])
                Price2Sold=float(orderMS['price'])
                ExecQty1=float(order['executedQty'])
                ExecQty2=float(orderMS['executedQty'])
                TradeInfo['Closed Buy Profit'][0] = (-TradeInfo['BTC Bought'][0
                    ]*TradeInfo['BTCUSDT Buy Price'][0] + Price1Sold*ExecQty1 
                    + Price2Sold*ExecQty2)
                TradeInfo['Free Funds'][0]=float(
                    client.get_asset_balance(asset='USDT')['free'])
                TradeInfo['BTCUSDT Buy Price'][0] = np.nan
                TradeInfo['BTC Bought'][0] = np.nan
                TradeInfo['Sell Stop-Limit Id'][0] = np.nan
                TradeInfo['Sell Stop Price'][0] = np.nan
                TradeInfo['Close-BTC-Buy']=True     
                TradeInfo['Sell Limit Price'][0]=np.nan
                print('---Sold '+str(ExecQty1+ExecQty2)+SetUp['trade']['pairTrade'])
                print('---for '+str(Price1Sold*ExecQty1+Price2Sold*ExecQty2)+SetUp['trade']['pairTrade'])
                print('------------')
                print('---Profit: '+str(TradeInfo['Closed Buy Profit'][0]))
            else:
                print('Tried to sell remainder but quantity='+str(quantity)+' is invalid...')
        else:
            print('Stop Loss is getting filled...')
            print('--> do nothing for now...')
    elif any(order['status'] == s for s in ['NEW', 'CANCELED','REJECTED','EXPIRED','PENDING_CANCEL']):
        print('Stop loss status is '+order['status'])
        if order['status'] == 'NEW' or order['status'] == 'CANCELED':
            # Check if a stop loss update is needed (new>old)
            tmp=client.get_ticker(symbol=SetUp['trade']['pair'])
            LastPrice=float(tmp['lastPrice'])            
            tmpCurrStopLoss = binFloat((1-SetUp['trade']['SLTresh'])*LastPrice)
            tmpCurrStopLossLimit = binFloat((1-SetUp['trade']['SLlimit'])*LastPrice)
            if binFloat(TradeInfo['Sell Stop Price'][0]) < tmpCurrStopLoss:
                print('Updating order...')
                # Cancel Order and accordingly update currStopLossId
                if order['status'] != 'CANCELED':
                    cancelOut = client.cancel_order(
                        symbol=SetUp['trade']['pair'],
                        orderId=TradeInfo['Sell Stop-Limit Id'][0])
                TradeInfo['Sell Stop-Limit Id'][0] = np.nan
                TradeInfo['Sell Stop Price'][0] = np.nan
                TradeInfo['Sell Limit Price'][0]=np.nan                    
                print('Order cancelled. Starting new order...')
                # Set new stop loss-limit
                TradeInfo['Update-SL-Sell'][0]=True
                TradeInfo= stopLoss(SetUp,TradeInfo)
            else:
                print('Keeping current Stop loss...')
    else:
        print('Error:could not update')
    return TradeInfo

def updateLimitOrder(SetUp,TradeInfo):
    # Need to think of double checking order book
    # Maybe another function?
    if TradeInfo['Buy Stop-Limit Id'][0]==np.nan:
        print('No limit-buy order found...')
        print('--> No action taken')
        return TradeInfo
    
    # Open Binance client
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Check Order status
    order = client.get_margin_order(
    symbol=SetUp['trade']['pair'],
    orderId=TradeInfo['Buy Stop-Limit Id'][0])
    if order['status'] == 'FILLED':
        #(1) Get buy info
        #(2) Check if enough coins to pay back loan
        #(3) Buy up to load ammount if needed
        #(4) Transfer to margin account
        #(5) Repay loan

        #(1)
        print('Limit buy has been hit')
        PriceBought=float(order['price'])
        ExecQty=float(order['executedQty'])

        #(2)
        loanDetsAssets=client.get_margin_account()
        Assets=loanDetsAssets['userAssets']
        loanToPay = ([float(i['borrowed'])+float(i['interest']) 
            for i in Assets if i['asset']==SetUp['trade']['pairTrade']][0])
        print('Current loan   --' + str(loanToPay) + SetUp['trade']['pairTrade'])
        print('Closed short   --'+str(ExecQty)+SetUp['trade']['pairTrade']) 

        #(3)
        ToBuy = loanToPay-ExecQty
        if ExecQty < loanToPay:
            print('Buying '+str(ToBuy)+SetUp['trade']['pairTrade'])
            order2 = client.order_market_buy(
                    symbol=SetUp['trade']['pair'],
                    quantity=binStr(ToBuy)
                    )
            # Update to buy for security        
            ToBuy=float(order2['executedQty'])*float(order2['price'])
            # (4)
            print('Transfering '+str(ToBuy)+SetUp['trade']['pairTrade']+' to margin account')
            transfer = client.transfer_spot_to_margin(asset=SetUp['trade']['pairTrade'], amount=ToBuy)    
        #(5)
        transaction = client.repay_margin_loan(asset=SetUp['trade']['pairTrade'], amount=binStr(loanToPay))
        status = client.get_margin_repay_details(
                asset=SetUp['trade']['pairTrade'],
                txId=transaction['tranId'])
        # Make sure we don't go to fast, i.e., we want to get the status
        ss=0
        ii=0
        while ss:
            ii=ii+1
            try:
                if ii > 10:
                    break
                a=status['rows'][0]['status']
                ss=1
            except:
                print('Cannot get status')
                ss=0
        repayTry=0

        while status['rows'][0]['status'] == 'PENDING':
            repayTry=repayTry+1
            status = client.get_margin_repay_details(
                    asset=SetUp['trade']['pairTrade'],
                    txId=transaction['tranId'])
            time.sleep(10)
        if status['rows'][0]['status'] == 'FAILED':
            # Need to find better way to avoid errors
            print('Failed to repay -- need manual check')
        elif status['rows'][0]['status'] == 'CONFIRMED':
            print('Loan payed back successfully')
            # Selling remainding BTC if any is left
            if -ToBuy<0.001: # add variable here
                print('Difference to small to sell')
                ToBuy=0
            else:
                order2 = client.create_margin_order(
                        symbol=SetUp['trade']['pair'],
                        side='SELL',
                        type='MARKET',
                        quantity=binFloat(-ToBuy),
                        )
                acc=getBalance(SetUp)
                transfer = client.transfer_margin_to_spot(asset=SetUp['trade']['pairRef'], 
                        amount=acc['marg']['USDT']['free'])
                # Update to buy for security
            TradeInfo['Free Funds'][0]=float(
                    client.get_asset_balance(asset='USDT')['free'])
            TradeInfo['Closed Short Profit'][0] = TradeInfo['BTC Shorted']['BTCUSDT Short Price'
                    ] - PriceBought*ExecQty-ToBuy
            TradeInfo['BTCUSDT Short Price'] = np.nan
            TradeInfo['BTC Shorted'][0] = np.nan
            TradeInfo['Close-BTC-Short'] = True
            TradeInfo['Buy Stop-Limit Id'][0] = np.nan
            TradeInfo['Buy Limit Price'][0]=np.nan
            TradeInfo['Buy Stop Price'][0] = np.nan                
    elif order['status'] == 'PARTIALLY_FILLED':
        print('Limit Order is getting filled')
        print('--> do nothing for now...')
    elif any(order['status'] == s for s in ['NEW', 'CANCELED','REJECTED','EXPIRED','PENDING_CANCEL']):
        if order['status'] == 'NEW' or order['status'] == 'CANCELED':
            # Check if a stop limit buy update is needed (new>old)
            tmp=client.get_ticker(symbol=SetUp['trade']['pair'])
            LastPrice=float(tmp['lastPrice'])
            tmpCurrLimitStop = binFloat((1+SetUp['trade']['LOTresh'])*LastPrice)
            tmpCurrLimitLimit = binFloat((1+SetUp['trade']['LOlimit'])*LastPrice)
            if binFloat(TradeInfo['Buy Stop Price'][0]) > tmpCurrLimitStop:            
                print('Updating order...')
                # Cancel Order and accordingly update currStopLossId
                # cancel order
                if order['status'] != 'CANCELED':
                    cancelOut = client.cancel_margin_order(
                        symbol=SetUp['trade']['pair'],
                        orderId=TradeInfo['Buy Stop-Limit Id'][0]
                    )
                    print('Order cancelled. Starting new order...')
                TradeInfo['Buy Stop-Limit Id'][0] = np.nan
                TradeInfo['Buy Limit Price'][0]=np.nan
                TradeInfo['Buy Stop Price'][0] = np.nan      
                # Set new stop-limit-order       
                TradeInfo['Update-SL-Buy'][0]=True
                TradeInfo=LimitOrder(SetUp,TradeInfo)
            else:
                print('Keeping current limit-buy')
    else:
        print('Error:could not update')
    return TradeInfo        

def getBalance(SetUp):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])    
    acc = av() 
    acc['exch']['BTC']['free'] = float(
            client.get_asset_balance(asset='BTC')['free'])
    acc['exch']['BTC']['locked'] = float(
            client.get_asset_balance(asset='BTC')['locked'])
    acc['exch']['BTC']['total'] = acc[
            'exch']['BTC']['free'] + acc['exch']['BTC']['locked']  

    acc['exch']['USDT']['free'] = float(
            client.get_asset_balance(asset='USDT')['free'])
    acc['exch']['USDT']['locked'] = float(
            client.get_asset_balance(asset='USDT')['locked'])
    acc['exch']['USDT']['total'] = acc[
            'exch']['USDT']['free'] + acc['exch']['USDT']['locked']  

    acc['exch']['BNB']['free'] = float(
            client.get_asset_balance(asset='BNB')['free'])
    acc['exch']['BNB']['locked'] = float(
            client.get_asset_balance(asset='BNB')['locked'])
    acc['exch']['BNB']['total'] = acc[
            'exch']['BNB']['free'] + acc['exch']['BNB']['locked']  
    
    exchOpenOrders = client.get_open_orders(symbol='BTCUSDT')
    acc['exch']['openStopSell'] = [i for i in exchOpenOrders if i['type'
        ]=='STOP_LOSS_LIMIT' and i['side'] == 'SELL']
    acc['exch']['openLStopBuy'] = [i for i in exchOpenOrders if i['type'
        ]=='STOP_LOSS_LIMIT' and i['side'] == 'BUY']

    info = client.get_margin_account()
    acc['marg']['netAssetBTC']=info['totalNetAssetOfBtc']
    acc['marg']['totAssetBTC']=info['totalAssetOfBtc']
    acc['marg']['totBorrowedBTC']=info['totalLiabilityOfBtc']

    for i in info['userAssets']:
        if i['asset']=='BTC':
            acc['marg']['BTC']['free'] = float(i['free'])
            acc['marg']['BTC']['borrowed'] = float(i['borrowed'])
            acc['marg']['BTC']['interest'] = float(i['interest'])
            acc['marg']['BTC']['locked'] = float(i['free'])
            acc['marg']['BTC']['net'] = float(i['netAsset'])
            acc['marg']['BTC']['total'] = acc['marg']['BTC'
                    ]['free'] + acc['marg']['BTC']['locked']
        if i['asset']=='USDT':
            acc['marg']['USDT']['free'] = float(i['free'])
            acc['marg']['USDT']['borrowed'] = float(i['borrowed'])
            acc['marg']['USDT']['interest'] = float(i['interest'])
            acc['marg']['USDT']['locked'] = float(i['free'])
            acc['marg']['USDT']['net'] = float(i['netAsset'])
            acc['marg']['USDT']['total'] = acc['marg']['USDT'
                    ]['free'] + acc['marg']['USDT']['locked']
        if i['asset']=='BNB':
            acc['marg']['BNB']['free'] = float(i['free'])
            acc['marg']['BNB']['borrowed'] = float(i['borrowed'])
            acc['marg']['BNB']['interest'] = float(i['interest'])
            acc['marg']['BNB']['locked'] = float(i['free'])
            acc['marg']['BNB']['net'] = float(i['netAsset'])
            acc['marg']['BNB']['total'] = acc['marg']['BNB'
                    ]['free'] + acc['marg']['BNB']['locked']
    acc['marg']['openOrders'] = client.get_open_margin_orders(symbol='BTCUSDT')
    acc['Assets']['USDT'] = acc['exch']['USDT']['total'] + acc['marg']['USDT']['net']
    acc['Assets']['BTC'] = acc['exch']['BTC']['total'] + acc['marg']['BTC']['net']
    acc['Assets']['BNB'] = acc['exch']['BNB']['total'] + acc['marg']['BNB']['net']

    prices = client.get_all_tickers()
    BTCUSDT = float([i['price'] for i in prices if i['symbol'] == 'BTCUSDT'][0])
    BNBUSDT = float([i['price'] for i in prices if i['symbol'] == 'BNBUSDT'][0])
    BNBBTC = float([i['price'] for i in prices if i['symbol'] == 'BNBBTC'][0])

    acc['TotAssets']['inUSDT'] = acc['Assets']['USDT'] + acc['Assets']['BTC'
            ] * BTCUSDT + acc['Assets']['BNB'] * BNBUSDT
    acc['TotAssets']['inBTC'] = acc['Assets']['BTC'] + acc['Assets']['USDT'
            ] / BTCUSDT + acc['Assets']['BNB'] * BNBBTC

    return acc  

