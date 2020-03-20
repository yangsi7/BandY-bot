import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib
import matplotlib.ticker as ticker
import matlab.engine
import pylab as plt
from mpl_finance import candlestick_ohlc
import csv
from . import params as ini
from .YbotUtils import csvreadEnd

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

def getJournal(SetUp, nticks):
    jJourn=csvreadEnd(SetUp['paths']['TradeInfo'], nticks)
    return jJourn
