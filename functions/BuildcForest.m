function [Mdl]=BuildcForest(tmw,varargin)
A.TimeIndex = timerange(datetime('01-Jan-2019','Locale','en_US'),datetime('01-May-2019','Locale','en_US'),'closed');
A.normWin=150;
A.varnames={'Open','High','Low','Close','Volume'};
A=parse_pv_pairs(A,varargin);

tmw = tmw(A.TimeIndex,:);
idxNnan=~isnan(tmw.priceNorm(:));
tmw=tmw(idxNnan,:);
bbounds=[0 0.15 0.3 0.6 0.75 1];
dpriceNorm = discretize(tmw.priceNorm,bbounds,'categorical');

X=table2array(tmw(:,A.varnames));

cost.ClassNames = categories(dpriceNorm);
cost.ClassificationCosts = [0 5 5 5 5; 5 0 1 1 5; 5 1 0 1 5;5 1 1 0 5;5 5 5 5 0];

t = templateTree('MinLeafSize',1);
Mdl = fitcensemble(X,dpriceNorm,'Method','Bag','Learner',t,'NumLearningCycles',500);
%Mdl = fitcensemble(X,dpriceNorm,'OptimizeHyperparameters','auto','Learners',t, ...
%    'HyperparameterOptimizationOptions',struct('AcquisitionFunctionName','expected-improvement-plus','UseParallel',true))
