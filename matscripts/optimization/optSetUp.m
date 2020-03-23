function [BayesObject] = optSetUp(tmw,varargin)
A.opt = 1;
A=parse_pv_pairs(A,varargin);

        optimVars = [
            optimizableVariable('LearnRateDropFactor',[0.01 0.9])
            optimizableVariable('LearnRateDropPeriod',[1 100], 'Type','integer')
            optimizableVariable('InitialLearnRate',[1e-7 0.9],'Transform','log')
            optimizableVariable('MiniBatchSize',[8000 15000],'Type','integer')
            optimizableVariable('gdf',[0.5 0.99],'Transform','log')
            optimizableVariable('sgdf',[0.9 0.99999],'Transform','log')
            optimizableVariable('L2Regularization',[1e-10 1e-5],'Transform','log')
            optimizableVariable('initdropoutRate',[0.01 0.99])
            optimizableVariable('dropoutRate',[0.01 0.99])
            optimizableVariable('Size',[10 100],'Type','integer')
            optimizableVariable('GradientThreshold',[0.1 10.0])
            optimizableVariable('numLayers',[1 8],'Type','integer')
                ];
    ObjFcn = makeObjFcn(tmw);
    BayesObject = bayesopt(ObjFcn,optimVars, ...
        'MaxTime',14*60*60, ...
        'IsObjectiveDeterministic',false, ...
        'UseParallel',true,...
        'MaxObjectiveEvaluations',150);
~
