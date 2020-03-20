#!/usr/bin/python3

import numpy as np
from datetime import datetime
import pandas as pd
import matplotlib
import matplotlib.ticker as ticker
import matlab.engine
import pylab as plt
import sys
from mpl_finance import candlestick_ohlc
import csv
import os.path
import pickle
import time
import matlab.engine
import fetchHistorical as fetchH
from currTradeFutures import getBalance

def initTradeFiles(SetUp):
    acc = getBalance(SetUp)    
    if not os.path.isfile(SetUp['paths']["TradeInfo"]):
        toDf = {'Open timestmp':[np.nan],'Open dtime':[np.nan], 'Close timestmp':[np.nan],
            'Close dtime':[np.nan], 'timestmp':[int(time.time())], 'Signal':[np.nan], 'BB':[np.nan], 
            'Free Funds':[acc['USDT']['mbalance']],'Total Assets':[acc['wBalance']],
            'BTC Bought':[np.nan],'BTCUSDT Buy Price':[np.nan], 
            'BTC Shorted':[np.nan], 'BTCUSDT Short Price':[np.nan], 
            'BTC Borrowed Id':[np.nan], 'Sell Stop Price':[np.nan],'Sell Limit Price':[np.nan], 
            'Sell Stop-Limit Id':[np.nan], 'Buy Stop Price':[np.nan],'Buy Limit Price':[np.nan],
            'Buy Stop-Limit Id':[np.nan], 'Closed Buy Sell-Price':[np.nan], 
            'Closed Short Buy-Price':[np.nan],'Closed Buy Profit':[np.nan], 'Closed Short Profit':[np.nan], 
            'Commission (BNB)':[np.nan], 'Buy-BTC':[False], 'Close-BTC-Buy':[False],'Short-BTC':[False], 
            'Close-BTC-Short':[False], 'Update-SL-Buy':[False], 'Update-SL-Sell':[False]}
        TradeInfo =  pd.DataFrame(toDf)    
        TradeInfo.to_csv(SetUp['paths']["TradeInfo"])
    else:
        TradeInfo = csvreadEnd(SetUp['paths']["TradeInfo"],1)
        i=TradeInfo.columns.get_loc('Buy-BTC')
        ii=TradeInfo.columns.get_loc('Update-SL-Sell')
        TradeInfo.iloc[0,i:ii]=False

        # Cancel spurious Stop-Limit Sell orders
        if 0 < len(acc['exch']['openStopSell']) < 2:
            if int(acc['exch']['openStopSell'][0]["orderId"]) != int(TradeInfo['Sell Stop-Limit Id']):
                TradeInfo['Sell Stop-Limit Id'] = int(acc['exch']['openStopSell'][0]["orderId"])
        elif len(acc['exch']['openStopSell']) > 1:
            print('More than one Stop Sell Order... Keeping the latest one')
            ttimes = [i["time"] for i in acc['exch']['openStopSell']]
            idx = ttimes.index(max(ttimes))
            for i in range(0,len(acc['exch']['openStopSell'])):
                if i == idx:
                    continue
                cancelOut=client.cancel_order(
                    symbol=SetUp["trade"]["pair"],
                    orderId=acc['exch']['openStopSell'][i]["orderId"])
        # Cancel spurious Stop-Limit Buy orders
        if 0 < len(acc['marg']['openStopBuy']) < 2:
            if int(acc['marg']['openStopBuy'][0]["orderId"]) != int(TradeInfo['Buy Stop-Limit Id']):
                TradeInfo['Buy Stop-Limit Id'] = int(acc['marg']['openStopBuy'][0]["orderId"])
        elif len(acc['marg']['openStopBuy']) > 1:
            print('More than one Stop Buy Order... Keeping the latest one')
            ttimes = [i["time"] for i in acc['marg']['openStopBuy']]
            idx = ttimes.index(max(ttimes))
            for i in range(0,len(acc['marg']['openStopBuy'])):
                if i == idx:
                    continue
                cancelOut=client.cancel_margin_order(
                    symbol=SetUp["trade"]["pair"],
                    orderId=acc['marg']['openStopBuy'][i]["orderId"])
    return TradeInfo

def appendToCsv(csvfile, TradeInfo):
        df = pd.read_csv(csvfile)
        df.append(TradeInfo, ignore_index = True)
        df.drop_duplicates(subset='Close timestmp',keep='last',inplace=True)
        df.to_csv(csvfile)

def csvreadEnd(csvfile, nrows):
    top = pd.read_csv(csvfile, nrows=1)
    headers = top.columns.values
 # Reads the last nrows of a csv file
    with open(csvfile,'r') as f:
        r=csv.reader(f,delimiter=',')
        row_count = sum(1 for row in r)
    with open(csvfile,'r') as f:
        r=csv.reader(f,delimiter=',')
        row=[];
        for i in range(row_count): # count from 0 to 7
            if i < row_count-nrows:
                next(r)     # and discard the rows
            else:
                row.append(next(r))
    a=pd.DataFrame(row,columns=headers)

    return a

def writeTradeJournal(TradeInfo,SetUp):
    # Initialize or load trade Information (pickle)
    if not os.path.isfile(SetUp['paths']["Journal"]):
        TradeInfo=initTradeFiles(SetUp)
    else:
        # Write data to file
        listKeys=["CloseTimeStamp","Signal","action","Funds","chfBuy",
                "shareBuy","chfShort","shareShort","currStopLoss",
                "currStopLossLimit",'currStopLossId','currLimitStop',
                'currLimitLimit','currLimitId',"BB","buyProfit","shortProfit",
                'BNBcomm',"shortId",'limitSell_i','limitBuy_i']
        towrite=[TradeInfo[i] for i in listKeys]
        f = open(SetUp['paths']["Journal"], 'a')
        wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        wr.writerow(towrite)
        f.close()
    return TradeInfo

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
#    nrows = int(eng.getMaxWinForPython('model',SetUp["paths"]["model"]))
#    rows = fetch_recent.main(SetUp,['-window',str(nrows+1)])
#    rows = [[float(i) for i in j] for j in rows]
    try:
        # Fire Buy/Short/Sell signals
#        signal = eng.fireSigForPython(matlab.double(rows),'model',SetUp["paths"]["model"])
        sig = eng.FireSignalWithBB('rroot',SetUp["paths"]["rroot"],'model',SetUp["paths"]["model"])
        signal=float(sig[0][0])
        BB=int(sig[0][1])
    except:
        print("Unexpected error:", sys.exc_info()[0])
    eng.quit()
    return signal,BB

def CheckNew(SetUp,TradeInfo):
    NewTicker=False
    iter=0
    starttime=time.time()
    while time.time()-starttime < 240:
        iter=iter+1
        Tick = fetchH.main([
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
    precision = 5
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

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

