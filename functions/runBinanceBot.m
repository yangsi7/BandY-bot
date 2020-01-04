% % % % % % % % % % % % % % % % % % % %
% % % % Yangino Crypto Bot  % % % % % % 
% % % % % % % % % % % % % % % % % % % %

% Add data and functions Paths
% % % % 
 rroot='/home/euphotic_/yangino-bot/';
 addpath(genpath(rroot));
 [~,TMW]=IngestBinance('rroot',rroot);

 
% Technical indicator parameters
% % % %

 A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed');
 A.TrainTimeIndex = timerange(datetime('01-May-2019','Locale','en_US'),datetime('30-Nov-2019','Locale','en_US'),'closed');
 A.PredTimeIndex = timerange(datetime('02-Jun-2019','Locale','en_US'),datetime('11-Dec-2020','Locale','en_US'),'closed');
 % ma
 A.ma.windowsize = 15;
 % ema
 A.ema.windowsize = [7, 15,30];%[5  10 15 30 50];
 % T3
 A.T3.v = 0.7;
 %tsom
 A.tsom.numperiod = 12;
 % rsi
 A.rsi.windowsize = [7, 15,30];%[5  10 15 30 50];
 %bollinger
 A.bollin.windowsize=[7, 15, 30];%[5  10 15 30 50];
 A.bollin.matype = 0; % 0: normal, 1: linear moving average
 A.bollin.numstd = 2; % Number of standard deviations for the upper and lower bounds
 %PVT
 A.pvt.windowsize=[7, 15, 30];
 %chaikvolat
 A.chaikvolat.numperiods = 10;
 A.chaikvolat.windowsize = [7, 15, 30];%[5  10 15 30 50];
 % Jurik MA
 A.jma.L=[7, 15, 30];
 A.jma.phi=50;
 A.jma.pow=2;

% First Get hotness
tmwNN = getHotness(TMW.h);

% Normalize price 
 A.normWinSize=[14*24, 0]; % Window size of 2 week backwards
 [tmw] = NormalizePrice(TMW.h,'windowsize',A.normWinSize);

% Calulate technical indicators
% % % %
 [varnames,tmw]=CalcIndicators(tmw,'ParamStruct',A);
 [varnames, tmw] = GetIndsDtDdt(tmw,varnames);

% Add "Hotness Index"
% % % %

 tmw=[tmw,tmwNN(:,'priceNorm')];

% Build a regression Forest
% % % %

 [Mdlr,impr]=BuildForest(tmw,'varnames',varnames,'TimeIndex',A.TrainTimeIndex,'PredictorImportance',0);
  save('/Users/yangsi/Box Sync/Crypto/scripts/models/fre_11Dec2019.mat','Mdlr','A','varnames')
 [tmwpred]=PredBuyIdx(tmw,Mdlr,'varnames',varnames,'method','fitrensemble','TimeIndex',A.PredTimeIndex);
 save('/Users/yangsi/Box Sync/Crypto/scripts/models/fre_11Dec2019.mat','MdlrCompact','A','varnames')

% Build a classification Forest
% % % %

[Mdlc]=BuildcForest(tmw,'varnames',varnames,'TimeIndex',A.TrainTimeIndex);
[tmwpred]=PredBuyIdx(tmwpred,Mdlc,'method','fitcensemble','varnames',varnames,'TimeIndex',A.PredTimeIndex);

% Run simulation and calculate profit
tmwpredNotNormalize=[TMW.h(A.PredTimeIndex,:),tmwpred(:,'yhat_fre')];
A.TrStpLoss = (0:0.005:0.1); % Need to make adaptative to volatility
A.TrLmtOrder = (0:0.005:0.1); % Idem
for i = 1 :length(A.TrStpLoss) 
   SumPerf{i} = cryptoSim(tmwpredNotNormalize,'TrStpLoss',A.TrStpLoss(i),'TrLmtOrder',A.TrLmtOrder(i));
   perfTot(i)=sum([SumPerf{i}.profitTot]);
end
bar(A.TrStpLoss*100,perfTot);
xlabel('Trailing SL and LO (% of price)');
ylabel('Gains over 6 month ($)')

A.TrStpLoss=0.0200;
A.TrLmtOrder=0.0200;
A.normWin=(1:14)*24;
for i = 1 :length(A.normWin)
   normwin=[A.normWin(i),0];
 [tmwpred]=PredBuyIdx(tmw,Mdlr,'varnames',varnames,'method','fitrensemble','TimeIndex',A.PredTimeIndex,'normWin',normwin);   
 tmwpredNotNormalize=[TMW.h(A.PredTimeIndex,:),tmwpred(:,'yhat_fre')];
   SumPerf{i} = cryptoSim(tmwpredNotNormalize,'TrStpLoss',A.TrStpLoss,'TrLmtOrder',A.TrLmtOrder);
   perfTot(i)=sum([SumPerf{i}.profitTot]);
end
bar(A.normWin,perfTot);
xlabel('Norm. Window (% of price)');
ylabel('Gains over 6 month ($)')

% Build a SVM classification model
% % % %
%[SVMc]=BuildcSVM(tmw);

% Plot performances 
% % % %
plotPerf(tmwpred,'method','fitrensemble');
plotPerf(tmwpred,'method','fitcensemble');

tmwpredNotNormalize=[TMW.h(A.PredTimeIndex,:),tmwpred(:,'yhat_fre')];
SumPerf2 = cryptoSim(tmwpredNotNormalize)
