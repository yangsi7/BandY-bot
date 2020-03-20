Hotnessfunction [tmw, Mdlr, varnames] = buildModel(TMW, A,varargin)
B.TrainTimeIndex = timerange(datetime('01-Jan-2019','Locale','en_US'),datetime('14-Sep-2019','Locale','en_US'),'closed');
B.gainThresh=1.0;
B.normWinSize=[14*24, 0];
B.useNNPrice=0;
B=parse_pv_pairs(B,varargin);

ttmw=TMW.h;
% First Get hotness
tmwNN = getHotness(ttmw,'gainThresh',B.gainThresh);

% Normalize price
[tmw] = NormalizePrice(ttmw,'windowsize',B.normWinSize);

% Calulate technical indicators
% % % %
 [varnames,tmw]=CalcIndicators(tmw,'ParamStruct',A);
 [varnames, tmw] = GetIndsDtDdt(tmw,varnames);
 tmw = fillmissing(tmw,'linear');

 if B.useNNPrice
 	[varnamesNN,tmwNN]=CalcIndicators(tmwNN,'ParamStruct',A);
 	[varnamesNN, tmwNN] = GetIndsDtDdt(tmwNN,varnames);
 	tmw = synchronize(tmw,tmwNN);
	for i = 1 : length(varnamesNN)
		varnamesNN{i} = [varnamesNN{i},'_NN'];
	end
	varnames=[varnames,varnamesNN];
 end

% Add "Hotness Index"
% % % %
 tmw=[tmw,tmwNN(:,'Hotness')];

% Build a regression Forest
% % % %

 [Mdlr,impr]=BuildForest(tmw,'varnames',varnames,'TimeIndex',B.TrainTimeIndex,'PredictorImportance',0);
 net=BuildNet(tmw,Mdlr,'varnames',varnames,'TimeIndex',B.TrainTimeIndex);

