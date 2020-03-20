import numpy as np
import sys
sys.path.append('/Users/yangsi/Box Sync/Crypto/scripts/python-binance/scripts')
import pandas as pd
from datetime import datetime
import matplotlib
import matplotlib.ticker as ticker
import YBotFetchRecent as fetchR
import YBotInit as ini
import matlab.engine
import pylab as plt
from mpl_finance import candlestick_ohlc
import YBotFunctions as ybf
import csv

def plotBot():
    winDays=14
    
    winHours=winDays*24
    SetUp = ini.initSetUp()
    rows = fetchR.main(SetUp,['-window',str(winHours)])
    Journ=ybf.getJournal(SetUp)
    
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
    Price=np.array(kurse_c_float,dtype=np.float32)
    
    quotes = [tuple([float(dates[i]),
                     float(kurse_o[i]),
                     float(kurse_h[i]),
                     float(kurse_l[i]),
                     float(kurse_c[i])]) for i in range(len(dates))] #_1
    
    a,b=ybf.getSig(SetUp,winHours)
    histsig = np.array(a,dtype=np.float32)
    BB = np.array(b,dtype=int)
    ii=[]
    for i in range(0,len(Journ['time'])):
        ii.append(datesFloat.index(Journ['time'][i]))
        Journ_price=[kurse_c_float[i] for i in ii]
    Journ_price=np.array(Journ_price,dtype=np.float32)
    
    funds=Journ["Funds"]
    chfbuy=(Journ['shareBuy']*Journ_price)[Journ['Buys_idx']]
    TotFunds=Journ["Funds"]+Journ['shareBuy']*Journ_price+Journ['chfShort']-Journ['shareShort']*Journ_price
    
    
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
    if Journ["Buys_idx"].size>0:
        idx=Journ["Buys_idx"]
        ax1.scatter(Journ['time'][idx],Journ["chfBuy"][idx]/Journ["shareBuy"][idx], color='g',marker='^',edgecolors='k',s=30)
    if Journ["BC_idx"].size>0:
        idx=Journ["BC_idx"]
        ax1.scatter(Journ['time'][idx],Price[idx], color='g',marker='v',edgecolors='k',s=30)
    if Journ["Shorts_idx"].size>0:
        idx=Journ["Shorts_idx"]
        ax1.scatter(Journ['time'][idx],Journ["chfShort"][idx]/Journ["shareShort"][idx], color='r',marker='v',edgecolors='k',s=30)
    if Journ["SC_idx"].size>2:
        idx=Journ["SC_idx"]
        ax1.scatter(Journ['time'][idx],Price[idx], color='r',marker='^',edgecolors='k',s=30)
    if Journ["SL_idx"].size>0:
        idx=Journ["SL_idx"]
        ax1.plot(Journ['time'][idx],Journ["currStopLoss"][idx],'+g--', linewidth=1)
        ax1.plot(Journ['time'][idx],Journ["currStopLossLimit"][idx],'+g', linewidth=1)
    if Journ["LO_idx"].size>0:
        idx = Journ["LO_idx"]
        ax1.plot(Journ['time'][idx],Journ["currLimitStop"][idx],'+r--', linewidth=1)
        ax1.plot(Journ['time'][idx],Journ["currLimitLimit"][idx],'+r', linewidth=1)
    
    ax2.plot(datesFloat,histsig[-len(datesFloat):])
    ax2.plot(Journ["time"],Journ["signal"])
    
    a=ax1.get_xticks().tolist()

    a=ddates
    ax1.set_xticklabels([])
    a=ax2.get_xticks()
    a=ddates
    ax2.set_xticklabels(a)
    ax1.tick_params(labelrotation=45)
    ax2.tick_params(labelrotation=45)
    
    ax4.plot(Journ["time"],Journ["Funds"])
    ax4.set_xticklabels([])
    ax4.tick_params(labelrotation=45)    

    ax5.plot(Journ["time"],TotFunds)
    ax5.set_xticklabels(a)
    ax5.tick_params(labelrotation=45)
    plt.savefig(SetUp['paths']['rroot']+'figures/BotJournal.pdf')
    plt.clf()


