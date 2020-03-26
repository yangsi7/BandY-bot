function [ddat,TMW] = IngestCrypto(varargin)
addpath(genpath('/Users/yangsi/Box Sync/UCLA/MATLAB'));
A.resample={'m','m15','h','h4','d','w'};
A.rroot='/home/euphotic_/yangino-bot/';
A.ValidTimeIndex = timerange(datetime('01-Sep-2000','Locale','en_US'),datetime('01-Jan-2200','Locale','en_US'),'closed');
A = parse_pv_pairs(A,varargin);
A.csvpath = [A.rroot,'/pythonBinance/Data/BinchBTCUSDT1h.csv'];

warning('off','MATLAB:table:ModifiedAndSavedVarnames');

format long;

ddat.raw=readtable(A.csvpath);
ddat.open = table2array(ddat.raw(:,2));
ddat.high = table2array(ddat.raw(:,3));
ddat.low = table2array(ddat.raw(:,4));
ddat.close = table2array(ddat.raw(:,5));
ddat.volume = table2array(ddat.raw(:,6));

% Millisecond timestamp since 1970-01-01
ddat.militime = table2array(ddat.raw(:,7));
% Convert to datenum (second timestamp since 0000-00-00)
%Convert to datetime
ddat.datetime = datetime(ddat.militime,'ConvertFrom','posixtime','TimeZone','');

% Create a timetable from minute vector input
TMW.h = timetable(ddat.open,ddat.high,ddat.low,ddat.close,ddat.volume, ...
    'VariableNames',{'Open','High','Low','Close','Volume'},'RowTimes',ddat.datetime);

idx=find(TMW.h.Close == 0 | TMW.h.Open == 0 | TMW.h.High == 0 | TMW.h.Low==0);
if ~isempty(idx); TMW.h{idx,:}=nan; end;

idx=find(TMW.h.Close ==inf | TMW.h.Open ==inf | TMW.h.High == inf | TMW.h.Low==inf);
if ~isempty(idx); TMW.h{idx,:}=nan; end;

TMW.h = fillmissing(TMW.h,'linear');
TMW.h = TMW.h(A.ValidTimeIndex,:);

