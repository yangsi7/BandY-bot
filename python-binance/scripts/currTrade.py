#!/usr/bin/env python

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
import fetch_historical
import fetch_recent
import time
import matlab.engine
import initBot as ini



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
    print('-----')
    print('---Hotness index is .......'+str(round(signal,2))+' and market is *'+BBstr+'*.')

    print('-----')
    print('')
    if (TradeInfo['currLimitId']==None and 
            TradeInfo['currStopLossId']==None and
            (0.2<signal < 0.8 or 
                (signal < 0.2 and (TradeInfo['shareBuy']!= None or BB == 0)) or
                (signal > 0.8 and (TradeInfo['shareShort'] != None or BB == 1)))):
        TradeInfo['action']=[]
        print('--> No action taken')
    #-------------
    #--Close Buy
    #-------------
    if TradeInfo['shareBuy'] != None and TradeInfo['currStopLoss']==None and signal>=0.8:
        print('---Index is getting cold!')
        print('------')
        print('---Setting a stop-limit to close the buy order...')
        print('')
        TradeInfo['action'].append('Stop=limit-sell')
        TradeInfo=stopLoss(SetUp,TradeInfo)
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
    #--Close short
    #-------------
    if TradeInfo['shareShort'] != None and TradeInfo['currLimitId']==None and signal<=0.2:
        print('---Index is getting hot!')
        print('------')
        print('---Setting a stop-limit to close the short order...')
        print('')
        TradeInfo['action'].append('Stop-limit-buy')
        TradeInfo=LimitOrder(SetUp,TradeInfo)
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
    #--Buy
    #-------------
    if TradeInfo['shareBuy'] == None and signal <= 0.2 and BB == 1:
        print('---BB is bullish and index is getting hot!')
        print('------')
        print('---Starting a buy order...')
        TradeInfo['action'].append('Buy')
        TradeInfo=buyOrder(SetUp,TradeInfo)
    #-------------
    #--Short
    #-------------
    if TradeInfo['shareShort'] == None and signal>=0.8 and BB == 0:
        print('---BB is bearish and Index is getting cold!')
        print('------')
        print('---Starting a short order...')
        TradeInfo['action'].append('Sell')
        TradeInfo=shortOrder(SetUp,TradeInfo)
    # Write trade journal
    LastInfo = load_obj(SetUp['paths']["LastInfo"])
    TradeInfo['CloseTimeStamp']=LastInfo['LastTimeStamp']
    TradeInfo['Signal']=signal
    TradeInfo['BB']=BB
    writeTradeJournal(TradeInfo,SetUp)
    return TradeInfo

def writeTradeJournal(TradeInfo,SetUp):
    # Initialize or load trade Information (pickle)
    if not os.path.isfile(SetUp['paths']["Journal"]):
        TradeInfo=initTradeFiles(SetUp)
    else:
        # Write data to file
        listKeys=["CloseTimeStamp","Signal","action","Funds","chfBuy",
                "shareBuy","chfShort","shareShort","currStopLoss",
                "currStopLossLimit",'currStopLossId','currLimitStop',
                'currLimitLimit','currLimitId',"BB","buyProfit","shortProfit",'BNBcomm']
        towrite=[TradeInfo[i] for i in listKeys]
        f = open(SetUp['paths']["Journal"], 'a')
        wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        wr.writerow(towrite)
        f.close()
    return TradeInfo

