% % % % % % % % % % % % % % % % % % % %
% % % % Yangino Crypto Bot  % % % % % % 
% % % % % % % % % % % % % % % % % % % %

% Add data and functions Paths
% % % % 

 addpath(genpath('/Users/yangsi/Box Sync/Crypto/'));
 [~,TMW]=IngestCrypto;

 
% Technical indicator parameters
% % % %

 A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed');
 A.TrainTimeIndex = timerange(datetime('01-Jan-2019','Locale','en_US'),datetime('01-May-2019','Locale','en_US'),'closed');
 A.PredTimeIndex = timerange(datetime('02-May-2019','Locale','en_US'),datetime('30-Sep-2019','Locale','en_US'),'closed');
 % ma
 A.ma.windowsize = 15;
 % ema
 A.ema.windowsize = [15,30];%[5  10 15 30 50];
 % T3
 A.T3.v = 0.7;
 %tsom
 A.tsom.numperiod = 12;
 % rsi
 A.rsi.windowsize = [15,30];%[5  10 15 30 50];
 %bollinger
 A.bollin.windowsize=[15, 30];%[5  10 15 30 50];
 A.bollin.matype = 0; % 0: normal, 1: linear moving average
 A.bollin.numstd = 2; % Number of standard deviations for the upper and lower bounds
 %PVT
 A.pvt.windowsize=[15, 30];
 %chaikvolat
 A.chaikvolat.numperiods = 10;
 A.chaikvolat.windowsize = [15, 30];;%[5  10 15 30 50];

% Replace Open, Close, High, Low prices with
% a running nmin-max normalization
% % % % 

 normWinSize=[14*24, 0]; % Window size of 2 week backwards
 [tmw] = NormalizePrice(TMW.h,'windowsize',normWinSize);

% Calulate technical indicators
% % % %
 [varnames,tmw]=CalcIndicators(tmw,'ParamStruct',A);
 [varnames, tmw] = GetIndsDtDdt(tmw,varnames);

% Calulate "Hotness Index"
% % % %

 tmw=getOpenClose(tmw);

% Build a regression Forest
% % % %

 [Mdlr,impr]=BuildForest(tmw,'varnames',varnames,'TimeIndex',A.TrainTimeIndex);
 [tmwpred]=PredBuyIdx(tmw,Mdlr,'varnames',varnames,'method','fitrensemble','TimeIndex',A.PredTimeIndex);

% Build a classification Forest
% % % %

[Mdlc]=BuildcForest(tmw,'varnames',varnames,'TimeIndex',A.TrainTimeIndex);
[tmwpred]=PredBuyIdx(tmwpred,Mdlc,'method','fitcensemble','varnames',varnames,'TimeIndex',A.PredTimeIndex);

% Build a SVM classification model
% % % %
%[SVMc]=BuildcSVM(tmw);

% Plot performances 
% % % %
plotPerf(tmwpred,'method','fitrensemble');
plotPerf(tmwpred,'method','fitcensemble');

tmwpredNotNormalize=[TMW.h(A.PredTimeIndex,:),tmwpred(:,'yhat_fre')];
SumPerf = cryptoSim(tmwpredNotNormalize)
