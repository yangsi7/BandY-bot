#!/usr/bin/python3
# Get the top-level logger object

import os
import sys

def initSetUp():
    SetUp = {}
    # Root
    rroot="/home/euphotic_/yangino-bot/"
    # Case name
    Exchange = "Binch"
     
    SetUp['exhangeType'] ='futures' # spot
    # Paths
    SetUp={"paths":{},"trade":{}};
    SetUp['paths']["rroot"]=rroot
    SetUp['paths']["secure"]=rroot+"secure/"+Exchange+"API.txt"
    SetUp['paths']["csvwrite"]=rroot+"pythonBinance/Data/"
    SetUp['paths']["trade"]=rroot+"pythonBinance/TradeData/"
    SetUp['paths']["matlab"]=rroot+"functions/"
    SetUp['paths']["model"]="StackedJan10.mat"
    SetUp["trade"]["Case"]="Dec2019"
    SetUp['FuturesDateStart']="12 Sep, 2019"

    # Create directories if none existant
    if not os.path.exists(rroot+'secure/'):
        log.warn(rroot+'secure/'+' does not exist --> creating')
        os.makedirs(rroot+'secure/')    
    if not os.path.exists(SetUp['paths']["secure"]):
        log.warn(SetUp['paths']["secure"]+' does not exist --> creating empty file')
        open(SetUp['paths']["secure"], 'a').close()
    if not os.path.exists(rroot+'models/'):
        log.warn(rroot+'models/'+' does not exist --> creating')
        os.makedirs(rroot+'models/')        
    if not os.path.exists(SetUp['paths']["csvwrite"]):
        log.warn(SetUp['paths']["csvwrite"]+' does not exist --> creating')
        os.makedirs(SetUp['paths']["csvwrite"])        

    # General Parameters
    SetUp["trade"]["pairTrade"]="BTC"
    SetUp["trade"]["pairRef"]="USDT"
    SetUp["trade"]["pair"]="BTCUSDT"
    SetUp["trade"]["tickDt"]="1h"
    SetUp["trade"]["MFee"]=0.04
    SetUp["trade"]["TFee"]=0.02

    # Trading parameters
    SetUp["trade"]["Leverage"]=20
    SetUp["trade"]["PercentFunds"]=0.3
    SetUp["trade"]["Slip"]=1.005
    SetUp["trade"]["Long"]=0.2
    SetUp["trade"]["Short"]=0.8
    SetUp["trade"]["CloseLong"]=0.65
    SetUp["trade"]["CloseShort"]=0.35
    SetUp["trade"]["Stop"]=0.04
    SetUp["trade"]["StopLimitSell"]=[0.04, 0.02]
    SetUp["trade"]["StopBuy"]=[0.025, 0.005]
    SetUp["trade"]["StopLimitBuy"]=[0.04, 0.02]
    SetUp["trade"]["TPstop"]=[0.007, 0.021]
    SetUp["trade"]["TPlimitadd"]=0.01




    # Dependant Paths
    # CSVs
    ffile=Exchange + SetUp["trade"]["pair"] + SetUp["trade"]["tickDt"] + ".csv"
    SetUp['paths']["Hist"]=SetUp["paths"]["csvwrite"] + ffile
    ffile=Exchange + SetUp["trade"]["pair"] + SetUp["trade"]["tickDt"]+"_"+SetUp["trade"]["Case"]+"_Journal.csv"
    # Pickles
    SetUp['paths']["LastInfo"]=SetUp["paths"]["csvwrite"] + "Binance" + SetUp["trade"]["tickDt"]
    SetUp['paths']["TradeInfo"]=SetUp["paths"]["csvwrite"] + ffile

    return SetUp
