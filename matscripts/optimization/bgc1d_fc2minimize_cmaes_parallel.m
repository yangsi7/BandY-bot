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
   [varnames,tmw] = CalcIndicators_andy(TMW.h,'Timeindex', ttime,...
      'rfper'     ,round(ParVal(1,indm)),...
      'rsiper'    ,round(ParVal(3,indm)),...
      'jmaL'      ,round(ParVal(4,indm)),...
      'jmaphi'    ,round(ParVal(5,indm)),...
      'adxper'    ,round(ParVal(7,indm)),...
      'bollper'   ,round(ParVal(8,indm)),...
      'svolper'   ,round(ParVal(14,indm)),...
      'macdfast'  ,round(ParVal(9,indm)),...
      'macdsignal',round(ParVal(10,indm)),...
      'macdlong'  ,round(ParVal(11,indm)),...
      'rfmult'    ,ParVal(2,indm),...
      'jmapow'    ,ParVal(6,indm),...
      'sarinc'    ,ParVal(12,indm),...
      'sarmmax'   ,ParVal(13,indm),...
      'svolf'     ,ParVal(15,indm),...
      );
   %tables
   [gains, drawdown, ~,~] = cryptoSimulation_andyopt(tmw,...
      'slscale1',ParVal(16,indm),...
      'slscale2',ParVal(17,indm),...
      'slscale3',ParVal(18,indm),...
      'slscale4',ParVal(19,indm),...
      'slmax',ParVal(20,indm),...
      'lstop',ParVal(21,indm),...
      'sstop',ParVal(22,indm),...
      'adxth',ParVal(23,indm),...
      'rsiobos',ParVal(24,indm) ...
      )
    % Fill in parallel array of costs
    tcost = -sign(gains).*(gains.^2) + (drawdown).^6.5

    tcost(tcostr==inf)=10000.^2;
    tcost(isnan(tcost))=10000.^2;

    mcost(1,indm) = tcost;

    disp(['bgc1d_iteration - cost : ' num2str(tcost)]);
 end

