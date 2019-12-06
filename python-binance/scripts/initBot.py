def initSetUp():
    # Case name
    Exchange = "Binch"

    # Paths
    SetUp={"paths":{},"trade":{}};
    SetUp['paths']["secure"]="/Users/yangsi/Box Sync/Crypto/secure/"+Exchange+"API.txt"
    SetUp['paths']["csvwrite"]="/Users/yangsi/Box Sync/Crypto/scripts/python-binance/Data/"
    SetUp['paths']["trade"]="/Users/yangsi/Box Sync/Crypto/scripts/python-binance/tradeData/"
    SetUp['paths']["matlab"]="/Users/yangsi/Box Sync/Crypto/scripts/functions/"
    SetUp['paths']["model"]="/Users/yangsi/Box Sync/Crypto/scripts/models/fre_26Nov2019.mat"
    SetUp["trade"]["Case"]="Dec2019"

    # General Parameters
    SetUp["trade"]["pairTrade"]="BTC"
    SetUp["trade"]["pairRef"]="USDT"
    SetUp["trade"]["pair"]="BTCUSDT"
    SetUp["trade"]["tickDt"]="1h"
    SetUp["trade"]["MFee"]=0.075
    SetUp["trade"]["TFee"]=0.075

    # Trading parameters
    SetUp["trade"]["StartFunds"]=200
    SetUp["trade"]["PercentFunds"]=0.5
    SetUp["trade"]["SLTresh"]=0.019
    SetUp["trade"]["LOTresh"]=0.019
    SetUp["trade"]["SLlimit"]=0.025
    SetUp["trade"]["LOlimit"]=0.025
    SetUp["trade"]["Slip"]=1.005



    # Dependant Paths
    # CSVs
    ffile=Exchange + SetUp["trade"]["pair"] + SetUp["trade"]["tickDt"] + ".csv"
    SetUp['paths']["Hist"]=SetUp["paths"]["csvwrite"] + ffile
    ffile=Exchange + SetUp["trade"]["pair"] + SetUp["trade"]["tickDt"]+"_"+SetUp["trade"]["Case"]+"_Journal.csv"
    SetUp['paths']["Journal"]=SetUp["paths"]["csvwrite"] + ffile
    # Pickles
    SetUp['paths']["LastInfo"]=SetUp["paths"]["csvwrite"] + "Binance" + SetUp["trade"]["tickDt"]
    SetUp['paths']["TradeInfo"]=SetUp["paths"]["trade"] + "CurrTradeBinance" + SetUp["trade"]["tickDt"]

    return SetUp
