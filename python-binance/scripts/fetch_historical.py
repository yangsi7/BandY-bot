#!/usr/bin/env python

"""Module summary
Fetch (or update existing) historical Ticker data
"""

from binance.client import Client
from datetime import datetime
import sys
import csv
import os.path
import argparse
import pickle
import initBot as ini

# Paths
sys.path.append('/Users/yangsi/Box Sync/Crypto/scripts/python-binance/scripts')

def main(args):
    SetUp = ini.initSetUp()    
    parser = argparse.ArgumentParser(description='Get ticker data.')
    parser.add_argument('-verbose', dest='verbose', action='store_true')
    parser.add_argument('-no-verbose', dest='verbose', action='store_false')
    parser.add_argument('-tickDt', type=str,choices=["1m","15m", "30m", "1h", "2h", "4h",
        "1d", "1w","1M"],default="1h")
    parser.add_argument('-pair', type=str,choices=["BTCUSDT"],default="BTCUSDT")
    parser.add_argument('-sdate', type=str,nargs='?', default="1 Jan, 2017",
                       help='Gather data from this date')
    args = parser.parse_args(args)

    # Last timestamp of database to check for corruption
    binInfoPath=SetUp["paths"]["csvwrite"] + "Binance" + args.tickDt
    if not isCorrupt(SetUp["paths"]["Hist"],binInfoPath):
        BinInfo = load_obj(binInfoPath)
        tt=datetime.fromtimestamp(BinInfo['LastTimeStamp']-3600*24)
        dayBefore=str(tt.day)+' '+tt.strftime('%b')+', '+str(tt.year)
        sdate = dayBefore 
    else:
        sdate = args.sdate
        print('--Historical file does not exists or is corrupt')
        print('-----')
        print('--Creating new data base for '+args.pair+args.tickDt+' starting from '+sdate)
    # Get tickers    
    ticks=getTickers(args,sdate,SetUp)
    listTocsv=ticks.contlist

    # Write data to file
    if not isCorrupt(SetUp["paths"]["Hist"],binInfoPath):
        idx = ticks.CloseTimeStamp.index(round(BinInfo['LastTimeStamp']))
        writeTocsv(listTocsv[idx+1:-1],SetUp["paths"]["Hist"],'a')
        if len(listTocsv[idx+1:])<=1:
            print("---" + args.pair + args.tickDt + " is up to date!")
        else:
            print("---Last update to " + args.pair + args.tickDt + " was on the " + BinInfo['LastDateStr'])
            print("------")        
            print("Updating " + str(len(listTocsv[idx+1:-1]) 
             ) + " " + args.tickDt + " ticks")         
        BinInfo={}
    else:
        a = ["OpenTimeStamp","Open","High","Low","Close","Volume","CloseTimeStamp"]
        a.append(listTocsv)
        writeTocsv(listTocsv[:-1],SetUp["paths"]["Hist"],'w')
    BinInfo={}
    BinInfo['LastTimeStamp']=ticks.CloseTimeStamp[-2]        
    tt=ticks.CloseDate[-2]
    BinInfo['LastDateStr']=str(tt.day)+' '+tt.strftime('%b')+', '+str(tt.year)
    save_obj(BinInfo,binInfoPath)

    return listTocsv[-2]

# Functions and Classes
def save_obj(obj, path):
    with open(path + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(path):
    with open(path + '.pkl', 'rb') as f:
        return pickle.load(f)

def isCorrupt(ccsv,ppickle):
 # Check if database is corrupted (Maybe implement more checks later on)    
    if not os.path.isfile(ccsv) or not os.path.isfile(ppickle+'.pkl'):
        return True
    row=csvreadEnd(ccsv, 1)[0]
    pickleLast=load_obj(ppickle)
    if round(float(row[6]))!=pickleLast['LastTimeStamp']:
        return True
    else:
        return False

def csvreadEnd(csvfile, nrows):
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
    return row

def writeTocsv(llist,ppath,writeOption):
    # Write list to csv
    f = open(ppath, writeOption)
    wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
    for item in llist:
        wr.writerow(item)
    f.close()

def getTickers(args,sdate,SetUp):
    # Get API keys and start Binance client
    apiK = open(SetUp["paths"]["secure"], "r").read().split('\n')
    client = Client(apiK[0], apiK[1])    
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
    tick.contlist = [[tick.OpenTimeStamp[i],tick.Open[i],tick.High[i],tick.Low[i],tick.Close[i],tick.Volume[i],tick.CloseTimeStamp[i]] for i in range(0,len(tick.Open))]
    return tick
    

class TickerStruct:
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
