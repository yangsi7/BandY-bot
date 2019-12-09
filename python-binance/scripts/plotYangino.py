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

def plotBot():
    winDays=7
    
    winHours=winDays*24
    SetUp = ini.initSetUp()
    rows = fetch_recent.main(SetUp,['-window',str(winHours)])
    Toplot,JournFull,Journ,ToplotFar=getJournal(SetUp)
    
    ccandles=[]
    for i in range(0,len(rows[0])):
        tmp=[c[i] for c in rows]
        ccandles.append(tmp)
    
    dates=ccandles[6]
    datesFloat=[float(dates[i])for i in range(len(dates))]
    def hTime(date):
        ttime=datetime.fromtimestamp(int(date)).strftime('%d')+'/'+datetime.fromtimestamp(int(date)
                ).strftime('%m')+'-'+datetime.fromtimestamp(int(date)).strftime('%H')+'h'
        return ttime
    ddates=[hTime(i) for i in dates]
    
    kurse_o=ccandles[1]
    kurse_h=ccandles[2]
    kurse_l=ccandles[3]
    kurse_c=ccandles[4]
    kurse_c_float=[float(kurse_c[i]) for i in range(len(dates))]
    
    quotes = [tuple([float(dates[i]),
                     float(kurse_o[i]),
                     float(kurse_h[i]),
                     float(kurse_l[i]),
                     float(kurse_c[i])]) for i in range(len(dates))] #_1
    
    ToplotAr=plotAr(Toplot)
    histsig=np.asarray(getSig(SetUp,JournFull,winHours))
    ii=[]
    for i in range(0,len(Journ['time'])):
        ii.append(datesFloat.index(Journ['time'][i]))
        Journ_price=[kurse_c_float[i] for i in ii]
    Journ_price=np.array(Journ_price,dtype=np.float32)
    TotFunds=Toplot["Funds"]+ToplotFar['shareBuy']*Journ_price+ToplotFar['chfShort']-ToplotFar['shareShort']*Journ_price
    
    
    fig = plt.figure(figsize=(15, 8))
    grid = plt.GridSpec(3, 3, wspace=0.4, hspace=0.3)
    ax1=plt.subplot(grid[0:2, 0:2])
    ax1.grid
    plt.title('Trade history (BTCUSDT)')
    ax2=plt.subplot(grid[2, 0:2])
    ax2.grid
    plt.title('Hotness index')
    ax3=plt.subplot(grid[0, 2])
    ax4=plt.subplot(grid[1, 2])
    plt.title('Funds (USDT)')
    ax5=plt.subplot(grid[2, 2])
    plt.title('Total Funds (equivalent USDT)')
    
    cl = candlestick_ohlc(ax1,quotes, width=0.8, colorup='k', colordown='k', alpha=1.0)
    if ToplotAr['Buys_time'].size>0:
        ax1.scatter(ToplotAr['Buys_time'],ToplotAr['Buys_chf']/ToplotAr['Buys_share'], color='g',marker='^',edgecolors='k',s=30)
    if ToplotAr['BC_time']!=None:
        ii=[]
        for i in range(0,len(ToplotAr['BC_time'])):
            ii.append(datesFloat.index(ToplotAr['BC_time'][i]))
        BC_price=[kurse_c_float[i] for i in ii]
        ax1.scatter(ToplotAr['BC_time'],BC_price, color='g',marker='v',edgecolors='k',s=30)
    if ToplotAr['Shorts_time']!=None:
        ax1.scatter(ToplotAr['Short_time'],ToplotAr['Short_chf']/ToplotAr['Short_share'], color='r',marker='v',edgecolors='k',s=30)
    if ToplotAr['SC_time']!=None:
        ii=[]
        for i in range(0,len(ToplotAr['SC_time'])):
            ii.append(datesFloat.index(ToplotAr['SC_time'][i]))
        SC_price=[kurse_c_float[i] for i in ii]
        ax1.scatter(ToplotAr['SC_time'],SC_price, color='r',marker='^',edgecolors='k',s=30)
    if ToplotAr['SL_time']!=None:
        SLtime=np.array([i for i in range(ToplotAr['SL_time'],int(Journ["time"][-1]))],dtype=np.float32)
        SLprice=np.array([ToplotAr['SL'] for i in range(ToplotAr['SL_time'],int(Journ["time"][-1]))],dtype=np.float32)
        SLLprice=np.array([ToplotAr['SLL'] for i in range(ToplotAr['SL_time'],int(Journ["time"][-1]))],dtype=np.float32)
        ax1.plot(SLtime,SLprice,'g--', linewidth=1)
        ax1.plot(SLtime,SLprice,'g', linewidth=1)
    if ToplotAr['LO_time']!=None:
        SLtime=np.array([i for i in range(ToplotAr['LO_time'],int(Journ["time"][-1]))],dtype=np.float32)
        SLprice=np.array([ToplotAr['LO'] for i in range(ToplotAr['LO_time'],int(Journ["time"][-1]))],dtype=np.float32)
        SLLprice==np.array([ToplotAr['LOL'] for i in range(ToplotAr['LO_time'],int(Journ["time"][-1]))],dtype=np.float32)
        ax1.plot(SLtime,SLprice,'r--', linewidth=1)
        ax1.plot(SLtime,SLprice,'r', linewidth=1)
    
    ax2.plot(datesFloat,histsig[-len(datesFloat):])
    ax2.plot(np.array(Journ["time"],dtype=np.float32),np.array(Journ["signal"],dtype=np.float32))
    
    a=ax1.get_xticks().tolist()
    a=ddates
    ax1.set_xticklabels([])
    a=ax2.get_xticks()
    a=ddates
    ax2.set_xticklabels(a)
    ax1.tick_params(labelrotation=45)
    ax2.tick_params(labelrotation=45)
    
    ax4.plot(Toplot["time"],Toplot["Funds"])
    ax4.set_xticklabels([])
    ax4.tick_params(labelrotation=45)    

    ax5.plot(Toplot["time"],TotFunds)
    ax5.set_xticklabels(a)
    ax5.tick_params(labelrotation=45)
    plt.savefig('/Users/yangsi/Box Sync/Crypto/scripts/figures/BotJournal.pdf')

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
    nrows = int(eng.getMaxWinForPython('model',SetUp["paths"]["model"]))
    rows = fetch_recent.main(SetUp,['-window',str(nrows+winHours)])
    rows = [[float(i) for i in j] for j in rows]
    try:
        # Fire Buy/Short/Sell signals
        signal = eng.getHotnessForPython(matlab.double(rows),'model',SetUp["paths"]["model"])
    except:
        print("Unexpected error:", sys.exc_info()[0])
    eng.quit()
    return signal

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
    Toplot["currStopLoss"] = [i[4] for i in jJourn if 'Stop-limit-sell' in i[2] or 'Update stop-limit-sell' in i[2]]
    Toplot["currStopLossLimit"] = [i[4] for i in jJourn if 'Stop-limit-sell' in i[2] or 'Update stop-limit-sell' in i[2]]
    Toplot["LO_time"] = [i[0] for i in jJourn if 'Stop-limit-buy' in i[2] or 'Update stop-limit-buy' in i[2]]
    Toplot["currLimit"] = [i[4] for i in jJourn if 'Stop-limit-buy' in i[2] or 'Update stop-limit-buy' in i[2]]
    Toplot["currLimitLimit"] = [i[4] for i in jJourn if 'Stop-limit-buy' in i[2] or 'Update stop-limit-buy' in i[2]]
    Toplot["BC_time"] = [i[0] for i in jJourn if 'buy-closed' in i[2]]    
    Toplot["SC_time"] = [i[0] for i in jJourn if 'short-closed' in i[2]]
    ToPlotFar={}
    ToPlotFar['shareBuy'] = np.array([i[5] if 'Buy' in i[2] else 0 for i in jJourn],dtype=np.float32)
    ToPlotFar['chfBuy'] = np.array([i[4] if 'Buy' in i[2] else 0 for i in jJourn],dtype=np.float32)
    ToPlotFar['shareShort'] = np.array([i[7] if 'Short' in i[2] else 0 for i in jJourn],dtype=np.float32)
    ToPlotFar['chfShort'] = np.array([i[6] if 'Short' in i[2] else 0 for i in jJourn],dtype=np.float32)    

    return Toplot,JournFull,Journ,ToPlotFar

