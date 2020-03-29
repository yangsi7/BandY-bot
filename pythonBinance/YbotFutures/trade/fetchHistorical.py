#!/usr/bin/python3

"""Module summary
Fetch (or update existing) historical Ticker data
"""
import sys
sys.path.append("..")
from datetime import datetime
import sys
import csv
import os.path
import argparse
import pickle
import pandas as pd
from . import params as ini
from APIpyBinance.client_futures import Client as ClientFutures
from APIpyBinance.client import Client as ClientExchange

def main(args):
    SetUp = ini.initSetUp()    
    parser = argparse.ArgumentParser(description='Get ticker data.')
    parser.add_argument('-verbose', dest='verbose', action='store_true')
    parser.add_argument('-no-verbose', dest='verbose', action='store_false')
    parser.add_argument('-futures', dest='verbose', action='store_false')
    parser.add_argument('-tickDt', type=str,choices=["1m","15m", "30m", "1h", "2h", "4h",
        "1d", "1w","1M"],default="1h")
    parser.add_argument('-tail', type=int, help="Return n last rows",default='2')
    parser.add_argument('-pair', type=str,choices=["BTCUSDT"],default="BTCUSDT")
    parser.add_argument('-sdate', type=str,nargs='?', default="1 Jan, 2017",
                       help='Gather data from this date')
    args = parser.parse_args(args)
    

    # Last timestamp of database to check for corruption
    # import data $ddays before last timestamp and drop duplicates for more stability
    ddays=2
    if not isCorrupt(SetUp["paths"]["Hist"],SetUp['paths']["LastInfo"]):
        BinInfo = load_obj(SetUp['paths']["LastInfo"])
        tt=datetime.fromtimestamp(BinInfo['LastTimeStamp']-3600*24*ddays)
        dayBefore=str(tt.day)+' '+tt.strftime('%b')+', '+str(tt.year)
        sdate = dayBefore 
    else:
        sdate = args.sdate
        print('--Historical file does not exists or is corrupt')
        print('-----')
        print('--Creating new data base for '+args.pair+args.tickDt+' starting from '+sdate)
        print('--Exchange data used until '+SetUp['FuturesDateStart']+' and Futures data beyond')
        TicksExchange=getTickers(args,sdate,SetUp,exch='Exchange')
    # Get tickers 
    Ticks=getTickers(args,SetUp['FuturesDateStart'],SetUp)

    # Write data to file
    if not isCorrupt(SetUp["paths"]["Hist"],SetUp['paths']["LastInfo"]):
        dfHist = pd.read_csv(SetUp["paths"]["Hist"])
        iniLen=len(dfHist)
        dfHist=dfHist.append(Ticks.iloc[:], ignore_index = True)
        dfHist.drop_duplicates(subset='Open timestmp',keep='last',inplace=True)
        dfHist.to_csv(SetUp["paths"]["Hist"], index=False, header=True)
        if len(dfHist)==iniLen:
            print("---" + args.pair + args.tickDt + " is up to date!")
        else:
            print("---Last update to " + args.pair + args.tickDt + " was on the " + BinInfo['LastDateStr'])
            print("------")        
            print("Updating " + str(len(dfHist)-iniLen 
             ) + " " + args.tickDt + " ticks")         
        BinInfo={}
    else:
        Ticks = TicksExchange.append(Ticks.iloc[:], ignore_index = True)
        Ticks.drop_duplicates(subset='Open timestmp',keep='last',inplace=True)
        Ticks.to_csv(SetUp["paths"]["Hist"], index=False, header=True)
    BinInfo={}
    BinInfo['LastTimeStamp']=Ticks.iloc[-2]['Close timestmp']   
    tt=Ticks.iloc[-2]['Close dtime']
    BinInfo['LastDateStr']=str(tt.day)+' '+tt.strftime('%b')+', '+str(tt.year)    
    save_obj(BinInfo,SetUp['paths']["LastInfo"])

    return Ticks.tail(args.tail)

# Functions and Classes
def save_obj(obj, path):
    with open(path + '.pkl', 'wb') as f:
        pickle.dump(obj, f)

def load_obj(path):
    with open(path + '.pkl', 'rb') as f:
        return pickle.load(f)

def isCorrupt(ccsv,ppickle):
 # Check if database is corrupted (Maybe implement more checks later on)    
    if not os.path.isfile(ccsv) or not os.path.isfile(ppickle+'.pkl'):
        return True
    row=csvreadEnd(ccsv, 2).iloc[0]
    pickleLast=load_obj(ppickle)
    if int(row['Close timestmp'])!=int(pickleLast['LastTimeStamp']):
        return True
    else:
        return False

def writeTocsv(llist,ppath,writeOption):
    # Write list to csv
    f = open(ppath, writeOption)
    wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
    for item in llist:
        wr.writerow(item)
    f.close()

def getTickers(args,sdate,SetUp,exch='Exchange'):
    # Get API keys and start Binance client
    apiK = open(SetUp["paths"]["secure"], "r").read().split('\n')
    if exch == 'Futures':
        client = ClientFutures(apiK[0], apiK[1])    
    elif exch=='Exchange':
        client = ClientExchange(apiK[0], apiK[1])
    else:
        raise Exception('Invalid value for exch')
        
    # get ticker data
    klines = client.get_historical_klines(args.pair, args.tickDt, sdate)
    tick = TickerStruct()
    tick.OpenTimeStamp = [round(item[0]/1000) for item in klines]
    tick.OpenDate = [datetime.fromtimestamp(date) for date in tick.OpenTimeStamp]
    tick.Open = [float(item[1]) for item in klines]
    tick.High = [float(item[2]) for item in klines]
    tick.Low = [float(item[3]) for item in klines]
    tick.Close = [float(item[4]) for item in klines]
    tick.Volume = [float(item[5]) for item in klines]
    tick.CloseTimeStamp = [round(item[6]/1000) for item in klines]
    tick.CloseDate = [datetime.fromtimestamp(date) for date in tick.CloseTimeStamp]
    # Tick data to be written
    toDf = {'Open timestmp':tick.OpenTimeStamp, 'Open':tick.Open,'High':tick.High,
            'Low':tick.Low, 'Close':tick.Close, 'Volume':tick.Volume, 'Close timestmp': 
            tick.CloseTimeStamp,'Open dtime':tick.OpenDate, 'Close dtime':tick.CloseDate}
    dfTicks =  pd.DataFrame(toDf)
    
    return dfTicks 

def csvreadEnd(csvfile, nrows):
    readAll = pd.read_csv(csvfile)
    a = readAll.tail(nrows)
    return a
    

class TickerStruct:
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
