#!/usr/bin/python3

"""Module summary
High level module built on top of python-binance

Exectute trades based on provided signals
    and current trade information.

"""


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
    BBstr = 'Bullish' if BB == 1 else 'Bearish'
    TradeInfo['action']=[]
    print('-----')
    print('---Hotness index is .......'+str(round(signal,2))+' and market is *'+BBstr+'*.')

    print('-----')
    print('')
    if (TradeInfo['currLimitId']==None and 
            TradeInfo['currStopLossId']==None and
            (SetUp["trade"]["buySig"]<signal < SetUp["trade"]["shortSig"] or 
                (signal < SetUp["trade"]["buySig"] and (TradeInfo['shareBuy']!= None or BB == 0)) or
                (signal > SetUp["trade"]["shortSig"] and (TradeInfo['shareShort'] != None or BB == 1)))):
        print('--> No action taken')
    #-------------
    #--Update Stop-limit-sell
    #-------------
    if TradeInfo['shareBuy'] != None and TradeInfo['currStopLossId']!=None:
        print('---Updating the existing stop-limit sell order...')
        print('')
        TradeInfo['action'].append('Update stop-limit-sell')
        TradeInfo=updateStopLoss(SetUp,TradeInfo)
        if TradeInfo['currStopLossId']==None:
            TradeInfo['action'].append('buy-closed')
    #-------------
    #--Close Buy
    #-------------
    if TradeInfo['shareBuy'] != None and TradeInfo['currStopLossId']==None and signal>=SetUp["trade"]["sellSig"]:
        print('---Index is getting cold!')
        print('------')
        print('---Setting a stop-limit to close the buy order...')
        print('')
        TradeInfo['action'].append('Stop-limit-sell')
        TradeInfo=stopLoss(SetUp,TradeInfo)
    #-------------
    #--Update Stop-limit-buy
    #-------------
    if TradeInfo['shareShort'] != None and TradeInfo['currLimitId']!=None:
        print('---Updating the existing stop-limit buy order...')
        print('')
        TradeInfo['action'].append('Update stop-limit-buy')
        TradeInfo=updateLimitOrder(SetUp,TradeInfo)
        if TradeInfo['currLimitId']==None:
            TradeInfo['action'].append('short-closed')        
    #-------------
    #--Close short
    #-------------
    if TradeInfo['shareShort'] != None and TradeInfo['currLimitId']==None and signal<=SetUp["trade"]["closeShortSig"]:
        print('---Index is getting hot!')
        print('------')
        print('---Setting a stop-limit to close the short order...')
        print('')
        TradeInfo['action'].append('Stop-limit-buy')
        TradeInfo=LimitOrder(SetUp,TradeInfo)
    #-------------
    #--Buy
    #-------------
    if TradeInfo['shareBuy'] == None and signal <= SetUp["trade"]["buySig"] and BB == 1:
        print('---BB is bullish and index is getting hot!')
        print('------')
        print('---Starting a buy order...')
        TradeInfo['action'].append('Buy')
        TradeInfo=buyOrder(SetUp,TradeInfo)
        TradeInfo=stopLoss(SetUp,TradeInfo)
    #-------------
    #--Short
    #-------------
    if TradeInfo['shareShort'] == None and signal>=SetUp["trade"]["shortSig"] and BB == 0:
        print('---BB is bearish and Index is getting cold!')
        print('------')
        print('---Starting a short order...')
        TradeInfo['action'].append('Short')
        TradeInfo=shortOrder(SetUp,TradeInfo)
        TradeInfo=LimitOrder(SetUp,TradeInfo)
    # Write trade journal
    TradeInfo=checkTradeInfo(TradeInfo,SetUp)
    LastInfo = load_obj(SetUp['paths']["LastInfo"])
    TradeInfo['CloseTimeStamp']=LastInfo['LastTimeStamp']
    TradeInfo['Signal']=signal
    TradeInfo['BB']=BB
    writeTradeJournal(TradeInfo,SetUp)
    return TradeInfo

 # # # # # # # # # 
