import numpy as np
import sys
sys.path.append('/Users/yangsi/Box Sync/Crypto/scripts/python-binance/scripts')
import pandas as pd
from datetime import datetime
import matplotlib
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matlab.engine
import pylab as plt
from mpl_finance import candlestick_ohlc
from . import plotUtils as pu
from . import params as ini
from . import YbotUtils as ybu
from . import fetchHistorical as fetchH
import csv
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

def plotBot():
    winDays=14
    winHours=winDays*24
    SetUp = ini.initSetUp()
    lrow = fetchH.main(['-pair', SetUp["trade"]["pair"],
        '-tickDt',SetUp["trade"]["tickDt"],'-tail',str(winHours)])    
    Journ=pu.getJournal(SetUp,winHours)
    Journ = Journ[[not i for i in Journ['Close timestmp'].isnull()]]
    Journ['price'] = [float(lrow[lrow['Close timestmp']==float(i)]['Close']) for i in Journ['Close timestmp']]
    Journ=Journ.rename(columns={'Close timestmp':'date'})
    Journ = Journ[[not i for i in Journ['date'].isnull()]]
    Journ.date=[mdates.date2num(datetime.fromtimestamp(i)) for i in Journ['date']]
    
    df = lrow[['Close dtime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df=df.rename(columns={'Close dtime':'date'})
    df.date=df['date'].apply(mdates.date2num)
    
    a,b=ybu.getSig(SetUp,winHours)
    histsig = np.array(a,dtype=np.float32)
    BB = np.array(b,dtype=int)
    ii=[]
    
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
    
    cl = candlestick_ohlc(ax1,df.values, width=0.02, colorup='k', colordown='k', alpha=1.0)
    ax1.scatter(Journ[Journ['Buy-BTC']==True]['date'],Journ[Journ['Buy-BTC']==True
        ]['price'], color='g',marker='^',edgecolors='k',s=30)
    ax1.scatter(Journ[Journ['Close-BTC-Buy']==True]['date'],Journ[
        Journ['Close-BTC-Buy']==True]['price'
            ], color='g',marker='v',edgecolors='k',s=30)
    ax1.scatter(Journ[Journ['Short-BTC']==True]['date'],Journ[Journ['Short-BTC']==True
        ]['price'], color='r',marker='v',edgecolors='k',s=30)
    ax1.scatter(Journ[Journ['Close-BTC-Short']==True]['date'],Journ[
        Journ['Close-BTC-Short']==True]['price'
            ], color='r',marker='^',edgecolors='k',s=30)

    ax1.xaxis_date()
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
    ax1.tick_params(labelrotation=45)

    
    ax2.plot(df.date, histsig)
    ax2.plot(Journ["date"],Journ["Signal"])
    ax2.xaxis_date()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H'))
    ax2.tick_params(labelrotation=45)

    plt.savefig(SetUp['paths']['rroot']+'figures/BotJournal.pdf')
    plt.clf()


