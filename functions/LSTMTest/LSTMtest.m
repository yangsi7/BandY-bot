 Rroot='/home/euphotic_/yangino-bot/';
 addpath(genpath(Rroot));
 [~,TMW]=IngestBinance('rroot',Rroot);
 A.TrainTimeIndex = timerange(datetime('01-Jan-2019','Locale','en_US'),datetime('1-Jun-2019','Locale','en_US'),'closed');
 tmw = TMW.h(A.TrainTimeIndex,:);

 data = [tmw.Open,tmw.Close,tmw.Low,tmw.High,tmw.Volume]';

 [returnLong,returnShort] = calcreturn(tmw.Close,tmw.High,tmw.Low);

 returnLong(returnLong<0)=0;returnShort(returnShort<0)=0


% rreturn=returnLong; rreturn(rreturn<=0)=-returnShort(rreturn<=0);
 
 numTimeStepsTrain = floor(0.9*size(data,2));
 dataTrain = data(:,1:numTimeStepsTrain+1);
 dataTest = data(:,numTimeStepsTrain+1:end);

 Y = [returnLong,returnShort]';
 YTrain = Y(:,1:numTimeStepsTrain+1);
 Ytest = Y(:,numTimeStepsTrain+1:end);

 [dataStandardized,p] = stand2(data,'win',24*7);
 dataTrain = dataStandardized(:,1:numTimeStepsTrain+1);
 dataTest = dataStandardized(:,numTimeStepsTrain+1:end);

% XTrain = dataTrainStandardized(:,1:end-1);
% YTrain = dataTrainStandardized(:,2:end);

 XTrain = dataTrainStandardized;

 numFeatures = 5;
 numResponses = 2;
 numHiddenUnits = 200;

layers = [ ...
    sequenceInputLayer(numFeatures)
    lstmLayer(numHiddenUnits)
    fullyConnectedLayer(numResponses)
    regressionLayer];

options = trainingOptions('adam', ...
    'MaxEpochs',250, ...
    'GradientThreshold',1, ...
    'InitialLearnRate',0.005, ...
    'LearnRateSchedule','piecewise', ...
    'LearnRateDropPeriod',125, ...
    'LearnRateDropFactor',0.2, ...
    'Verbose',0, ...
    'Plots','training-progress');

net = trainNetwork(XTrain,YTrain,layers,options);

YPred = predict(net,dataTest);

XTest = dataTestStandardized(:,1:end-1);
net = predictAndUpdateState(net,XTrain);
[net,YPred] = predictAndUpdateState(net,YTrain(:,end));

numTimeStepsTest = numel(XTest);
for i = 2:100
    [net,YPred(:,i)] = predictAndUpdateState(net,YPred(:,i-1),'ExecutionEnvironment','cpu');
end
plot(YPred(1,100:300));hold on; plot(Ytest(1,100:300)); hold off;
