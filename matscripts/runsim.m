 Rroot='/home/euphotic_/yangino-bot/';
 addpath(genpath(Rroot));
 [~,TMW]=IngestBinance('rroot',Rroot);


% Technical indicator parameters
% % % %

 A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed');
 A.TrainTimeIndex = timerange(datetime('14-Sep-2019','Locale','en_US'),datetime('19-Jan-2020','Locale','en_US'),'closed');
 A.PredTimeIndex = timerange(datetime('01-Jan-2019','Locale','en_US'),datetime('05-Jan-2050','Locale','en_US'),'closed');

[varnames,tmw] = TA.strat1(TMW.h,'Timeindex', A.PredTimeIndex);
profit = cryptoSimulation_andy(tmw);

optimize_cmaes
