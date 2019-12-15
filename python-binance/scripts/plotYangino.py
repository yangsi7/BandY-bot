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
import plotFunction
import csv

def plotBot():
    winDays=14
    
    winHours=winDays*24
    SetUp = ini.initSetUp()
    rows = fetch_recent.main(SetUp,['-window',str(winHours)])
    Toplot,JournFull,Journ,ToplotFar=plotFunction.getJournal(SetUp)
    
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
    
    ToplotAr=plotFunction.plotAr(Toplot)
    a,b=plotFunction.getSig(SetUp,JournFull,winHours)
    histsig = np.asarray(a)
    BB = np.asarray(b)
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
    plt.clf()


