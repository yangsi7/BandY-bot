function [Mdl]=BuildcSVM(tmw,varargin)
A.TimeIndex = timerange(datetime('01-Jan-2018','Locale','en_US'),datetime('31-May-2018','Locale','en_US'),'closed');
A.normWin=150;
A=parse_pv_pairs(A,varargin);

tmw = tmw(A.TimeIndex,:);
idxNnan=~isnan(tmw.priceNorm(:));
tmw=tmw(idxNnan,:);

dpriceNorm = discretize(tmw.priceNorm,[0 0.2 0.8 1],'categorical');


X=[tmw.Open,tmw.Close,tmw.Low,tmw.High,tmw.Volume,tmw.hlc,tmw.ema,tmw.T3];
t = templateSVM('Standardize',true);
Mdl = fitcecoc(X,dpriceNorm,'Learners',t,'FitPosterior',true,'OptimizeHyperparameters','auto',...
    'HyperparameterOptimizationOptions',struct('AcquisitionFunctionName',...
    'expected-improvement-plus'));
