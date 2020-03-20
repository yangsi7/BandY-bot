% % % % % % % % % % % % % % % % % % % %
% % % % Yangino Crypto Bot  % % % % % % 
% % % % % % % % % % % % % % % % % % % %

% Add data and functions Paths
% % % % 
 Rroot='/home/euphotic_/yangino-bot/';
 addpath(genpath(Rroot));
 [~,TMW]=IngestBinance('rroot',Rroot);

 
% Technical indicator parameters
% % % %

 A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed');
 A.TrainTimeIndex = timerange(datetime('14-Sep-2019','Locale','en_US'),datetime('19-Jan-2020','Locale','en_US'),'closed');
 A.PredTimeIndex = timerange(datetime('15-Sep-2019','Locale','en_US'),datetime('05-Jan-2050','Locale','en_US'),'closed'); 
  A.PredTimeIndex = timerange(datetime('01-Jul-2018','Locale','en_US'),datetime('31-Dec-2018','Locale','en_US'),'closed');
 % ma
 A.ma.windowsize = 15;
 % ema
 A.ema.windowsize = [6, 12, 24, 48, 96];%[5  10 15 30 50];
 % T3
 A.T3.v = 0.7;
 %tsom
 A.tsom.numperiod = 12;
 % rsi
 A.rsi.windowsize = [6, 12, 24, 48, 96];%[5  10 15 30 50];
 %bollinger
 A.bollin.windowsize=[6, 12, 24, 48, 96];%[5  10 15 30 50];
 A.bollin.matype = 0; % 0: normal, 1: linear moving average
 A.bollin.numstd = 2; % Number of standard deviations for the upper and lower bounds
 %PVT
 A.pvt.windowsize=[7, 15, 30];
 %chaikvolat
 A.chaikvolat.numperiods = 10;
 A.chaikvolat.windowsize = [6, 12, 24, 48, 96];%[5  10 15 30 50];
 % Jurik MA
 A.jma.L=[6, 12, 24, 48, 96];
 A.jma.phi=50;
 A.jma.pow=2;

 A.adx.windowsize=[6, 12, 24, 48, 96];
 A.macd.scale=[0.5,1,2];
 A.T3.volfact = [0.5, 0.7, 0.9]

 A.cci.ws=[6, 12, 24, 48, 96];
 A.cci.cst=0.015;

 A.mfi.ws = [6, 12, 24, 48, 96];

 A.sar.scale=[0.5, 1, 2];

 A.gainThresh=1.0;
 A.normWinSize1=[30*24, 0];
 A.normWinSize2=[15*24, 0];

 % Normalize price
 ttmw=TMW.h;

 tmwNN = getHotness(ttmw,'gainThresh',A.gainThresh);
