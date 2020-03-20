 Rroot='/home/euphotic_/yangino-bot/';
 addpath(genpath(Rroot));
 [~,TMW]=IngestBinance('rroot',Rroot);
 A.TrainTimeIndex = timerange(datetime('15-Sep-2019','Locale','en_US'),datetime('26-Jan-2020','Locale','en_US'),'closed');
 tmw = TMW.h;
 data = [tmw.Open,tmw.Close,tmw.Low,tmw.High,tmw.Volume]';
 indsX = [1,3,4,5];
 indsY=2;
 [dataStandardized,p] = stand2(data,'win',24*7);

 par.mmin=nanmin(dataStandardized(2,:));
 par.mmax=nanmax(dataStandardized(2,:));
 tmw.Open = minmaxnorm(dataStandardized(1,:),'par',par)';
 tmw.Close = minmaxnorm(dataStandardized(2,:),'par',par)';
 tmw.Low = minmaxnorm(dataStandardized(3,:),'par',par)';
 tmw.High = minmaxnorm(dataStandardized(4,:),'par',par)';
 tmw.Volume = minmaxnorm(dataStandardized(5,:),'par',par)';
 [varnames,tmw,varnamesBad] = CalcIndicatorsLSTM(tmw);
 tmw = tmw(A.TrainTimeIndex,:);
 dataStandardized2 = table2array(tmw)';


 % Normalize price
 ttmw=TMW.h;
 tmwNN = getHotnessNew(ttmw,'gainThresh',1.0);
 T = tmwNN(A.TrainTimeIndex,'Hotness');
 T=T.Hotness
 idZeroOne = find(T==0 | T == 1);


 T = T(idZeroOne(2):idZeroOne(end-1))';
 X = dataStandardized2(:,idZeroOne(2):idZeroOne(end-1));
% Calulate technical indicators 


 % Autoregression Time-Series Problem with a NAR Neural Network
 % Created Sat May 16 23:01:03 WAT 2015
 %
 % This script assumes this variable is defined:
 %
 %   PInput - feedback time series. 1050x1double
% inputSeries = num2cell(dataStandardized,1);
% targetSeries = num2cell(dataStandardized,1);
 inputSeriesPre = num2cell(X,1);
 targetSeriesPre = num2cell(T);
 test = 0.15;
 ndat = size(X,2);
 ntest = floor(ndat-ndat*test);
 inputSeries = inputSeriesPre(:,1:ntest);
 targetSeries = targetSeriesPre(1:ntest);
 inputSeriesTest = inputSeriesPre(:,ntest+1:end);
 targetSeriesTest = targetSeriesPre(ntest+1:end);
 % Choose a Training Function
 % 
 trainFcn = 'trainbr';  % Levenberg-Marquardt
 inputDelays = 1:5;
 feedbackDelays = 1:5;
 hiddenLayerSize = 10;
 net = narxnet(inputDelays,feedbackDelays,hiddenLayerSize,'open',trainFcn);
 % Prepare the Data for Training and Simulation
 % The function PREPARETS prepares time series data 
 % for a particular network, shifting time by the minimum 
 % amount to fill input states and layer states.
 % Using PREPARETS allows you to keep your original 
 % time series data unchanged, while easily customizing it 
 % for networks with differing numbers of delays, with
 % open loop or closed loop feedback modes.
 [inputs,inputStates,layerStates,targets] = ... 
     preparets(net,inputSeries,{},targetSeries);
 
 % Set up Division of Data for Training, Validation, Testing
 net.layers{1}.transferFcn = 'tansig';
 net.layers{2}.transferFcn= 'tansig'
 net.inputs{1}.processFcns = {'removeconstantrows','mapminmax'}
 net.output.processFcns = {'removeconstantrows','mapminmax'}

 net.divideFcn = 'divideblock';
 net.divideParam.trainRatio = 80/100;
 net.divideParam.valRatio = 20/100;
 net.divideParam.testRatio = 0/100;
 net.trainParam.max_fail=6;
 
 % Train the Network
 [net,tr] = train(net,inputs,targets,inputStates,layerStates);
 [y1,xf,af] = net(inputs,inputStates,layerStates);
 [netc] = closeloop(net);


 [inputs,inputStates,layerStates,targets] = ...
     preparets(netc,inputSeriesTest,{},targetSeriesTest);
outputs= netc(inputs,inputStates,layerStates);

 [outputs] = net(inputs,inputStates,layerStates);
 figure
plot(cell2mat(outputs));hold on; grid on;
plot(cell2mat(targetSeriesTest)); hold off;


 errors = gsubtract(targets,outputs);
 performance = perform(net,targets,outputs)
 
 % Test the Network
  [inputs,inputStates,layerStates,targets] = ...
      preparets(netc,inputSeriesTest,{},{});
 netc = closeloop(net);
 [outputs,xf,af] = net(inputs,inputStates,layerStates);
 errors = gsubtract(targets,outputs);
 performance = perform(net,targets,outputs)

