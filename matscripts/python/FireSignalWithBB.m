function HotnessIdx = FireSignalWithBB(varargin)

%load('/Users/yangsi/Box Sync/Crypto/scripts/models/fre_11Dec2019.mat')
B.rroot = '/home/euphotic_/yangino-bot/';
B.model='StackedJan10.mat';
B.onlyBB=0;
B.PredTimeIndex = timerange(datetime('01-Jul-2019','Locale','en_US'),datetime('01-Jan-2200','Locale','en_US'),'closed');
B.Xwin=1;
B=parse_pv_pairs(B,varargin);

modelPath=[B.rroot,'models/',B.model];
ms = load(modelPath);
id='MATLAB:class:mustReturnObject';
warning('off',id);
load(modelPath);

[~,TMW]=IngestBinance;

% First Get hotness
tmwNN = getHotness(TMW.h);

tmwToPred=TMW.h(B.PredTimeIndex,:);
tt= tmwNN(B.PredTimeIndex,'Hotness');
tmwToPred=runStackedModel(tmwToPred,ms,'PredTimeIndex',B.PredTimeIndex);
tmwToPred=postProc(tmwToPred(1:end-1,:));

inds=tmwToPred.shortTermSig;
BB=nan(size(inds));
BB(2:end) = inds(2:end)-inds(1:end-1);
BB(BB>0)=1;BB(BB<=0)=0;
%HotnessIdx=[idShort,BB];
HotnessIdx=[inds(end-B.Xwin+1:end),BB(end-B.Xwin+1:end)];
