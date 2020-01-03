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

def plotAr(Toplot):
    ToplotAr={}
    ToPlotFar={}
    for i in ['Buys_time','Buys_chf', 'Shorts_time','Short_chf','Buys_share','Short_share']:
        ToplotAr[i]=np.array(Toplot[i],dtype=np.float32)
    ToplotAr['SL_time'] =[Toplot['SL_time'][-1] if Toplot['SL_time'] else None][0]
    ToplotAr['SL']=[Toplot['currStopLoss'][-1] if Toplot['currStopLoss'] else None][0]
    ToplotAr['SLL']=[Toplot['currStopLossLimit'][-1] if Toplot['currStopLossLimit'] else None][0]
    ToplotAr['LO_time'] =[Toplot['LO_time'][-1] if Toplot['LO_time'] else None][0]
    ToplotAr['LO']=[Toplot['currLimit'][-1] if Toplot['currLimit'] else  None][0]
    ToplotAr['LOL']=[Toplot['currLimitLimit'][-1] if Toplot['currLimitLimit'] else None][0]
    ToplotAr['SC_time']=[Toplot['SC_time'][-1] if Toplot['SC_time'] else None][0]
    ToplotAr['BC_time']=[Toplot['BC_time'][-1] if Toplot['BC_time'] else None][0]
    if ToplotAr['SC_time'] != None and ToplotAr['LO_time'] != None:
        if ToplotAr['SC_time'][-1] > ToplotAr['LO_time']:
            ToplotAr['LO_time']=None
            ToplotAr['LO']=None
            ToplotAr['LOL']=None
    if ToplotAr['BC_time'] != None and ToplotAr['SL_time'] != None:
        if ToplotAr['BC_time'][-1] > ToplotAr['SL_time']:
            ToplotAr['SL_time']=None
            ToplotAr['SL']=None
            ToplotAr['SLL']=None
    return ToplotAr

def getSig(SetUp,jJourn,winHours):
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
    Journ["action"]=[eval(i[2]) if eval(i[2]) else None for i in jJourn]
    Journ["Funds"]=[float(i[3]) for i in jJourn]
    Journ["chfBuy"]=[float(i[4]) if i[4]!='' else None for i in jJourn]
    Journ["shareBuy"]=[float(i[5]) if i[5]!='' else None for i in jJourn]
    Journ["chfShort"]=[float(i[6]) if i[6]!='' else None for i in jJourn]
    Journ["shareShort"]=[float(i[7]) if i[7]!='' else None for i in jJourn]
    Journ["currStopLoss"]=[float(i[8]) if i[8]!='' else None for i in jJourn]
    Journ["currStopLossLimit"]=[float(i[9]) if i[9]!='' else None for i in jJourn]
    Journ["currStopLossId"]=[float(i[10]) if i[10]!='' else None for i in jJourn]
    Journ["currLimitStop"]=[float(i[11]) if i[11]!='' else None for i in jJourn]
    Journ["currLimitLimit"]=[float(i[12]) if i[12]!='' else None for i in jJourn]
    Journ["currLimitId"]=[float(i[13]) if i[13]!='' else None for i in jJourn]
    Journ["BNBcomm"]=[float(i[14]) if i[14]!='' else None for i in jJourn]
    Toplot={}
    Toplot["time"] = np.array([i[0] for i in jJourn],dtype=np.float32)
    Toplot["Funds"] = np.array([i[3] for i in jJourn],dtype=np.float32)
    Toplot["Buys_time"] = [i[0] for i in jJourn if 'Buy' in i[2]]
    Toplot["Buys_share"] = [i[5] for i in jJourn if 'Buy' in i[2]]
    Toplot["Buys_chf"] = [i[4] for i in jJourn if 'Buy' in i[2]]
    Toplot["Shorts_time"] = [i[0] for i in jJourn if 'Short' in i[2]]
    Toplot["Short_chf"] = [i[6] for i in jJourn if 'Short' in i[2]]
    Toplot["Short_share"] = [i[7] for i in jJourn if 'Short' in i[2]]
    Toplot["SL_time"] = [i[0] for i in jJourn if 'Stop-limit-sell' in i[2] or 'Update stop-limit-sell' in i[2]]
    Toplot["currStopLoss"] = [i[8] for i in jJourn if 'Stop-limit-sell' in i[2] or 'Update stop-limit-sell' in i[2]]
    Toplot["currStopLossLimit"] = [i[9] for i in jJourn if 'Stop-limit-sell' in i[2] or 'Update stop-limit-sell' in i[2]]
    Toplot["LO_time"] = [i[0] for i in jJourn if 'Stop-limit-buy' in i[2] or 'Update stop-limit-buy' in i[2]]
    Toplot["currLimit"] = [i[11] for i in jJourn if 'Stop-limit-buy' in i[2] or 'Update stop-limit-buy' in i[2]]
    Toplot["currLimitLimit"] = [i[12] for i in jJourn if 'Stop-limit-buy' in i[2] or 'Update stop-limit-buy' in i[2]]
    Toplot["BC_time"] = [i[0] for i in jJourn if 'buy-closed' in i[2]]
    Toplot["SC_time"] = [i[0] for i in jJourn if 'short-closed' in i[2]]
    ToPlotFar={}
    ToPlotFar['shareBuy'] = np.array([i[5] if 'Buy' in i[2] else 0 for i in jJourn],dtype=np.float32)
    ToPlotFar['chfBuy'] = np.array([i[4] if 'Buy' in i[2] else 0 for i in jJourn],dtype=np.float32)
    ToPlotFar['shareShort'] = np.array([i[7] if 'Short' in i[2] else 0 for i in jJourn],dtype=np.float32)
    ToPlotFar['chfShort'] = np.array([i[6] if 'Short' in i[2] else 0 for i in jJourn],dtype=np.float32)

    return Toplot,JournFull,Journ,ToPlotFar    
