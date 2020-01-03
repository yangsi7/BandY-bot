import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib
import matplotlib.ticker as ticker
import fetch_recent
import initBot as ini
import matlab.engine
import pylab as plt
from mpl_finance import candlestick_ohlc
import csv

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
