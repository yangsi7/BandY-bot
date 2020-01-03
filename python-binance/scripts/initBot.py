def initSetUp():
    # Case name
    Exchange = "Binch"

    # Paths
    SetUp={"paths":{},"trade":{}};
    SetUp['paths']["secure"]="/Users/yangsi/Box Sync/Crypto/secure/"+Exchange+"API.txt"
    SetUp['paths']["csvwrite"]="/Users/yangsi/Box Sync/Crypto/scripts/python-binance/Data/"
    SetUp['paths']["trade"]="/Users/yangsi/Box Sync/Crypto/scripts/python-binance/tradeData/"
    SetUp['paths']["matlab"]="/Users/yangsi/Box Sync/Crypto/scripts/functions/"
    SetUp['paths']["model"]="/Users/yangsi/Box Sync/Crypto/scripts/models/fre_11Dec2019.mat"
    SetUp["trade"]["Case"]="Dec2019"

    # General Parameters
    SetUp["trade"]["pairTrade"]="BTC"
    SetUp["trade"]["pairRef"]="USDT"
    SetUp["trade"]["pair"]="BTCUSDT"
    SetUp["trade"]["tickDt"]="1h"
    SetUp["trade"]["MFee"]=0.075
    SetUp["trade"]["TFee"]=0.075

    # Trading parameters
    SetUp["trade"]["StartFunds"]=413.85
    SetUp["trade"]["PercentFunds"]=0.5
    SetUp["trade"]["SLTresh"]=0.0075
    SetUp["trade"]["LOTresh"]=0.0075
    SetUp["trade"]["SLlimit"]=0.02
    SetUp["trade"]["LOlimit"]=0.02
    SetUp["trade"]["SLTresh2"]=0.02
    SetUp["trade"]["LOTresh2"]=0.02
    SetUp["trade"]["SLlimit2"]=0.03
    SetUp["trade"]["LOlimit2"]=0.03
    SetUp["trade"]["Slip"]=1.005
    SetUp["trade"]["sellSig"]=0.6
    SetUp["trade"]["shortSig"]=0.7
    SetUp["trade"]["buySig"]=0.2
    SetUp["trade"]["closeShortSig"]=0.2




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