% Closed Loop Network
% Use this network to do multi-step prediction.
% The function CLOSELOOP replaces the feedback input with a direct
% connection from the output layer.
net2 = removedelay(net);
[netc,xic,aic] = closeloop(net,xf,af);

netc.name = [net.name ' - Closed Loop'];
view(netc)
[xc,xic,aic,tc] = preparets(netc,inputSeries,{},targetSeries);
for i = 1 : 20
   [xc,xic,aic] = netc(xc,xic,aic);
end

closedLoopPerformance = perform(netc,tc,yc)






 [returnLong,returnShort] = calcreturn(tmw.Close,tmw.High,tmw.Low);

 rreturnLong = returnLong;
 rreturnShort = returnShort;
 idxbestLong = returnLong>=returnShort;
 idxbestShort = returnLong<returnShort;

 nrreturn = nan(size(returnLong));
 nrreturn(idxbestLong) = returnLong(idxbestLong);
 nrreturn(idxbestShort) = -returnShort(idxbestShort);
 crreturn=nan(size(nrreturn));
 
 crreturn(nrreturn>-0.005 & nrreturn<0.005) = 0;
 crreturn(nrreturn>=0.005 &  nrreturn<0.01) = 1;
 crreturn(nrreturn>=0.01) = 2;
 crreturn(nrreturn<=-0.005 & nrreturn>-0.01) = -1;
 crreturn(nrreturn<=-0.01) = -2;




% rreturn=returnLong; rreturn(rreturn<=0)=-returnShort(rreturn<=0);
 
 numTimeStepsTrain = floor(0.8*size(data,2));
 dataTrain = data(:,1:numTimeStepsTrain+1);
 dataTest = data(:,numTimeStepsTrain+1:end);

 YTrain = crreturn(1:numTimeStepsTrain+1);
 Ytest = crreturn(numTimeStepsTrain+1:end);

 [dataStandardized,p] = stand2(data,'win',24*7);
  XTrain =dataStandardized(:,1:numTimeStepsTrain+1);
  XTest=dataStandardized(:,numTimeStepsTrain+1:end);
 
 %par.mmin=nanmin(dataStandardized(2,:));
 %par.mmax=nanmax(dataStandardized(2,:));
 %tmw.Open = minmaxnorm(dataStandardized(1,:),'par',par)';
 %tmw.Close = minmaxnorm(dataStandardized(2,:),'par',par)';
 %tmw.Low = minmaxnorm(dataStandardized(3,:),'par',par)';
 %tmw.High = minmaxnorm(dataStandardized(4,:),'par',par)';
 %tmw.Volume = minmaxnorm(dataStandardized(5,:),'par',par)';
 %[varnames,tmw,varnamesBad] = CalcIndicatorsLSTM(tmw);
 %
 %dataStandardized2 = table2array(tmw)';
 %dataStandardized2 = (dataStandardized2 - nanmean(dataStandardized2,2))./nanstd(dataStandardized2,0,2);
 %idxnan=find(isnan(dataStandardized2(:)));
 %dataTrain = dataStandardized2(:,1:numTimeStepsTrain+1);
 %dataTest = dataStandardized2(:,numTimeStepsTrain+1:end); 
% dataTrain = dataStandardized(:,1:numTimeStepsTrain+1);
% dataTest = dataStandardized(:,numTimeStepsTrain+1:end);

% XTrain = dataTrainStandardized(:,1:end-1);
% YTrain = dataTrainStandardized(:,2:end);

% XTrain = dataTrain(1:5,:);
% toTest = dataTest(1:5,:);

 numFeatures = 5;
 numResponses = 5;
 numHiddenUnits = 100;

layers = [ ...
    sequenceInputLayer(numFeatures)
    lstmLayer(numHiddenUnits)
    dropoutLayer(0.2)
    lstmLayer(numHiddenUnits)
    dropoutLayer(0.2)
    fullyConnectedLayer(numResponses)
    softmaxLayer
    classificationLayer]

miniBatchSize = 27;
maxEpochs = 2000 
options = trainingOptions('adam', ...
    'ExecutionEnvironment','cpu', ...
    'MaxEpochs',maxEpochs, ...
    'GradientThreshold',1, ...
    'Verbose',false, ...
    'Plots','training-progress');

YCat=categorical(YTrain)';

net = trainNetwork(XTrain,YCat,layers,options);

YPred = predict(net,dataTest);
YPred = classify(net,XTest);
XTest = dataTestStandardized(:,1:end-1);
net = predictAndUpdateState(net,XTrain);
[net,YPred] = predictAndUpdateState(net,YTrain(:,end));

numTimeStepsTest = numel(XTest);
for i = 2:100
    [net,YPred(:,i)] = predictAndUpdateState(net,YPred(:,i-1),'ExecutionEnvironment','cpu');
end
plot(YPred);hold on; plot(categorical(Ytest)); hold off;