# Market Buy order 
# ----------------
def buyOrder(SetUp,TradeInfo):
    apiK = open(SetUp["paths"]["secure"], "r").read().split('\n')
    client = Client(apiK[0], apiK[1])
    tmp=client.get_ticker(symbol=SetUp["trade"]["pair"])
    LastPrice=float(tmp['lastPrice'])
    TradeInfo['shareBuy'] =binFloat(TradeInfo["Funds"]*SetUp["trade"]["PercentFunds"]/LastPrice)
    TradeInfo['chfBuy'] = binFloat(TradeInfo["Funds"]*SetUp["trade"]["PercentFunds"])
    order = client.order_market_buy(
    symbol=SetUp["trade"]["pair"],
    quantity=binStr(TradeInfo['shareBuy']),
    newOrderRespType="RESULT"
    )
    # Check order
    a=client.get_my_trades(symbol=SetUp["trade"]["pair"],limit=1)
    a=a[0]
    TradeInfo['shareBuy'] = binFloat(a["qty"])
    TradeInfo['chfBuy'] = binFloat(a["qty"])*binFloat(a["price"])
    if a['commissionAsset']=='BNB':
        TradeInfo['BNBcomm']=TradeInfo['BNBcomm']+binFloat(a['commission'])
        BTCcomm=0
    else:
        BTCcomm=binFloat(a['commission'])
    TradeInfo['Funds']=TradeInfo['Funds']-TradeInfo['chfBuy']-BTCcomm
    return TradeInfo

 # # # # # # # 
# Market short  
# ------------
def shortOrder(SetUp,TradeInfo):
    # Open Binance client
    apiK = open(SetUp['paths']['secure'], "r").read().split('\n')        
    client = Client(apiK[0], apiK[1])

    # calculate ammount to short
    tmp=client.get_ticker(symbol=SetUp["trade"]["pair"])
    LastPrice=float(tmp['lastPrice'])        
    TradeInfo['shareShort'] = TradeInfo["Funds"]*SetUp["trade"]["PercentFunds"]/LastPrice
    TradeInfo['chfShort'] = TradeInfo["Funds"]*SetUp["trade"]["PercentFunds"]
    
    # -Transfer funds as collateral 
    # -Check that ammount to short < max margin loan 
    # -Initiate loan
    transfer = client.transfer_spot_to_margin(asset=SetUp["trade"]["pairRef"], amount=str(TradeInfo['chfShort']))
    maxLoanDets = client.get_max_margin_loan(asset=SetUp["trade"]["pairTrade"])
    maxloan=binFloat(maxLoanDets['amount'])
    if TradeInfo['shareShort'] > maxloan:
        print('Max possible loan to small, increase margin account funds')
        return TradeInfo
    else:    
        shortId = client.create_margin_loan(asset=SetUp["trade"]["pairTrade"], amount=binStr(TradeInfo['shareShort']))
        TradeInfo['shortId']=shortId['tranId']
    # Check Loan and wait for it to execute
    loadStatus='init'
    loanTry=0
    while loadStatus != 'CONFIRMED':
        loanTry=loanTry+1
        try:
            loanDets = client.get_margin_loan_details(asset='BTC', txId=TradeInfo['shortId'])
            loadStatus = loanDets['rows'][0]['status']
        except:
            print("An exception occurred getting Loan details")    
        time.sleep(1)
        # if the loan failed, initiate again
        if loadStatus == 'FAILED':
            print('Loan failed, initiating new load')
            shortId = client.create_margin_loan(asset=SetUp["trade"]["pairTrade"], amount=str(shareShort))
            TradeInfo['shortId']=shortId['tranId']
        # After 10 tries, abandon
        if loanTry == 10:
            print('Loan failed 10 times, breaking')
            break

    # Sell loan ammount at market price    
    if loadStatus == 'CONFIRMED':
        TradeInfo['shareShort']=binFloat(loanDets['rows'][0]['principal'])
        order = client.create_margin_order(
        symbol=SetUp["trade"]["pair"],
        side='SELL',
        type='MARKET',
        newOrderRespType='ACK',
        quantity=binFloat(TradeInfo['shareShort']))

    # Check order
    a=client.get_my_trades(symbol=SetUp["trade"]["pair"],limit=1)
    a=a[0]
    TradeInfo['shareShort'] = binFloat(a["qty"])
    TradeInfo['chfShort'] = binFloat(a["qty"])*binFloat(a["price"])
    if a['commissionAsset']=='BNB':
        TradeInfo['BNBcomm']=TradeInfo['BNBcomm']+binFloat(a['commission'])
        BTCcomm=0
    else:
        BTCcomm=binFloat(a['commission'])
    TradeInfo['Funds']=TradeInfo['Funds']+TradeInfo['chfShort']-BTCcomm
    return TradeInfo        