def initTradeFiles(SetUp):
    # Initialize or load trade Information (pickle)
    if not os.path.isfile(SetUp['paths']["TradeInfo"]+'.pkl'):
        CurrTradeInfo = {'CloseTimeStamp':None,"Signal":None,"action":[],
                'Funds':None,'chfBuy':None,'shareBuy':None,'chfShort':None,
                'shareShort':None, 'currStopLoss':None,'currStopLossLimit':None,
                'currStopLossId':None,'currLimitStop':None,'currLimitLimit':None,
                'currLimitId':None,'BB':None, 'buyProfit':None,'shortProfit':None,
                'BNBcomm':0}
        save_obj(CurrTradeInfo,SetUp['paths']["TradeInfo"])
    else:
        CurrTradeInfo = load_obj(SetUp['paths']["TradeInfo"])
    if not os.path.isfile(SetUp['paths']["Journal"]):
        # Write data to file
        listKeys=["CloseTimeStamp","Signal","action","Funds","chfBuy",
        "shareBuy","chfShort","shareShort","currStopLoss",
        "currStopLossLimit",'currStopLossId','currLimitStop',
        'currLimitLimit','currLimitId','BB','buyProfit','shortProfit','BNBcomm']
        writeOption = 'w'
        f = open(SetUp['paths']["Journal"], writeOption)
        wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        wr.writerow(listKeys)
        f.close()
    return CurrTradeInfo
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
    TradeInfo['shareBuy'] = float(a["qty"])
    TradeInfo['chfBuy'] = float(a["qty"])*float(a["price"])
    if a['commissionAsset']=='BNB':
        TradeInfo['BNBcomm']=TradeInfo['BNBcomm']+float(a['commission'])
        BTCcomm=0
    else:
        BTCcomm=float(a['commission'])
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
    maxloan=float(maxLoanDets['amount'])
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
        loanDets = client.get_margin_loan_details(asset='BTC', txId=TradeInfo['shortId'])
        loadStatus = loanDets['rows'][0]['status']
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
        TradeInfo['shareShort']=float(loanDets['rows'][0]['principal'])
        order = client.create_margin_order(
        symbol=SetUp["trade"]["pair"],
        side='SELL',
        type='MARKET',
        newOrderRespType='ACK',
        quantity=binFloat(TradeInfo['shareShort']))

    # Check order
    a=client.get_my_trades(symbol=SetUp["trade"]["pair"],limit=1)
    a=a[0]
    TradeInfo['shareShort'] = float(a["qty"])
    TradeInfo['chfShort'] = float(a["qty"])*float(a["price"])
    if a['commissionAsset']=='BNB':
        TradeInfo['BNBcomm']=TradeInfo['BNBcomm']+float(a['commission'])
        BTCcomm=0
    else:
        BTCcomm=float(a['commission'])
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
    TradeInfo['currStopLoss'] = binFloat((1-SetUp["trade"]["SLTresh"])*LastPrice)
    TradeInfo['currStopLossLimit'] = binFloat((1-SetUp["trade"]["SLlimit"])*LastPrice)

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
    TradeInfo['currLimitStop'] = (1+SetUp["trade"]["LOTresh"])*LastPrice
    TradeInfo['currLimitLimit'] = (1+SetUp["trade"]["LOlimit"])*LastPrice

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
        PriceSold=float(order['price'])
        ExecQty=float(order['executedQty'])
        TradeInfo['buyProfit'] = TradeInfo['chfBuy']-PriceSold*ExecQty
        TradeInfo['chfBuy'] = 0
        TradeInfo['shareBuy'] = 0
        TradeInfo['currStopLossId'] = None
        TradeInfo['currStopLoss'] = None
        TradeInfo['currStopLimit']=None
        print('---Sold '+str(ExecQty)+PairTrade)
        print('---for '+str(PriceSold*ExecQty)+PairRef)
        print('------------')
        print('---Profit: '+str(TradeInfo['buyProfit']))
    elif order['status'] == 'PARTIALLY_FILLED':
        if SetUp["trade"]["Slip"]*LastPrice < order['price']:
            print('Stop Loss-limit was missed !!!')
            tmpsell=float(order['origQty']-order[executedQty])
            if tmpsell>0:
                print('Selling remainder '+str(tmpsell)+
                        SetUp["trade"]["pair"]+' at market price')
                orderMS = client.order_market_sell(
                    symbol=SetUp["trade"]["pair"],
                    quantity=binFloat(tmpsell))
                Price1Sold=float(order['price'])
                Price2Sold=float(orderMS['price'])
                ExecQty1=float(order['executedQty'])
                ExecQty2=float(orderMS['executedQty'])
                TradeInfo['buyProfit'] = (TradeInfo['chfBuy']
                        -Price1Sold*ExecQty1 - Price2Sold*ExecQty2)
                TradeInfo['chfBuy'] = 0
                TradeInfo['shareBuy'] = 0
                TradeInfo['currStopLossId'] = None
                TradeInfo['currStopLoss'] = None
                TradeInfo['currStopLimit']=None
                print('---Sold '+str(ExecQty1+ExecQty2)+PairTrade)
                print('---for '+str(Price1Sold*ExecQty1+Price2Sold*ExecQty2)+PairRef)
                print('------------')
                print('---Profit: '+str(TradeInfo['buyProfit']))
            else:
                print('Tried to sell remainder but quantity='+str(quantity)+' is invalid...')
        else:
            print('Stop Loss is getting filled...')
            print('--> do nothing for now...')
    elif any(order['status'] == s for s in ['NEW', 'CANCELED','REJECTED','EXPIRED','PENDING_CANCEL']):
        print("Stop loss status is "+order['status'])
        if order['status'] == 'NEW':
            print('Updating order...')
            # Cancel Order and accordingly update currStopLossId
            cancelOut = client.cancel_order(
                    symbol=SetUp["trade"]["pair"],
                    orderId=TradeInfo['currStopLossId'])
            TradeInfo['currStopLossId']=None
            print('Order cancelled. Starting new order...')
            # Set new stop loss-limit
            TradeInfo= stopLoss(SetUp,TradeInfo)
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
        PriceBought=float(order['price'])
        ExecQty=float(order['executedQty'])

        #(2)
        loanDets=client.get_margin_account()
        Assets=loanDets['userAssets']
        loanToPay = float([i['borrowed'] for i in Assets if i['asset']==SetUp['trade']['pairTrade']][0])
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
            ToBuy=float(order2['executedQty'])*float(order2['price'])
            # (4)
            print('Transfering '+str(loanToPay)+SetUp["trade"]["pairTrade"]+' to margin account')
            transfer = client.transfer_spot_to_margin(asset=SetUp["trade"]["pairTrade"], amount=loanToPay)    
        else:
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
                # Update to buy for security
                ToBuy = -float(order2['executedQty'])*float(order2['price'])
        TradeInfo["Funds"]=TradeInfo["Funds"]-ToBuy

        #(5)
        transaction = client.repay_margin_loan(asset=SetUp["trade"]["pairTrade"], amount=binStr(loanToPay))
        status = client.get_margin_repay_details(
                asset=SetUp["trade"]["pairTrade"],
                txId=transaction['tranId'])
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
        if order['status'] == 'NEW':
            print('Updating order...')
            # Cancel Order and accordingly update currStopLossId
            # cancel order
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
        print('Error:could not update')
    return TradeInfo        

def unpackOrder(order):
    price=0
    qty=0
    comm=0
    for i in order['fills']:
        price = price + i['price']
        qty = qty + i['qty']
        comm= comm + i['comm']
    AdjPrice = Price-comm
    return AdjPrice,qty,comm

def save_obj(obj, path):
    with open(path + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(path):
    with open(path + '.pkl', 'rb') as f:
        return pickle.load(f)

def binStr(amount):
    precision = 5    
    if type(amount)==str:
        lenNum=len(str(int(round(float(amount)))))
        amount=float(amount)
        precision = precision-lenNum
    else :
        lenNum=len(str(int(round(amount))))
        precision = precision-lenNum

        amt_str = "{:0.0{}f}".format(amount, precision)
    return amt_str

def binFloat(amount):
    precision = 5
    if type(amount)==str:
        lenNum=len(str(int(round(float(amount)))))
        amount=float(amount)
        precision = precision-lenNum        
    else:
        lenNum=len(str(int(round(amount))))
        precision = precision-lenNum    
    amt_float = float("{:0.0{}f}".format(amount, precision))
    return amt_float
