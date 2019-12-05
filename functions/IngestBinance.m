function [ddat,TMW] = IngestCrypto(varargin)
addpath(genpath('/Users/yangsi/Box Sync/UCLA/MATLAB'));
A.resample={'m','m15','h','h4','d','w'};
A.csvpath = '/Users/yangsi/Box Sync/Crypto//scripts/python-binance/Data/BinBTCUSDT1h.csv';
A = parse_pv_pairs(A,varargin);

ddat.raw=csvread(A.csvpath,1,0);
ddat.open = ddat.raw(:,2);
ddat.high = ddat.raw(:,3);
ddat.low = ddat.raw(:,4);
ddat.close = ddat.raw(:,5);
ddat.volume = ddat.raw(:,6);

% Millisecond timestamp since 1970-01-01
ddat.militime = ddat.raw(:,7);
% Convert to datenum (second timestamp since 0000-00-00)
ddat.datenum = ddat.militime/86400 + datenum(1970,1,1);
%Convert to datetime
ddat.datetime = datetime(ddat.datenum,'ConvertFrom','datenum');

% Create a timetable from minute vector input
TMW.h = timetable(ddat.open,ddat.high,ddat.low,ddat.close,ddat.volume, ...
    'VariableNames',{'Open','High','Low','Close','Volume'},'RowTimes',ddat.datetime);

idx=find(TMW.h.Close ==0 | TMW.h.Open ==0);
if ~isempty(idx); TMW.h{idx,:}=nan; end;

TMW.h = fillmissing(TMW.h,'linear');