def stopLoss(SetUp,TradeInfo):
    # use implicit Falsness of empty lists
    if TradeInfo['currStopLossId'] != None:
        print('Current stop loss (Id='+str(TradeInfo['currStopLossId'])+') exists')
        print('No action taken')
        return TradeInfo

    # Open Binance client
    apiK = open(SetUp["paths"]["secure"], "r").read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Calculate Stop loss value
    tmp=client.get_ticker(symbol=SetUp["trade"]["pair"])
    LastPrice=float(tmp['lastPrice'])
    if TradeInfo['limitSell_i'] == 0:
        TradeInfo['currStopLoss'] = binFloat((1-SetUp["trade"]["SLTresh2"])*LastPrice)
        TradeInfo['currStopLossLimit'] = binFloat((1-SetUp["trade"]["SLlimit2"])*LastPrice)
    else:
        TradeInfo['currStopLoss'] = binFloat((1-SetUp["trade"]["SLTresh"])*LastPrice)
        TradeInfo['currStopLossLimit'] = binFloat((1-SetUp["trade"]["SLlimit"])*LastPrice)
    TradeInfo['limitSell_i'] = TradeInfo['limitSell_i'] + 1    

    # Put in the order
    order = client.create_order(
    symbol=SetUp["trade"]["pair"],
    side='SELL',
    type='STOP_LOSS_LIMIT',
    timeInForce='GTC',
    quantity=binFloat(TradeInfo['shareBuy']),
    stopPrice=binStr(TradeInfo['currStopLoss']),
    price=binStr(TradeInfo['currStopLossLimit'])
    )

    TradeInfo['currStopLossId']=order['orderId']     
    print('Initiated Stop loss limit at: '+ SetUp["trade"]["pairTrade"] + '=' + str(
        TradeInfo['currStopLoss'])+'/'+str(TradeInfo['currStopLossLimit']))
    print('Latest price: '+SetUp["trade"]["pairTrade"] + '=' +str(LastPrice))

    return TradeInfo


def LimitOrder(SetUp,TradeInfo):
    # use implicit Falsness of empty lists
    if TradeInfo['currLimitId']!=None:
        print('Current Limit Order (Id='+str(TradeInfo['currLimitId'])+') exists')
        print('No action taken')
        return TradeInfo
    # Open Binance client
    apiK = open(SetUp["paths"]["secure"], "r").read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Calculate Limit order value
    tmp=client.get_ticker(symbol=SetUp["trade"]["pair"])
    LastPrice=float(tmp['lastPrice'])
    if TradeInfo['limitBuy_i'] == 0:
        TradeInfo['currLimitStop'] = (1+SetUp["trade"]["LOTresh2"])*LastPrice
        TradeInfo['currLimitLimit'] = (1+SetUp["trade"]["LOlimit2"])*LastPrice
    else:
        TradeInfo['currLimitStop'] = (1+SetUp["trade"]["LOTresh"])*LastPrice
        TradeInfo['currLimitLimit'] = (1+SetUp["trade"]["LOlimit"])*LastPrice
    TradeInfo['limitBuy_i'] = TradeInfo['limitBuy_i'] + 1
    order = client.create_margin_order(
    symbol=SetUp["trade"]["pair"],
    side='BUY',
    type='STOP_LOSS_LIMIT',
    timeInForce='GTC',
    quantity=binFloat(TradeInfo['shareShort']),
    stopPrice=binStr(TradeInfo['currLimitStop']),
    price=binStr(TradeInfo['currLimitLimit'])
    )

    TradeInfo['currLimitId']=order['orderId']
    print('Initiated stop-limit-buy order at: '+ SetUp["trade"]["pairTrade"] + '=' + str(
        TradeInfo['currLimitStop'])+'/'+str(TradeInfo['currLimitLimit']))
    print('Latest price: '+SetUp["trade"]["pairTrade"] + '=' +str(LastPrice))

    return TradeInfo

