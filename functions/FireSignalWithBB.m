function HotnessIdx = FireSignalWithBB(varargin)

%load('/Users/yangsi/Box Sync/Crypto/scripts/models/fre_11Dec2019.mat')
B.rroot = '/home/euphotic_/yangino-bot/';
B.model='fre_11Dec2019.mat';
B.PredTimeIndex = timerange(datetime('01-Jun-2019','Locale','en_US'),datetime('01-Jan-2200','Locale','en_US'),'closed');
B.Xwin=1;
B=parse_pv_pairs(B,varargin);
addpath(genpath(B.rroot));
modelPath=[B.rroot,'models/',B.model];

id='MATLAB:class:mustReturnObject';
warning('off',id);
load(modelPath);

[~,TMW]=IngestBinance;

% First Get hotness
tmwNN = getHotness(TMW.h);

% Normalize price
B.normWinSize=[14*24, 0]; % Window size of 2 week backwards
[tmw] = NormalizePrice(TMW.h,'windowsize',B.normWinSize);

% Calulate technical indicators
% % % %
[varnames,tmw]=CalcIndicators(tmw,'ParamStruct',A);
[varnames, tmw] = GetIndsDtDdt(tmw,varnames);

% Add "Hotness Index"
% % % %
tmw=[tmw,tmwNN(:,'priceNorm')];

%Make initial prediction
[tmwpred]=PredBuyIdx(tmw,Mdlr,'varnames',varnames,'method','fitrensemble');

% Remove first hours to avoid nans
rmNan=500;
x=tmwpred.yhat_fre;
x1=x(rmNan:end);

% Bullish/bearish Indicator
% Trend of T3w30 
ddt3=tmwpred.dd_T3w30(rmNan:end);
% Normalized of T3w30
t3=tmwpred.T3w30(rmNan:end);
nt3=  BackNorm(t3,'BackNormWin',30*24);
BB=nan(size(t3));
BB=(ddt3>0);


idxRaw=x1;
% Filter trends
% Get trend and detrend
windowSize=30*24*3;
y1 = filterSY(x1,'windowSize',windowSize);
x2=x1-y1; % detrended

% Get medium-term index and normalize
backNormWin1=30*24; % 2 weeks
idMed= BackNorm(x2,'BackNormWin',backNormWin1);

windowSize2=30*24;
y2 = filterSY(x2,'windowSize',windowSize2);

% remove medium-term index to get short term index
x3=x2-y2;
% Filter out noise
windowSize3=4;
y3 = filterSY(x3,'windowSize',windowSize3);
% Normalized denoized short term index
backNormWin2=30*24; % 2 weeks
idShort= BackNorm(y3,'backNormWin',backNormWin2);

% Add indexes back to timetable and filter
% % % %
tmwpred = addvars(tmwpred(rmNan:end,:),idxRaw,idMed,idShort);
tmwpred=tmwpred(B.PredTimeIndex,:);

HotnessIdx=[idShort,BB];
HotnessIdx=HotnessIdx(end-B.Xwin+1:end,:);

