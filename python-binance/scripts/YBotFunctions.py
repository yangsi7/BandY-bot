#!/usr/bin/python3

import numpy as np
from datetime import datetime
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
import YBotFetchHistorical as fetchH
import YBotFetchRecent as fetchR

def initTradeFiles(SetUp):
    # Initialize or load trade Information (pickle)
    if not os.path.isfile(SetUp['paths']["TradeInfo"]+'.pkl'):
        CurrTradeInfo = {'CloseTimeStamp':None,"Signal":None,"action":[],
                'Funds':None,'chfBuy':None,'shareBuy':None,'chfShort':None,
                'shareShort':None,'currStopLoss':None,
                'currStopLossLimit':None,
                'currStopLossId':None,'currLimitStop':None,'currLimitLimit':None,
                'currLimitId':None,'BB':None, 'buyProfit':None,'shortProfit':None,
                'BNBcomm':0, 'shortId':None,'limitSell_i':0,'limitBuy_i':0}
        save_obj(CurrTradeInfo,SetUp['paths']["TradeInfo"])
    else:
        CurrTradeInfo = load_obj(SetUp['paths']["TradeInfo"])
    if not os.path.isfile(SetUp['paths']["Journal"]):
        # Write data to file
        listKeys=["CloseTimeStamp","Signal","action","Funds","chfBuy",
        "shareBuy","chfShort","shareShort","currStopLoss",
        "currStopLossLimit",'currStopLossId','currLimitStop',
        'currLimitLimit','currLimitId','BB','buyProfit','shortProfit','BNBcomm'
        'shortId', 'limitSell_i', 'limitBuy_i']
        writeOption = 'w'
        f = open(SetUp['paths']["Journal"], writeOption)
        wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
        wr.writerow(listKeys)
        f.close()
    return CurrTradeInfo

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

def csvreadEnd(csvfile):
 # Reads the last nrows of a csv file
    with open(csvfile,'r') as f:
        r=csv.reader(f,delimiter=',')
        row_count = sum(1 for row in r)
    with open(csvfile,'r') as f:
        r=csv.reader(f,delimiter=',')
        row=[];
        for i in range(row_count): # count from 0 to 7
            row.append(next(r))
    return row

def getJournal(SetUp):
    jJourn=csvreadEnd(SetUp['paths']['Journal'])[1:]
    JournFull=[[int(i[0])if i[0]!='' else None,
        eval(i[2]) if eval(i[2]) else None,
        float(i[3]),
        float(i[4]) if i[4]!='' else None,
        float(i[5]) if i[5]!='' else None,
        float(i[6]) if i[6]!='' else None,
        float(i[7]) if i[7]!='' else None,
        float(i[8]) if i[8]!='' else None,
        float(i[9]) if i[9]!='' else None,
        float(i[10]) if i[10]!='' else None,
        float(i[11]) if i[11]!='' else None,
        float(i[12]) if i[12]!='' else None,
        float(i[13]) if i[13]!='' else None,
        float(i[14]) if i[14]!='' else None,
        ] for i in jJourn]
    Journ={}
    Journ["time"]=[float(i[0]) for i in jJourn]
    Journ["signal"]=[float(i[1]) if i[1]!='' else None for i in jJourn]
#    Journ["action"]=[eval(i[2]) if eval(i[2]) else None for i in jJourn]
    Journ["Funds"]=[float(i[3]) for i in jJourn]
    Journ["chfBuy"]=[float(i[4]) if i[4]!='' else None for i in jJourn]
    Journ["shareBuy"]=[float(i[5]) if i[5]!='' else None for i in jJourn]
    Journ["chfShort"]=[float(i[6]) if i[6]!='' else None for i in jJourn]
    Journ["shareShort"]=[float(i[7]) if i[7]!='' else None for i in jJourn]
    Journ["currStopLoss"]=[float(i[8]) if i[8]!='' else None for i in jJourn]
    Journ["currStopLossLimit"]=[float(i[9]) if i[9]!='' else None for i in jJourn]
    Journ["currStopLossId"]=[int(i[10]) if i[10]!='' else None for i in jJourn]
    Journ["currLimitStop"]=[float(i[11]) if i[11]!='' else None for i in jJourn]
    Journ["currLimitLimit"]=[float(i[12]) if i[12]!='' else None for i in jJourn]
    Journ["currLimitId"]=[int(i[13]) if i[13]!='' else None for i in jJourn]
    Journ["BNBcomm"]=[float(i[14]) if i[14]!='' else None for i in jJourn]


    JournFields = [key for key in Journ.keys()]
    JournMa={}
    for ff in JournFields:
        JournMa[ff]=np.ma.masked_invalid(np.array(Journ[ff], dtype=float), copy=False)
    JournMa["Buys_idx"] = np.where(np.array([True if 'Buy' in i[2] else False for i in jJourn],dtype=bool))[0]
    JournMa["Shorts_idx"] = np.where(np.array([True if 'Short' in i[2] else False for i in jJourn],dtype=bool))[0]
    JournMa["SL_idx"] = np.where(np.array([True if 'Stop-limit-sell' in i[2] or 'Update stop-limit-sell' in i[2] else False for i in jJourn],dtype=bool))[0]
    JournMa["LO_idx"] = np.where(np.array([True if 'Stop-limit-buy' in i[2] or 'Update stop-limit-buy' in i[2] else False for i in jJourn],dtype=bool))[0]
    JournMa["BC_idx"] = np.where(np.array([True if 'buy-closed' in i[2] else False for i in jJourn] ,dtype=bool))[0]
    JournMa["SC_idx"] = np.where(np.array([True if 'short-closed' in i[2] else False for i in jJourn],dtype=bool))[0]

    return JournMa    

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