def updateStopLoss(SetUp,TradeInfo):
    # use implicit Falsness of empty lists
    if TradeInfo['currStopLossId']==None:
        print('No stop loss found...')
        print('--> No action taken')
        return TradeInfo
    
    # Open Binance client
    apiK = open(SetUp["paths"]["secure"], "r").read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Check last price
    tmp=client.get_ticker(symbol=SetUp["trade"]["pair"])
    LastPrice=float(tmp['lastPrice'])

    # Check Order status
    order = client.get_order(
    symbol=SetUp["trade"]["pair"],
    orderId=TradeInfo['currStopLossId'])
    if order['status'] == 'FILLED':
        print('Stop loss has been hit')
        PriceSold=binFloat(order['price'])
        ExecQty=binFloat(order['executedQty'])
        TradeInfo['buyProfit'] = -TradeInfo['chfBuy']+PriceSold*ExecQty
        TradeInfo['Funds'] = TradeInfo['Funds'] + PriceSold*ExecQty
        TradeInfo['chfBuy'] = None
        TradeInfo['shareBuy'] = None
        TradeInfo['currStopLossId'] = None
        TradeInfo['currStopLoss'] = None
        TradeInfo['currStopLossLimit']=None
        print('---Sold '+str(ExecQty)+SetUp["trade"]["pairTrade"])
        print('---for '+str(PriceSold*ExecQty)+'USDT')
        print('------------')
        print('---Profit: '+str(TradeInfo['buyProfit']))
    elif order['status'] == 'PARTIALLY_FILLED':
        if SetUp["trade"]["Slip"]*LastPrice < order['price']:
            print('Stop Loss-limit was missed !!!')
            tmpsell=binFloat(order['origQty']-order[executedQty])
            if tmpsell>0:
                print('Selling remainder '+str(tmpsell)+
                        SetUp["trade"]["pair"]+' at market price')
                orderMS = client.order_market_sell(
                    symbol=SetUp["trade"]["pair"],
                    quantity=binFloat(tmpsell))
                Price1Sold=binFloat(order['price'])
                Price2Sold=binFloat(orderMS['price'])
                ExecQty1=binFloat(order['executedQty'])
                ExecQty2=binFloat(orderMS['executedQty'])
                TradeInfo['buyProfit'] = (-TradeInfo['chfBuy']
                        +Price1Sold*ExecQty1 + Price2Sold*ExecQty2)
                TradeInfo['Funds'] = (TradeInfo['Funds'] 
                        + Price1Sold*ExecQty1+Price2Sold*ExecQty2)
                TradeInfo['chfBuy'] = None
                TradeInfo['shareBuy'] = None
                TradeInfo['currStopLossId'] = None
                TradeInfo['currStopLoss'] = None
                TradeInfo['currStopLossLimit']=None
                print('---Sold '+str(ExecQty1+ExecQty2)+SetUp["trade"]["pairTrade"])
                print('---for '+str(Price1Sold*ExecQty1+Price2Sold*ExecQty2)+SetUp["trade"]["pairTrade"])
                print('------------')
                print('---Profit: '+str(TradeInfo['buyProfit']))
            else:
                print('Tried to sell remainder but quantity='+str(quantity)+' is invalid...')
        else:
            print('Stop Loss is getting filled...')
            print('--> do nothing for now...')
    elif any(order['status'] == s for s in ['NEW', 'CANCELED','REJECTED','EXPIRED','PENDING_CANCEL']):
        print("Stop loss status is "+order['status'])
        if order['status'] == 'NEW' or order['status'] == 'CANCELED':
            # Check if a stop loss update is needed (new>old)
            tmp=client.get_ticker(symbol=SetUp["trade"]["pair"])
            LastPrice=float(tmp['lastPrice'])            
            tmpCurrStopLoss = binFloat((1-SetUp["trade"]["SLTresh"])*LastPrice)
            tmpCurrStopLossLimit = binFloat((1-SetUp["trade"]["SLlimit"])*LastPrice)
            if binFloat(TradeInfo['currStopLoss']) < tmpCurrStopLoss:
                print('Updating order...')
                # Cancel Order and accordingly update currStopLossId
                if order['status'] != 'CANCELED':
                    cancelOut = client.cancel_order(
                        symbol=SetUp["trade"]["pair"],
                        orderId=TradeInfo['currStopLossId'])
                TradeInfo['currStopLossId']=None
                print('Order cancelled. Starting new order...')
                # Set new stop loss-limit
                TradeInfo= stopLoss(SetUp,TradeInfo)
            else:
                print('Keeping current Stop loss...')
    else:
        print('Error:could not update')
    return TradeInfo

