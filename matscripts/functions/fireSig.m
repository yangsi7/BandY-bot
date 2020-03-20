function sig = FireSignalWithBB(varargin)
% % % % % % % % %  
% Fires Long and Short signals for use by the python Bot
%
% --Optional args 
% ---------------
A.rroot = '/home/euphotic_/yangino-bot/';
A.model='strat1';
A.PredTimeIndex = timerange(datetime('01-Jul-2019',...
   'Locale','en_US'),datetime('01-Jan-2200','Locale','en_US'),'closed');
A.Xwin=1;
A=parse_pv_pairs(A,varargin); % parse varargin
% ---------------

% retreive historical data
addpath(genpath(A.rroot));
[~,TMW]=IngestBinance('rroot',A.rroot);

% Calculate technical indicators
[varnames,tmw] = TA.strat1(TMW.h,'Timeindex', A.PredTimeIndex);

% Get long and short signals
[long, short] = strategy(tmw, 'strat', 'Andy');

presig = zeros(size(long));
presig(long)=1;
presig(short)=-1;
sig = presig(end-A.Xwin:end);

