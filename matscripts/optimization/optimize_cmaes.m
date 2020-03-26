
AllParam = {
                'rfper',               15,                    35;            ...
                'rfmult',              0.5,                   3;            ...
                'rsiper',              15,                    35;            ...
                'jmaL',                10,                    35;            ...
                'jmaphi',              10,                    70;            ...
                'jmapow',              1,                     3;            ...
                'adxper',              10,                    35;            ...
                'bollper',             10,                    35;            ...
                'macdfast',            3,                     15;            ...
                'macdsignal',          1,                     15;            ...
                'macdlong',            1,                     15;            ...
                'sarinc',              0.1,                   0.9;            ...
                'sarmmax',             0.01,                  0.5;            ...
                'svolper',             15,                    80;            ...
                'svolf',               1,                     2;            ...
                'slscale1',            0.001,                 5;            ...
                'slscale2',            0.5,                   3;            ...
                'slscale3',            0.001,                 5;            ...
                'slscale4',            0.5,                   3;            ...
                'slmax',              0.001,                  0.1;            ...
                'lstop',              0.001,                  0.05;            ...
                'sstop',              0.001,                  0.05;            ...
                'adxth',              5,                      60;            ...
                'rsiobos',            40,                     80;            ...
                };

 ParNames = AllParam(:,1);
 nPar = size(ParNames,1); % number of parameters

 ParMin = [AllParam{:,2}]';
 ParMax = [AllParam{:,3}]';


% Initialize final output structure
 Optim.ParNames = ParNames;
 Optim.ParMin = ParMin;
 Optim.ParMax = ParMax;

% NOTES:
% (1) Parameters are normalized by subtracting the min and dividing by
%     a normalization factor, typically the range (so they are b/w 0-1)
%     This is done to allow the CMAES algorithm to work in the space [0 1]
% (2) If needed, remember to add the constraint:
%     Constraints: KDen1 + KDen2 + KDen3 = remin
%     This should be done in the cost function (bgc1d setup step)
%     as an ad-hoc constraint (removes one degree of freedom)
%     Remember to remove the corresponding K from the parameter pool!
%     (suggestion: remove KDen1, since first step drives everuthing)
% Calculates useful quantities for normalization, optimization, etc.
 ParMean = (ParMin + ParMax)/2';
 ParRange = ParMax - ParMin;
 ParNorm = ParRange;
%ParStart = (ParMean - ParMin) ./ ParNorm;
 ParStart = rand(nPar,1);
 ParSigma = ParRange./ParNorm/sqrt(12);

% Options
 optn.EvalParallel = '1';
 optn.LBounds = (ParMin - ParMin) ./ ParNorm;
 optn.UBounds = (ParMax - ParMin) ./ ParNorm;
 optn.MaxFunEvals = 2000;

% Enables parallelization
% Note, the # of cores should be the same as the population size of the CMAES:
% Popul size: 4 + floor(3*log(nPar))
 if strcmp(optn.EvalParallel,'1')
    FunName = 'bgc1d_fc2minimize_cmaes_parallel';
    delete(gcp('nocreate'))
    npar = 4;
    ThisPool = parpool('local',npar);
 else
    FunName = 'bgc1d_fc2minimize_cmaes';
 end
 FunArg.ParNames = ParNames;
 FunArg.ParMin = ParMin;
 FunArg.ParNorm = ParNorm; 
    % Runs the optimization
 tic;
 [pvarout, pmin, counteval, stopflag, out, bestever] = cmaes(FunName,ParStart,ParSigma,optn,FunArg);

% Stops parallel pool
 if strcmp(optn.EvalParallel,'1')
    delete(ThisPool);
 end

% Fills in some output in final structure
% NOTE: instead of saving last iteration, saves best solution
 % Renormalized parameters
 Optim.ParNames = ParNames;
 Optim.ParOpt = ParMin + ParNorm .* bestever.x;