% Calulate technical indicators
% % % %
 [tmw1] = NormalizePrice(ttmw,'windowsize',A.normWinSize1);
 [varnames1,tmw1,varnamesBad]=CalcIndicators2(tmw1,'ParamStruct',A);
 [varnames1, tmw1] = GetIndsDtDdt(tmw1,varnames1);
 tmw1=[tmw1,tmwNN(:,'Hotness')];
 [Mdlr1,varSelect1]=BuildForest(tmw1,'varnames',varnames1,'TimeIndex',A.TrainTimeIndex,'PredictorImportance',1);
 [tmwpred1]=PredBuyIdx(tmw1,Mdlr1,'varnames',varSelect1,'method','fitrensemble','TimeIndex',A.TrainTimeIndex);
 wins=[7,15,30,60,120,240];
 sigProcVar={'yhat_fre'};
 for i = 1: length(wins)   
    tmpSig = indicators(tmwpred1.yhat_fre,'ema',wins(i));
    tmwpred1 = addvars(tmwpred1,tmpSig,'NewVariableNames',['yhat_freW',num2str(wins(i))]);
    sigProcVar=[sigProcVar,['yhat_freW',num2str(wins(i))]];
 end


 [tmw2] = NormalizePrice(ttmw,'windowsize',A.normWinSize2);
 [varnames2,tmw2,varnamesBad]=CalcIndicators2(tmw2,'ParamStruct',A);
 [varnames2, tmw2] = GetIndsDtDdt(tmw2,varnames2);
 tmw2=[tmw2,tmwNN(:,'Hotness')];
 [Mdlr2,varSelect2]=BuildForest(tmw2,'varnames',varnames2,'TimeIndex',A.TrainTimeIndex,'PredictorImportance',1);
 [tmwpred2]=PredBuyIdx(tmw2,Mdlr2,'varnames',varSelect2,'method','fitrensemble','TimeIndex',A.TrainTimeIndex);
  for i = 1: length(wins)
    tmpSig = indicators(tmwpred2.yhat_fre,'ema',wins(i));
    tmwpred2 = addvars(tmwpred2,tmpSig,'NewVariableNames',['yhat_freW',num2str(wins(i))]);
 end
 
 netVarSelect=50;
 XX=[table2array(tmwpred1(:,[varSelect1(1:netVarSelect),sigProcVar])),table2array(tmwpred2(:,[varSelect2(1:netVarSelect),sigProcVar]))]';
 
 xx=XX(:,wins(end):end);
 yy=tmwpred1.Hotness(wins(end):end)';
 net = fitnet([10]);
 net.divideFcn = 'divideind';
 [trainInd, valInd, testInd]=dividIndsCycle(yy,'nblocks',2000,'nsplit',[0.6,0.2,0.2]);
 net.divideParam.trainInd = trainInd;
 net.divideParam.valInd   = valInd;
 net.divideParam.testInd  = testInd;
 net = train(net,xx,yy);


 
  varNames.varSelect1 =varSelect1;
  varNames.varSelect2 =varSelect2;
  varNames.sigProcVar =sigProcVar;  
  varParams.wins=[7,15,30,60,120,240];
  varParams.netVarSelect = netVarSelect;
  varParams.normWinSize1 = A.normWinSize1;
  varParams.normWinSize2 = A.normWinSize2;
  save('~/yangino-bot/models/StackedJan20.mat','Mdlr1','Mdlr2','net','varNames','varParams','A');
  ms = load('~/yangino-bot/models/StackedJan10.mat');
  tmwToPred=TMW.h(A.PredTimeIndex,:);
  tt= tmwNN(A.PredTimeIndex,'Hotness'); 
  tmwToPred=runStackedModel(tmwToPred,ms,'PredTimeIndex',A.PredTimeIndex);
  tmwToPred=postProc(tmwToPred);

  function plotResults(tmwNN,tmwToPred)
  % time range to plot
   tstart=datetime('01-Aug-2018','Locale','en_US');
   tend=datetime('30-Sep-2018','Locale','en_US')
   ttime=timerange(tstart,tend,'closed')

  %tables
   tmwplot=tmwNN(ttime,:);
   tmwplotSig=tmwToPred(ttime,:);
   x=tmwplotSig.shortTermSig;
   dsig=nan(size(x));
   for i = 4:length(x)
      dsig(i) = (2*x(i) - 5*x(i-1)+4*x(i-2)-x(i-3));
   end
   longT = [0.1];
   ShortT=[0.9];
   BuySigs = false(size(tmwplotSig.shortTermSig));
   SellSigs = false(size(tmwplotSig.shortTermSig));

   BuyClose=BuySigs;
   SellClose=SellSigs;
   Bull = tmwplotSig.shortTermSig <longT(1) ;
   Bear = tmwplotSig.shortTermSig >ShortT(1);   
   dsig(tmwplotSig.shortTermSig <longT(1) | tmwplotSig.shortTermSig >ShortT(1))=0;
   for i = 2 : length(tmwplotSig.shortTermSig)
      if Bull(i) & tmwplotSig.shortTermSig(i)>tmwplotSig.shortTermSig(i-1)
         BuySigs(i)=true;
      end
      if Bear(i) & tmwplotSig.shortTermSig(i) < tmwplotSig.shortTermSig(i-1)
         SellSigs(i)=true;
      end
   end

   BuyClose(dsig*7<-0.5)=true;
   SellClose(dsig*7>0.5)=true; 
   