def updateLimitOrder(SetUp,TradeInfo):
    # Need to think of double checking order book
    # Maybe another function?
    if TradeInfo['currLimitId']==None:
        print('No limit-buy order found...')
        print('--> No action taken')
        return TradeInfo
    
    # Open Binance client
    apiK = open(SetUp["paths"]["secure"], "r").read().split('\n')
    client = Client(apiK[0], apiK[1])

    # Check Order status
    order = client.get_margin_order(
    symbol=SetUp["trade"]["pair"],
    orderId=TradeInfo['currLimitId'])
    if order['status'] == 'FILLED':
        #(1) Get buy info
        #(2) Check if enough coins to pay back loan
        #(3) Buy up to load ammount if needed
        #(4) Transfer to margin account
        #(5) Repay loan

        #(1)
        print('Limit buy has been hit')
        PriceBought=binFloat(order['price'])
        ExecQty=binFloat(order['executedQty'])

        #(2)
        loanDetsAssets=client.get_margin_account()
        Assets=loanDetsAssets['userAssets']
        loanToPay = binFloat([i['borrowed'] for i in Assets if i['asset']==SetUp['trade']['pairTrade']][0])
        print('Current loan   --' + str(loanToPay) + SetUp['trade']['pairTrade'])
        print('Closed short   --'+str(ExecQty)+SetUp['trade']['pairTrade']) 

        #(3)
        ToBuy = loanToPay-ExecQty
        if ExecQty < loanToPay:
            print('Buying '+str(ToBuy)+SetUp['trade']['pairTrade'])
            order2 = client.order_market_buy(
                    symbol=SetUp["trade"]["pair"],
                    quantity=binFloat(ToBuy)
                    )
            # Update to buy for security        
            ToBuy=binFloat(order2['executedQty'])*binFloat(order2['price'])
            # (4)
            print('Transfering '+str(loanToPay)+SetUp["trade"]["pairTrade"]+' to margin account')
            transfer = client.transfer_spot_to_margin(asset=SetUp["trade"]["pairTrade"], amount=loanToPay)    
        else:
        #(5)
            transaction = client.repay_margin_loan(asset=SetUp["trade"]["pairTrade"], amount=binStr(loanToPay))
            status = client.get_margin_repay_details(
                    asset=SetUp["trade"]["pairTrade"],
                    txId=transaction['tranId'])
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
                    asset=SetUp["trade"]["pairTrade"],
                    txId=transaction['tranId'])
            time.sleep(10)
        if status['rows'][0]['status'] == 'FAILED':
            # Need to find better way to avoid errors
            print('Failed to repay -- need manual check')
        elif status['rows'][0]['status'] == 'CONFIRMED':
            print('Loan payed back successfully')
            if -ToBuy<0.001: # add variable here
                print('Difference to small to sell')
                ToBuy=0
            else:
                order2 = client.create_margin_order(
                        symbol=SetUp["trade"]["pair"],
                        side='SELL',
                        type='MARKET',
                        quantity=binFloat(-ToBuy),
                        )
                acc=getBalance(SetUp)
                transfer = client.transfer_margin_to_spot(asset=SetUp["trade"]["'pairRef'"], amount=acc['marg']['USDT']['free'])
                # Update to buy for security
                ToBuy = -binFloat(order2['executedQty'])*binFloat(order2['price'])
            TradeInfo["Funds"]=TradeInfo["Funds"]-ToBuy

            TradeInfo['shortProfit'] = TradeInfo['chfShort'] - PriceBought*ExecQty-ToBuy
            TradeInfo['chfShort'] = 0
            TradeInfo['shareShort'] = 0
            TradeInfo['currLimitId'] = None
            TradeInfo['currLimitLimit']=None
            TradeInfo['currLimitStop'] = None                
    elif order['status'] == 'PARTIALLY_FILLED':
        print('Limit Order is getting filled')
        print('--> do nothing for now...')
    elif any(order['status'] == s for s in ['NEW', 'CANCELED','REJECTED','EXPIRED','PENDING_CANCEL']):
        if order['status'] == 'NEW' or order['status'] == 'CANCELED':
            # Check if a stop limit buy update is needed (new>old)
            tmp=client.get_ticker(symbol=SetUp["trade"]["pair"])
            LastPrice=float(tmp['lastPrice'])
            tmpCurrLimitStop = binFloat((1+SetUp["trade"]["LOTresh"])*LastPrice)
            tmpCurrLimitLimit = binFloat((1+SetUp["trade"]["LOlimit"])*LastPrice)
            if binFloat(TradeInfo['currLimitStop']) > tmpCurrLimitStop:            
                print('Updating order...')
                # Cancel Order and accordingly update currStopLossId
                # cancel order
                if order['status'] != 'CANCELED':
                    cancelOut = client.cancel_margin_order(
                        symbol=SetUp["trade"]["pair"],
                        orderId=TradeInfo['currLimitId']
                    )
                    print('Order cancelled. Starting new order...')
                TradeInfo['currLimitId']=None
                TradeInfo['currLimitStop']=None
                TradeInfo['currLimitLimit']=None
                # Set new stop-limit-order       
                TradeInfo=LimitOrder(SetUp,TradeInfo)
            else:
                print('Keeping current limit-buy')
    else:
        print('Error:could not update')
    return TradeInfo        

def getBalance(SetUp):
    apiK = open(SetUp["paths"]["secure"], "r").read().split('\n')
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
    
    acc['exch']['openOrders'] = client.get_open_orders(symbol='BTCUSDT')
    
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
    return acc  

def checkTradeInfo(TradeInfo,SetUp):
        acc=getBalance(SetUp)
        if TradeInfo['Funds']!= acc['exch']['USDT']['free']:
            print('Inconsitent funds --> replace')
            TradeInfo['Funds']= acc['exch']['USDT']['free']
        if TradeInfo['shareBuy'] !=None: 
            if abs(TradeInfo['shareBuy'] - acc['exch']['BTC']['total']) > 1e-06 and acc['exch']['BTC']['total']> 1e-06:
                print('Inconsitent BTC --> replace')
                TradeInfo['shareBuy']= acc['exch']['BTC']['total']
        else:
            TradeInfo['shareBuy'] = None

        if acc['exch']['openOrders'] == []:
            TradeInfo['currStopLossId']=None
            TradeInfo['limitSell_i']=0
        if acc['marg']['openOrders'] == []:            
            TradeInfo['currLimitId']=None
            TradeInfo['limitBuy_i']=0


        return TradeInfo
