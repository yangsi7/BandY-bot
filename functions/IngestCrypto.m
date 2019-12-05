function [ddat,TMW] = IngestCrypto(varargin)
addpath(genpath('/Users/yangsi/Box Sync/UCLA/MATLAB'));
A.resample={'m','m15','h','h4','d','w'};
A.csvpath = '/Users/yangsi/Box Sync/Crypto/Data/Bitfitnex/Minute/392-crypto-currency-pairs-at-minute-resolution/btcusd.csv';
A = parse_pv_pairs(A,varargin);

ddat.raw=csvread(A.csvpath,1,0);
ddat.open = ddat.raw(:,2);
ddat.close = ddat.raw(:,3);
ddat.high = ddat.raw(:,4);
ddat.low = ddat.raw(:,5);
ddat.volume = ddat.raw(:,6);

% Millisecond timestamp since 1970-01-01
ddat.militime = ddat.raw(:,1);
% Convert to datenum (second timestamp since 0000-00-00)
ddat.datenum = ddat.militime/86400000 + datenum(1970,1,1);
%Convert to datetime
ddat.datetime = datetime(ddat.datenum,'ConvertFrom','datenum');

% Create a timetable from minute vector input
TMW.m = timetable(ddat.open,ddat.high,ddat.low,ddat.close,ddat.volume, ...
    'VariableNames',{'Open','High','Low','Close','Volume'},'RowTimes',ddat.datetime);

idx=find(TMW.m.Close ==0 | TMW.m.Open ==0);
if ~isempty(idx); TMW.m{idx,:}=nan; end;

TMW.m = fillmissing(TMW.m,'linear');

if sum(strcmp(A.resample,'m15'))==1
	m15Open = retime(TMW.m(:,'Open'),'regular','firstvalue','TimeStep',minutes(15));
	m15High = retime(TMW.m(:,'High'),'regular','max','TimeStep',minutes(15));
	m15Low = retime(TMW.m(:,'Low'),'regular','min','TimeStep',minutes(15));
	m15Close = retime(TMW.m(:,'Close'),'regular','lastvalue','TimeStep',minutes(15));
	TMW.m15 = [m15Open,m15High,m15Low,m15Close];
	TMW.m15 = synchronize(TMW.m15,TMW.m(:,'Volume'),'regular','sum','TimeStep',minutes(15));
        idx=find(TMW.m15.Close ==0 | TMW.m15.Open ==0);	
	if ~isempty(idx); TMW.m15{idx,:}=nan;end;
	TMW.m15 = fillmissing(TMW.m15,'linear');
end

if sum(strcmp(A.resample,'h'))==1
	hOpen = retime(TMW.m(:,'Open'),'hourly','firstvalue');
	hHigh = retime(TMW.m(:,'High'),'hourly','max');
	hLow = retime(TMW.m(:,'Low'),'hourly','min');
	hClose = retime(TMW.m(:,'Close'),'hourly','lastvalue');
	TMW.h = [hOpen,hHigh,hLow,hClose];
	TMW.h = synchronize(TMW.h,TMW.m(:,'Volume'),'hourly','sum');
        idx=find(TMW.h.Close ==0 | TMW.h.Open ==0);
	if ~isempty(idx); TMW.h{idx,:}=nan;end;
	TMW.h = fillmissing(TMW.h,'linear');
end

if sum(strcmp(A.resample,'h4'))==1
	h4Open = retime(TMW.m(:,'Open'),'regular','firstvalue','TimeStep',hours(4));
	h4High = retime(TMW.m(:,'High'),'regular','max','TimeStep',hours(4));
	h4Low = retime(TMW.m(:,'Low'),'regular','min','TimeStep',hours(4));
	h4Close = retime(TMW.m(:,'Close'),'regular','lastvalue','TimeStep',hours(4));
	TMW.h4 = [h4Open,h4High,h4Low,h4Close];
	TMW.h4 = synchronize(TMW.h4,TMW.m(:,'Volume'),'regular','sum','TimeStep',hours(4));
        idx=find(TMW.h4.Close ==0 | TMW.h4.Open ==0);
	if ~isempty(idx);TMW.h4{idx,:}=nan;end;	
	TMW.h4 = fillmissing(TMW.h4,'linear');
end

if sum(strcmp(A.resample,'w'))==1
	wOpen = retime(TMW.m(:,'Open'),'weekly','firstvalue');
	wHigh = retime(TMW.m(:,'High'),'weekly','max');
	wLow = retime(TMW.m(:,'Low'),'weekly','min');
	wClose = retime(TMW.m(:,'Close'),'weekly','lastvalue');
	TMW.w = [wOpen,wHigh,wLow,wClose];
	TMW.w = synchronize(TMW.w,TMW.m(:,'Volume'),'weekly','sum');
        idx=find(TMW.w.Close ==0 | TMW.w.Open ==0);
	if ~isempty(idx);TMW.w{idx,:}=nan;end;	
	TMW.w = fillmissing(TMW.w,'linear');
end

if sum(strcmp(A.resample,'d'))==1
	dOpen = retime(TMW.m(:,'Open'),'daily','firstvalue');
	dHigh = retime(TMW.m(:,'High'),'daily','max');
	dLow = retime(TMW.m(:,'Low'),'daily','min');
	dClose = retime(TMW.m(:,'Close'),'daily','lastvalue');
	TMW.d = [dOpen,dHigh,dLow,dClose];
	TMW.d = synchronize(TMW.d,TMW.m(:,'Volume'),'daily','sum');
        idx=find(TMW.d.Close ==0 | TMW.d.Open ==0);
	if ~isempty(idx);TMW.d{idx,:}=nan;end;	
	TMW.d = fillmissing(TMW.d,'linear');
end

if sum(strcmp(A.resample,'m'))~=1
	clear TMW.m;
end