%   BuySigs = tmwplotSig.shortTermSig <0.1;
%   SellSigs = tmwplotSig.shortTermSig >0.9;   

   subplot(2,1,1)
   p1=plot(tmwplot.Time,tmwplot.Close); hold on;
   p2= scatter(tmwplot.Time(BuySigs),tmwplot.Close(BuySigs),'^','filled');
   p2.MarkerFaceColor=[65, 145, 80]/255; % Green
   p2.MarkerEdgeColor='k';
   p3= scatter(tmwplot.Time(SellSigs),tmwplot.Close(SellSigs),'^','filled');
   p3.MarkerFaceColor=[179, 48, 48]/255; % Green
   p3.MarkerEdgeColor='k';  
   p4= scatter(tmwplot.Time(SellClose),tmwplot.Close(SellClose),'o','filled');
   p4.MarkerFaceColor=[65, 145, 80]/255; % Green
   p4.MarkerEdgeColor='k';
   p5= scatter(tmwplot.Time(BuyClose),tmwplot.Close(BuyClose),'o','filled');
   p5.MarkerFaceColor=[179, 48, 48]/255; % Green
   p5.MarkerEdgeColor='k';

   xlim([datetime('01-Aug-2018','Locale','en_US'),datetime('30-Sep-2018','Locale','en_US')])
   hold off;
   subplot(2,1,2)
   plot(tmwplotSig.Time,tmwplotSig.shortTermSig); hold on;
   plot(tmwplotSig.Time,tmwplotSig.signal); 
   plot(tmwplotSig.Time,dsig*7);
   hold off;
   xlim([datetime('01-Aug-2018','Locale','en_US'),datetime('30-Sep-2018','Locale','en_US')])

   ttmw=TMW.h;
   tmwNN = getHotness(ttmw,'gainThresh',A.gainThresh);      
   ms = load('~/yangino-bot/models/StackedJan10.mat');

%   tstart=datetime('01-Aug-2018','Locale','en_US');
%   tend=datetime('30-Sep-2018','Locale','en_US')
   tstart=datetime('15-Sep-2019','Locale','en_US');
   tend=datetime('05-Jan-2020','Locale','en_US')
   ttime=timerange(tstart,tend,'closed')
   tmwToPred=TMW.h(ttime,:);  
   tmwToPred=runStackedModel(tmwToPred,ms,'PredTimeIndex',ttime);
   tmwToPred=postProc(tmwToPred);
   %tables
   tmwplot=tmwNN(ttime,:);
   tmwplotSig=tmwToPred(ttime,:);  
   yhat_fre = tmwplotSig.shortTermSig;
   BB = tmwplotSig.BB;
   tmwplot = addvars(tmwplot,yhat_fre,BB);
   a = cryptoSimulation(tmwplot)
   plot(tmwplot.Time,a.Funds)
      SumPerf{i} = cryptoSim(tmwpredNotNormalize,'TrStpLoss',A.TrStpLoss(i),'TrLmtOrder',A.TrLmtOrder(i));
      perfTot(i)=sum([SumPerf{i}.profitTot]);


 end

  plot(tt.Hotness);hold on;
  plot(sig1);
  plot(sig2);
  plot(signal,'k','LineWidth',2);hold off;

 

 [tmwpred2]=PredBuyIdx(tmw,Mdlr2,'varnames',varnames2,'method','fitrensemble','TimeIndex',A.TrainTimeIndex);




 [varnames,tmwNN,varnamesBad]=CalcIndicators(ttmw,'ParamStruct',A);
 [varnames, tmwNN] = GetIndsDtDdt(tmwNN,varnames);

 % First Get hotness
 tmwNN = getHotness(ttmw,'gainThresh',A.gainThresh);



[tmw, Mdlr, varnames]=buildModels(TMW,A,'TrainTimeIndex',A.TrainTimeIndex);
save('/home/euphotic_/yangino-bot/models/fre_futures_9Jan2019_version1.mat','Mdlr','A');
[tmwpred]=PredBuyIdx(tmw,Mdlr,'varnames',varnames,'method','fitrensemble','TimeIndex',A.PredTimeIndex);
tmwpred=postProc(tmwpred);
tmwpredNotNormalize=synchronize(TMW.h(A.PredTimeIndex,:),tmwpred(:,{'yhat_fre','signal','BB','adxW15','pdiW15','mdiW15'}));

sumPerf=cryptoSim(tmwpredNotNormalize,'strategy','yhat_fre','thrLong',0.25,'thrShort',0.7);

[tmwpred]=PredBuyIdx(tmw,Mdlr,'varnames',varnames,'method','fitrensemble','TimeIndex',A.PredTimeIndex);

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
