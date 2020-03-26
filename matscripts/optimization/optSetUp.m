function [BayesObject] = optSetUp(varargin)
A.onlysim = 0;
A=parse_pv_pairs(A,varargin);
if ~A.onlysim
        optimVars = [
            optimizableVariable('rfper',[15 35], 'Type','integer')
            optimizableVariable('rfmult',[0.5 3])
            optimizableVariable('rsiper',[15 35], 'Type','integer')
            optimizableVariable('jmaL',[10 35], 'Type','integer')
            optimizableVariable('jmaphi',[10 70], 'Type','integer')
            optimizableVariable('jmapow',[1 3], 'transform','log')
            optimizableVariable('adxper',[10 35], 'Type','integer')
            optimizableVariable('bollper',[10 35], 'Type','integer')
            optimizableVariable('macdfast',[3 15], 'Type','integer')
            optimizableVariable('macdsignal', [1 15],'Type','integer')
            optimizableVariable('macdlong', [1 15], 'Type','integer')
            optimizableVariable('sarinc',[0.1,0.9])
            optimizableVariable('sarmmax',[0.01,0.5])
            optimizableVariable('svolper',[15,80],'Type','integer')
            optimizableVariable('svolf',[1,2])
            optimizableVariable('slscale1', [0.001,5])
            optimizableVariable('slscale2', [0.5,3],'transform','log')
            optimizableVariable('slscale3', [0.001,5])
            optimizableVariable('slscale4', [0.5,3],'transform','log')
            optimizableVariable('slmax', [0.001,0.1])
            optimizableVariable('lstop',[0.001 0.05])
            optimizableVariable('sstop',[0.001 0.05])
            optimizableVariable('adxth',[5 60])
            optimizableVariable('rsiobos',[40 80])
                ];
else
        optimVars = [
            optimizableVariable('slscale1', [0.001,5])
            optimizableVariable('slscale2', [0.5,3],'transform','log')
            optimizableVariable('slscale3', [0.001,5])
            optimizableVariable('slscale4', [0.5,3],'transform','log')
            optimizableVariable('slmax', [0.001,0.1])
            optimizableVariable('lstop',[0.001 0.05])
            optimizableVariable('sstop',[0.001 0.05])
            optimizableVariable('adxth',[5 60])
            optimizableVariable('rsiobos',[40 80])
                ];

%            optimizableVariable('ftp',[0.25 0.75])
%            optimizableVariable('dnSL',[0 1],'Type','integer')
%            optimizableVariable('tp1',[0.001 0.01])
%            optimizableVariable('tp2',[0.005 0.05])
%            optimizableVariable('tp1scale',[0.01 0.2])
%            optimizableVariable('tp2scale',[0.01 0.2])
end

    ObjFcn = makeObjFcn();
    BayesObject = bayesopt(ObjFcn,optimVars, ...
        'MaxTime',24*60*60, ...
        'IsObjectiveDeterministic',true, ...
        'ExplorationRatio',0.75,...
        'AcquisitionFunctionName', 'expected-improvement-plus',...
        'NumSeedPoints',100,...
        'UseParallel',true,...
        'MaxObjectiveEvaluations',200);
