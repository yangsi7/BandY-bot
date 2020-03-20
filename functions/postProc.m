function tmwpred = postProcess(tmwpred,varargin)

%load('/Users/yangsi/Box Sync/Crypto/scripts/models/fre_11Dec2019.mat')
B.onlyBB=0;
B.PredTimeIndex = timerange(datetime('01-Jun-2019','Locale','en_US'),datetime('01-Jan-2200','Locale','en_US'),'closed');
B=parse_pv_pairs(B,varargin);

rmNan=600;

% Remove first hours to avoid nans
x=tmwpred.signal;
x1=x(rmNan:end);

% Filter trends
% Get trend and detrend
%windowSize=7*24;
%y1 = filterSY(x1,'windowSize',windowSize);

y11 = JMA2(x1,'L',8);

x2=x1-y11; % detrended

%windowSize2=14;
%y2 = filterSY(x2,'windowSize',windowSize2,'filter',1);
%
backNormWin2=5*24; % 2 weeks
shortTermSig= BackNorm(y11,'backNormWin',backNormWin2);
BB=nan(size(shortTermSig));
BB(2:end) = shortTermSig(2:end)-shortTermSig(1:end-1);
BB(BB>0)=1;BB(BB<=0)=0;

shortTermSig=[nan(rmNan-1,1);shortTermSig];
BB = [nan(rmNan-1,1);BB];

% % % %
tmwpred = addvars(tmwpred,shortTermSig,BB);

