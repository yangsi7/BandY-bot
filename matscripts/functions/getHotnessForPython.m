function sig = getHotnessForPython(pyIn,varargin)
addpath(genpath('/Users/yangsi/Box Sync/UCLA/MATLAB'));
A.model='/Users/yangsi/Box Sync/Crypto/scripts/models/fre_26Nov2019.mat';
A = parse_pv_pairs(A,varargin);

ddat.open = pyIn(:,2);
ddat.high = pyIn(:,3);
ddat.low = pyIn(:,4);
ddat.close = pyIn(:,5);
ddat.volume = pyIn(:,6);
ddat.timestamp = pyIn(:,7);

% Convert to datenum (second timestamp since 0000-00-00)
ddat.datenum = ddat.timestamp./86400 + datenum(1970,1,1);
%ddat.datenum=ddat.timestamp;
%Convert to datetime
ddat.datetime = datetime(ddat.datenum,'ConvertFrom','datenum');
TMW.h = timetable(ddat.open,ddat.high,ddat.low,ddat.close,ddat.volume, ...
    'VariableNames',{'Open','High','Low','Close','Volume'},'RowTimes',ddat.datetime);

idx=find(TMW.h.Close ==0 | TMW.h.Open ==0);
if ~isempty(idx); TMW.h{idx,:}=nan; end;

TMW.h = fillmissing(TMW.h,'linear');   

% load model
load(A.model)

% First Get hotness
tmwNN = getHotness(TMW.h);
hotness=tmwNN.Hotness;
sig = hotness;

