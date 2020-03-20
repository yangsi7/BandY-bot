function mcost = bgc1d_fc2minimize_cmaes_parallel(ParStart,FunArg)

 % Unfolds arguments
 ParNames = FunArg.ParNames;
 ParMin = FunArg.ParMin;
 ParNorm = FunArg.ParNorm;

 % Re-builds non-normalized parameters:
%ParVal = ParMin + ParStart .* ParNorm;
 ParVal = bsxfun(@plus,ParMin,bsxfun(@times,ParStart,ParNorm));

 % Allows for parallelization of cost function, accepting ParStart input of size NpxNm
 % Np: # parameters of the problem
 % Nm: # simultaneous calls

 [Np Nm] = size(ParStart);

 mcost = nan(1,Nm);

 parfor indm=1:Nm

   %disp(['Running bgc1d_iteration']);
    % Change parameters with those selected in Scenario_child(ichr).chromosome
   tstart=datetime('15-Sep-2019','Locale','en_US');
   tend=datetime('05-Jan-2020','Locale','en_US')
   ttime=timerange(tstart,tend,'closed');
   Rroot='/home/euphotic_/yangino-bot/';
   addpath(genpath(Rroot));
   [~,TMW]=IngestBinance('rroot',Rroot);
   [varnames,tmw] = CalcIndicators_andy(TMW.h,'Timeindex', ttime);
   %tables
   tcost = cryptoSimulation_andyopt(tmw,'slscale1',ParVal(1,indm),'slscale2',ParVal(3,indm),'slscale3',ParVal(3,indm),'slscale4',ParVal(4,indm));
    % Fill in parallel array of costs
    mcost(1,indm) = tcost;
    disp(['bgc1d_iteration - cost : ' num2str(tcost)]);
 end

