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

# Paths
sys.path.append('/Users/yangsi/Box Sync/Crypto/scripts/python-binance/scripts')
securePath="/Users/yangsi/Box Sync/Crypto/secure/"
csvwritepath="/Users/yangsi/Box Sync/Crypto/scripts/python-binance/Data/"


def main(args):
    parser = argparse.ArgumentParser(description='Get ticker data.')
    parser.add_argument('-update', dest='update', action='store_true')
    parser.add_argument('-no-update', dest='update', action='store_false')
    parser.add_argument('-verbose', dest='verbose', action='store_true')
    parser.add_argument('-no-verbose', dest='verbose', action='store_false')
    parser.add_argument('-GetcsvLast', dest='GetcsvLast', action='store_true')
    parser.add_argument('-no-GetcsvLast', dest='GetcsvLast', action='store_false')
    parser.add_argument('-tickDt', type=str,choices=["1m","15m", "30m", "1h", "2h", "4h",
        "1d", "1w","1M"],default="1h")
    parser.add_argument('-pair', type=str,choices=["BTCUSDT"],default="BTCUSDT")
    parser.add_argument('-sdate', type=str,nargs='?', default="1 Jan, 2017",
                       help='Gather data from this date')
    args = parser.parse_args(args)
    #Paths to csvs and pickles
    ffile="Bin" + args.pair + args.tickDt + ".csv"
    csvfile=csvwritepath + ffile

    if (args.GetcsvLast or args.update) and not os.path.isfile(csvfile):
        print(ffile + " does not exist. Rerun with -update False to create it.")
    
    if args.GetcsvLast and os.path.isfile(csvfile):
        with open(csvfile,'r') as f:
            r=csv.reader(f,delimiter=',')
            row_count = sum(1 for row in r)
        with open(csvfile,'r') as f:
            r=csv.reader(f,delimiter=',')
            for i in range(row_count-1): # count from 0 to 7
                next(r)     # and discard the rows
            row = next(r)
        LastTimeStamp = round(float(row[6]))
        LastDatetime = datetime.fromtimestamp(LastTimeStamp) 
        LastDateStr = str(LastDatetime.day) + " " + LastDatetime.strftime("%b"
                ) + ", " + str(LastDatetime.year)
        BinInfo = {'row_count':row_count, 'LastTimeStamp':LastTimeStamp,
                'LastDatetime': LastDatetime, 'LastDateStr': LastDateStr}
        save_obj(BinInfo,csvwritepath + "Binance" + args.tickDt)
    
    
    # Get API keys and start Binance client
    apiK = open(securePath + "BinAPI.txt", "r").read().split('\n')
    client = Client(apiK[0], apiK[1])
    
    # get start date (last date in csv if updating)
    if args.update:
        BinInfo = load_obj(csvwritepath + "Binance" + args.tickDt)
        sdate = BinInfo['LastDateStr'] 
    else:
        sdate = args.sdate
    
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
    if args.update:
        # Get tick index corresponding to last ticker in csv 
        idx = tick.CloseTimeStamp.index(round(BinInfo['LastTimeStamp']))
        if idx == len(tick.CloseTimeStamp) - 1:
            if args.verbose:
                print(ffile + " is up to date")
                print("exiting...")
            sys.exit(0) 
        else:
            if args.verbose:
                print("Last update to " + ffile + " was on the " + BinInfo['LastDateStr'])
                print("Updating " + str(len(tick.CloseTimeStamp) 
                    -idx) + " " + args.tickDt + " ticks") 
    else:
        idx=0
    
    # Tick data to be written 
    tick.contlist = [[tick.OpenTimeStamp[i],tick.Open[i],tick.High[i],tick.Low[i],tick.Close[i],tick.Volume[i],tick.CloseTimeStamp[i]] for i in range(idx,len(tick.Open))]
    
    # Write data to file
    writeOption = 'a' if args.update else 'w'
    f = open(csvfile, writeOption)
    wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
    if not args.update:
        wr.writerow(["OpenTimeStamp","Open","High","Low","Close","Volume","CloseTimeStamp"])
    for item in tick.contlist:
        wr.writerow(item)    
    f.close()

    # Return rows
    return tick.contlist[-1]

# Functions and Classes
def save_obj(obj, path):
    with open(path + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(path):
    with open(path + '.pkl', 'rb') as f:
        return pickle.load(f)

class TickerStruct:
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
