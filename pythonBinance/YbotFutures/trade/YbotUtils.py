#!/usr/bin/python3

import sys
sys.path.append("..")
import numpy as np
from datetime import datetime
import pandas as pd
import matlab.engine
import pylab as plt
import sys
from mpl_finance import candlestick_ohlc
import csv
import os.path
import pickle
import time
import matlab.engine
import smtplib

from APIpyBinance.client_futures import Client
from . import fetchHistorical as fetchH

def initTradeFiles(SetUp):
    acc = getBalance(SetUp)    
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    if not os.path.isfile(SetUp['paths']["TradeInfo"]):
        toDf = {'Open timestmp':[np.nan],'Open dtime':[np.nan], 'Close timestmp':[np.nan],
            'Close dtime':[np.nan], 'timestmp':[int(time.time())], 'Signal':[np.nan],
            'Free Funds':[acc['USDT']['mBalance']],'Total Assets':[acc['wBalance']],
            'BTC Bought':[np.nan],'BTCUSDT Buy Price':[np.nan], 'LongOrderID':[np.nan],
            'LongOrderID1':[np.nan],'LongOrderID2':[np.nan], 'tp1':[np.nan], 'tp2':[np.nan],
            'BTC Shorted':[np.nan], 'BTCUSDT Short Price':[np.nan], 'ShortOrderID':[np.nan],
            'ShortOrderID1':[np.nan], 'ShortOrderID2':[np.nan], 'lTP1ID':[np.nan], 'lTP2ID':[np.nan],
            'lTPuID':[np.nan], 'sTP1ID':[np.nan], 'sTP2ID':[np.nan],'sTPuID':[np.nan],
            'BTC Borrowed Id':[np.nan], 'Sell Stop Price':[np.nan],'Sell Limit Price':[np.nan], 
            'ShortStopLossId':[np.nan], 'Buy Stop Price':[np.nan],'Buy Limit Price':[np.nan],
            'LongStopLossId':[np.nan], 'Closed Buy Sell-Price':[np.nan], 'CprlTP1':[np.nan], 'CprlTP2':[np.nan], 
            'CprlTPu':[np.nan],'CprsTP1':[np.nan], 'CprsTP2':[np.nan], 'CprsTPu':[np.nan],
            'Closed Short Buy-Price':[np.nan],'Closed Buy Profit':[np.nan], 'Closed Short Profit':[np.nan], 
            'Commission (BNB)':[np.nan], 'Buy-BTC':[False], 'Close-BTC-Buy':[False],'Short-BTC':[False], 
            'Close-BTC-Short':[False], 
            'Update-SL-Buy':[False], 'Update-SL-Sell':[False], 'BlSLh':[False],'BsSLh':[False],'BprlSL':[np.nan],
            'BprsSL':[np.nan],'BlO':[False],'BsO':[False],'BprlO':[np.nan],
            'BprsO':[np.nan],'Blprofit':[np.nan],'btclO':[np.nan],'btcsO':[np.nan],
            'Bsprofit':[np.nan], 'BlTP1h':[False], 'BlTP2h':[False],'BlTPuh':False,'BprlTP1h':[np.nan], 
            'BprlTP2h':[np.nan],'BprlPuh':[np.nan],
            'BsTP1h':[False], 'BsTP2h':[False],'BsTPuh':False,'BprsTP1h':[np.nan], 
            'BprsTP2h':[np.nan],'BprsPuh':[np.nan]}
        TradeInfo =  pd.DataFrame(toDf)    
        TradeInfo.to_csv(SetUp['paths']["TradeInfo"],index=False)
    else:
        TradeInfo = csvreadEnd(SetUp['paths']["TradeInfo"],1)
        TradeInfo['Free Funds'] = np.float(acc['USDT']['mBalance'])
        i=TradeInfo.columns.get_loc('Buy-BTC')
        ii=TradeInfo.columns.get_loc('Update-SL-Sell')
        TradeInfo.iloc[0,i:ii]=False

        # Cancel spurious Stop-Limit Sell orders
        if 0 < len(acc['openSellOrders']) < 2:
            if int(acc['openSellOrders'][0]['orderId']) != TradeInfo['LongStopLossId'][0]:
                TradeInfo['LongStopLossId'] = int(acc['openSellOrders'][0]['orderId'])
        elif len(acc['openSellOrders']) > 1:
            print('More than one Stop Sell Order... Keeping the latest one')
            ttimes = [i["time"] for i in acc['openSellOrders']]
            idx = ttimes.index(max(ttimes))
            for i in range(0,len(acc['openSellOrders'])):
                if i == idx:
                    continue
                cancelOut=client.cancel_order(
                    symbol=SetUp["trade"]["pair"],
                    orderId=acc['openSellOrders'][i]["orderId"])
        # Cancel spurious Stop-Limit Buy orders
        if 0 < len(acc['openBuyOrders']) < 2:
            if int(acc['openBuyOrders'][0]['orderId']) != TradeInfo['ShortStopLossId'][0]:
                TradeInfo['ShortStopLossId'] = int(acc['openBuyOrders'][0]['orderId'])
        elif len(acc['openBuyOrders']) > 1:
            print('More than one Stop Buy Order... Keeping the latest one')
            ttimes = [i["time"] for i in acc['openBuyOrders']]
            idx = ttimes.index(max(ttimes))
            for i in range(0,len(acc['openBuyOrders'])):
                if i == idx:
                    continue
                cancelOut=client.cancel_order(
                    symbol=SetUp["trade"]["pair"],
                    orderId=acc['openBuyOrders'][i]["orderId"])

        if acc['BTCUSDT']!={}:
            if acc['BTCUSDT']['side'] == 'SELL':
                TradeInfo['btcsO'] = acc['BTCUSDT']['iMarginPair']
                TradeInfo['BprsO'] = acc['BTCUSDT']['ePrice']
                TradeInfo['btclO'] = np.nan
                TradeInfo['BprlO'] = np.nan
            elif acc['BTCUSDT']['side'] == 'BUY':
                TradeInfo['btclO'] = acc['BTCUSDT']['iMarginPair']
                TradeInfo['BprlO'] = acc['BTCUSDT']['ePrice']
                TradeInfo['btcsO'] = np.nan
                TradeInfo['BprsO'] = np.nan


    return TradeInfo

