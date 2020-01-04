#!/usr/bin/python3

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


def main(SetUp,args):
    parser = argparse.ArgumentParser(description='Get ticker data.')
    parser.add_argument('-window', type=int, default=1, help='return last n rows')
    parser.add_argument('-tickDt', type=str,choices=["1m","15m", "30m", "1h", "2h", "4h",
        "1d", "1w","1M"],default="1h")
    parser.add_argument('-pair', type=str,choices=["BTCUSDT"],default="BTCUSDT")
    args = parser.parse_args(args)

    if not os.path.isfile(SetUp['paths']['Hist']):
        print(ffile + " does not exist. Rerun with -update False to create it.")
    
    if  os.path.isfile(SetUp['paths']['Hist']):
        with open(SetUp['paths']['Hist'],'r') as f:
            r=csv.reader(f,delimiter=',')
            row_count = sum(1 for row in r)
        with open(SetUp['paths']['Hist'],'r') as f:
            r=csv.reader(f,delimiter=',')
            row=[];
            for i in range(row_count): # count from 0 to 7
                if i < row_count-args.window:
                    next(r)     # and discard the rows
                else:
                    row.append(next(r))
                       
    return row

# Functions and Classes
def save_obj(obj, path):
    with open(path + '.pkl', 'wb') as f:
        pickle.dump(obj, f)

def load_obj(path):
    with open(path + '.pkl', 'rb') as f:
        return pickle.load(f)

class TickerStruct:
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
