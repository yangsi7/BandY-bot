function maxWins= getMaxWinForPython(varargin)
addpath(genpath('/Users/yangsi/Box Sync/UCLA/MATLAB'));
A.model='/Users/yangsi/Box Sync/Crypto/scripts/models/fre_26Nov2019.mat';
A = parse_pv_pairs(A,varargin);

load(A.model,'A');

wins = [A.ma.windowsize, A.ema.windowsize, A.tsom.numperiod, A.rsi.windowsize, A.bollin.windowsize, A.pvt.windowsize, A.chaikvolat.numperiods, A.chaikvolat.windowsize, A.normWinSize];

maxWins=nanmax(wins);