def csvreadEnd(csvfile, nrows):
    readAll = pd.read_csv(csvfile)
    a = readAll.tail(nrows).reset_index(drop=True)
    return a

def appendToCsv(csvfile, TradeInfo):
        df = pd.read_csv(csvfile)
        df=df.append(TradeInfo, ignore_index = True,sort=False)
        df.drop_duplicates(subset='Close timestmp',keep='last',inplace=True)
        df.to_csv(csvfile,index=False)

def waitForTicker(SetUp,TradeInfo):
    x=datetime.today()
    y=x.replace(day=x.day, hour=x.hour, minute=59, second=30, microsecond=0)
    delta_t=y-x
    secs=delta_t.seconds+1
    secWakeUp=60 # Wake up this many seconds before
    minInterv=1
    secInterv=minInterv*60
    nInterval=int(max(0,(secs-secWakeUp)//secInterv))
    # Sleep and Wake up this one minute before
    print('* * * * Next ticker in about '+str(secs//60)+' minutes * * * *')
    print('---> Going to sleep')
    for tt in range(0,nInterval):
        time.sleep(secInterv)
    timeleft=(secs-secWakeUp-nInterval*secInterv)
    time.sleep(timeleft)

def fireSig(SetUp):
    # call matlab scripts 
    eng = matlab.engine.start_matlab()
    eng.addpath(SetUp["paths"]["matlab"])
    try:
        # Fire Buy/Short/Sell signals
        sig = eng.fireSig('rroot',SetUp["paths"]["rroot"],'Xwin',1)
        signal=sig
    except:
        print("Unexpected error:", sys.exc_info()[0])
    eng.quit()
    return signal

def plotBot(SetUp):
    # call matlab scripts 
    eng = matlab.engine.start_matlab()
    eng.addpath(SetUp["paths"]["matlab"])
    try:
        # Fire Buy/Short/Sell signals
        a = eng.plotBot()
    except:
        print("Unexpected error:", sys.exc_info()[0])
    eng.quit()

def CheckNew(SetUp,TradeInfo):
    NewTicker=False
    iter=0
    starttime=time.time()
    while time.time()-starttime < 240:
        iter=iter+1
        Tick = fetchH.main([
            '-pair', SetUp["trade"]["pair"],'-tickDt',SetUp["trade"]["tickDt"]])
        LastInfo=load_obj(SetUp['paths']["LastInfo"])

        if TradeInfo['Close timestmp'][0] == LastInfo['LastTimeStamp']:
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

def getBalance(SetUp):
    apiK = open(SetUp['paths']['secure'], 'r').read().split('\n')
    client = Client(apiK[0], apiK[1])
    acc = AutoVivification()
    a = client.get_account()
    acc['total']['wBalance']=float(a['totalWalletBalance'])
    acc['total']['mBalance']=float(a['totalMarginBalance'])
    acc['total']['uProfit']=float(a['totalUnrealizedProfit'])
    acc['total']['oMargin']=float(a['totalOpenOrderInitialMargin'])
    acc['total']['iMargin']=float(a['totalInitialMargin'])
    acc['total']['pMargin']=float(a['totalPositionInitialMargin'])

    for i in a['assets']:
        acc[i['asset']]['wBalance']=float(i['walletBalance'])
        acc[i['asset']]['mBalance']=float(i['marginBalance'])
        acc[i['asset']]['uProfit']=float(i['unrealizedProfit'])
        acc[i['asset']]['oMargin']=float(i['openOrderInitialMargin'])
        acc[i['asset']]['iMargin']=float(i['initialMargin'])
        acc[i['asset']]['pMargin']=float(i['positionInitialMargin'])

    b = client.get_positions()
    for i in b:
        if float(i['positionAmt'])==0:
            continue
        acc[i['symbol']]['iMarginUSDT']=float(i['entryPrice'])*abs(float(i['positionAmt']))
        acc[i['symbol']]['iMarginPair']=abs(float(i['positionAmt']))
        acc[i['symbol']]['side'] = 'SELL' if float(i['positionAmt']) < 0  else 'BUY'
        acc[i['symbol']]['ePrice']=float(i['entryPrice'])
        acc[i['symbol']]['uProfit']=float(i['unRealizedProfit'])
        acc[i['symbol']]['leverage']=float(i['leverage'])
        acc[i['symbol']]['cPrice']=float(i['entryPrice'])-float(i['unRealizedProfit'
            ])/acc[i['symbol']]['iMarginPair']

    nullAssets = list(set(list(acc.keys()))^set(['USDT','BTC','BNB','total']))
    for i in nullAssets:
        acc[i]['wBalance']=0
        acc[i]['mBalance']=0
        acc[i]['uProfit']=0
        acc[i]['oMargin']=0
        acc[i]['iMargin']=0
        acc[i]['pMargin']=0
    a = client.get_open_orders(symbol='BTCUSDT')
    acc['openSellOrders']=[i for i in a if i['side']=='SELL']
    acc['openBuyOrders']=[i for i in a if i['side']=='BUY']
    return acc

def getSig(SetUp,winHours):
    # call matlab scripts

    eng = matlab.engine.start_matlab()
    eng.addpath(SetUp["paths"]["matlab"])
    try:
        # Fire Buy/Short/Sell signals
#        signal = eng.fireSigForPython(matlab.double(rows),'model',SetUp["paths"]["model"])
        sig = eng.FireSignalWithBB('model',SetUp["paths"]["model"],'Xwin',winHours)
        signal=[float(i[0]) for i in sig]
        BB=[int(i[1]) for i in sig]
    except:
        print("Unexpected error:", sys.exc_info()[0])
    eng.quit()
    return signal,BB

def save_obj(obj, path):
    with open(path + '.pkl', 'wb') as f:
        pickle.dump(obj, f)

def load_obj(path):
    with open(path + '.pkl', 'rb') as f:
        return pickle.load(f)

class TickerStruct:
    pass

def binStr(amount):
    precision = 4
    if type(amount)==str:
        lenNum=len(str(int(round(binFloat(amount)))))
        amount=float(amount)
        precision = precision-lenNum
    else :
        lenNum=len(str(int(round(amount))))
        precision = precision-lenNum

        amt_str = "{:0.0{}f}".format(amount, precision)
    return amt_str

def binFloat(amount):
    precision = 4
    if type(amount)==str:
        lenNum=len(str(int(round(float(amount)))))
        amount=float(amount)
        precision = precision-lenNum
    else:
        lenNum=len(str(int(round(amount))))
        precision = precision-lenNum
    amt_float = float("{:0.0{}f}".format(amount, precision))
    return amt_float

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def sendEmail(TradeInfo):
    if not TradeInfo['Close-BTC-Buy'][0]  and not TradeInfo['Close-BTC-Short'][0
            ] and not TradeInfo['Buy-BTC'][0] and not TradeInfo['Short-BTC'][0]:
        return
    else:
        emailstr= '''..................................................................
Master Yang, I am  here to report.................\n'''
        if TradeInfo['Close-BTC-Buy'][0]:
            s='''......................................................................
--- Long position closed ---
    Sell price: {0} 
    Profit: {1} \n'''
            emailstr = emailstr + s.format(TradeInfo['Closed Buy Sell-Price'][0],
                    TradeInfo['Closed Buy Profit'][0])
        if TradeInfo['Close-BTC-Short'][0]:
            s = ''''......................................................................
--- Short position closed ---
    Buy price: {0}
    Profit: {1}\n'''
            emailstr = emailstr + s.format(TradeInfo['Closed Short Buy-Price']
                        [0],TradeInfo['Closed Short Profit'])
        if TradeInfo['Buy-BTC'][0]:
            s = '''......................................................................
--- Long position Opened ---
    Buy price: {0}\n'''
            emailstr = emailstr + s.format(TradeInfo['BTCUSDT Buy Price'][0])
        if TradeInfo['Short-BTC'][0]:
            s = '''......................................................................
--- Short position Opened ---
    Short price: {0}\n'''
            emailstr = emailstr + s.format(TradeInfo['BTCUSDT Short Price'][0])
        emailstr=emailstr+\
            '''..................................................................\n\n
....beep...beep...more...BTC...back to work...'''

    sent_from = 'yanginobot@gmail.com'
    to = ['simon.yang.ch@gmail.com']
    subject = 'Yangino: new trade'
    body = emailstr
    
    email_text = """\
    From: %s
    To: %s
    Subject: %s
    
    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login('yanginobot@gmail.com', 'agGPv88BpYkip3wytZX2Rkm6')
        server.sendmail(sent_from, to, email_text)
        server.close()
    except:
        print('Could not connect to gmail server...')
    

