function [varnames,tmw,varnamesBad] = CalcIndicators(tmw,varargin)

% select all if no time index is provided
A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed'); 
 
A.ParamStruct = [];
 
% Default parameters
% ma
A.ma.windowsize = 15;
% ema
A.ema.windowsize = 15;
% T3
A.T3.v = 0.7;
%tsom
A.tsom.numperiod = 12;
% rsi
A.rsi.windowsize = 14;
%bollinger
A.bollin.windowsize=10;
A.bollin.matype = 0; % 0: normal, 1: linear moving average
A.bollin.numstd = 2; % Number of standard deviations for the upper and lower bounds
%price-volume-trend
A.pvt.windowsize=15;
%chaikvolat
A.chaikvolat.numperiods = 10;
A.chaikvolat.windowsize = 10;
% Jurik MA
A.jma.L=7;
A.jma.phi=50;
A.jma.pow=2;
A.adx=7;

A.Norm=0;

A=parse_pv_pairs(A,varargin);
if ~isempty(A.ParamStruct); A=A.ParamStruct;end;

ttmw=tmw;

% HLC average
returnFunc = @(open,high,low,close,volume) (high +low + close)/3;;
tmw = [tmw,rowfun(returnFunc,ttmw,'OutputVariableNames',{'hlc'})]; 

% exponential moving average 
endi=length(A.ema.windowsize);
for i = 1 : endi
    ema.(['w',num2str(A.ema.windowsize(i))]) = movavg(ttmw(:,'Close'),'exponential',A.ema.windowsize(i),'fill');
    ema.(['w',num2str(A.ema.windowsize(i))]).Properties.VariableNames{'Close'} = ['emaw',num2str(A.ema.windowsize(i))];
    tmw=[tmw,ema.(['w',num2str(A.ema.windowsize(i))])];

    % T3 moving average 
    emaema =  movavg(tmw(:,['emaw',num2str(A.ema.windowsize(i))]),'exponential',A.ema.windowsize(i),'fill');
    emaema.Properties.VariableNames{['emaw',num2str(A.ema.windowsize(i))]} = 'emaema';
    tmwtmp=[tmw(:,['emaw',num2str(A.ema.windowsize(i))]),emaema];
    %head(tmw)
    %returnFunc = @(open,high,low,close,volume,ema, emaema) 2*ema - emaema;
    %Inds.dema = rowfun(returnFunc,tmw,'OutputVariableNames',{'dema'});
    %tmw=[tmw,Inds.dema];
    %GD
    returnFunc = @(ema, emaema) ema + A.T3.v * (ema - emaema);
    GD1 = rowfun(returnFunc,tmwtmp,'OutputVariableNames',{'GD1'});
    ema1 = movavg(GD1(:,'GD1'),'exponential',A.ema.windowsize(i),'fill');
    ema1.Properties.VariableNames{'GD1'} = 'ema1';
    GD1=[GD1,ema1];
    emaema1 =  movavg(GD1(:,'ema1'),'exponential',A.ema.windowsize(i),'fill');
    emaema1.Properties.VariableNames{'ema1'} = 'emaema1';
    GD1=[GD1,emaema1];
    returnFunc = @(GD1,ema1, emaema1) ema1 + A.T3.v * (ema1 - emaema1);
    GD2 = rowfun(returnFunc,GD1,'OutputVariableNames',{'GD2'});
    ema2 = movavg(GD2(:,'GD2'),'exponential',A.ema.windowsize(i),'fill');
    ema2.Properties.VariableNames{'GD2'} = 'ema2';
    GD2=[GD2,ema2];
    emaema2 =  movavg(GD2(:,'ema2'),'exponential',A.ema.windowsize(i),'fill');
    emaema2.Properties.VariableNames{'ema2'} = 'emaema2';
    GD2=[GD2,emaema2];
    returnFunc = @(GD1,ema1, emaema1) ema1 + A.T3.v * (ema1 - emaema1);
    T3.(['w',num2str(A.ema.windowsize(i))]) = rowfun(returnFunc,GD2,'OutputVariableNames',{['T3w',num2str(A.ema.windowsize(i))]});
    tmw=[tmw,T3.(['w',num2str(A.ema.windowsize(i))])];
end

% simple moving average
endi=length(A.ma.windowsize);
for i = 1 : endi
    ma.(['w',num2str(A.ma.windowsize(i))]) = movavg(ttmw(:,'Close'),'simple',A.ma.windowsize(i),'fill');
    ma.(['w',num2str(A.ma.windowsize(i))]).Properties.VariableNames{'Close'} = ['maw',num2str(A.ma.windowsize(i))];
    tmw=[tmw,ma.(['w',num2str(A.ma.windowsize(i))])];
end
   % MACD
[macdLine, macdSline] = macd(ttmw);
macdLine.Properties.VariableNames{'Open'} ='macdLineOpen';
macdLine.Properties.VariableNames{'High'} ='macdLineHigh';
macdLine.Properties.VariableNames{'Low'} ='macdLineLow';
macdLine.Properties.VariableNames{'Close'} ='macdLineClose';
macdLine.Properties.VariableNames{'Volume'} ='macdLineVolume';

macdSline.Properties.VariableNames{'Open'} ='macdSlineOpen';
macdSline.Properties.VariableNames{'High'} ='macdSlineHigh';
macdSline.Properties.VariableNames{'Low'} ='macdSlineLow';
macdSline.Properties.VariableNames{'Close'} ='macdSlineClose';
macdSline.Properties.VariableNames{'Volume'} ='macdSlineVolume';

tmw=[tmw,macdLine,macdSline];

% tsmom -- momentum indicator
%tmw.Volume = []; % remove VOLUME field
MomTsom.(['np',num2str(A.tsom.numperiod)]) = tsmom(ttmw(:,'Close'),'NumPeriods',A.tsom.numperiod); 
MomTsom.(['np',num2str(A.tsom.numperiod)]).Properties.VariableNames{'Close'} = ['MomTsomnp',num2str(A.tsom.numperiod)];
tmw=[tmw,MomTsom.(['np',num2str(A.tsom.numperiod)])];

%ADX
endi=length(A.adx.windowsize);
for i = 1 : endi
	a=indicators([tmw.High,tmw.Low,tmw.Close],'adx');
	pdi=a(:,1);
	mdi=a(:,2);
	adx=a(:,3);
	tmw=addvars(tmw,pdi,'NewVariableNames',['pdiW',num2str(A.adx.windowsize(i))]);
	tmw=addvars(tmw,mdi,'NewVariableNames',['mdiW',num2str(A.adx.windowsize(i))]);
	tmw=addvars(tmw,adx,'NewVariableNames',['adxW',num2str(A.adx.windowsize(i))]);
end


%RSI
endi=length(A.rsi.windowsize);
for i = 1 : endi
    rsi.(['w',num2str(A.rsi.windowsize(i))]) = rsindex(ttmw(:,'Close'),'WindowSize',A.rsi.windowsize(i));
    rsi.(['w',num2str(A.rsi.windowsize(i))]).Properties.VariableNames{'RelativeStrengthIndex'} = ['rsiw',num2str(A.rsi.windowsize(i))];
    tmw=[tmw,rsi.(['w',num2str(A.rsi.windowsize(i))])];
end


%adline
ADline = adline(ttmw);
tmw=[tmw,ADline];

%bollinger
endi=length(A.bollin.windowsize);
for i = 1 : endi
    [middle.(['w',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)]),upper.(['w',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)]),lower.(['w',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)])]= bollinger(ttmw(:,'Close'),'WindowSize',A.bollin.windowsize(i),'Type',A.bollin.matype,'NumStd',A.bollin.numstd);
    middle.(['w',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)]).Properties.VariableNames{'Close'} =['BollMw',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)];
    upper.(['w',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)]).Properties.VariableNames{'Close'} =['BollUw',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)];
    lower.(['w',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)]).Properties.VariableNames{'Close'} =['BollLw',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)];

    tmw=[tmw,middle.(['w',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)]),upper.(['w',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)]),lower.(['w',num2str(A.bollin.windowsize(i)),'t',num2str(A.bollin.matype),'nstd',num2str(A.bollin.numstd)])];
end


%price-volume-trend
%endi=length(A.pvt.windowsize);
%for i = 1 : endi
%	pvTrend = pvtrend(ttmw);
%	tmp = movavg(pvTrend(:,'PriceVolumeTrend'),'simple',A.pvt.windowsize(i));
%	tmp.Properties.VariableNames{'PriceVolumeTrend'}=['anomPVTw',num2str(A.pvt.windowsize(i))];
%	tmw=[tmw,tmp];
%end


% chaiken volatility
endi=length(A.ema.windowsize);
for i = 1 : endi
    chaikVolat = chaikvolat(ttmw,'NumPeriods',A.chaikvolat.numperiods, 'WindowSize',A.chaikvolat.windowsize(i));
    chaikVolat.Properties.VariableNames{'ChaikinVolatility'} = ['CVw',num2str(A.chaikvolat.windowsize(i))];
    tmw=[tmw,chaikVolat];
end

% JMA
endi=length(A.jma.L);
for i = 1 : endi
   jma = JMA(tmw,'L',A.jma.L(i),'phi',A.jma.phi,'pow',A.jma.pow);
   tmw=addvars(tmw,jma,'NewVariableNames',{['jma_L',num2str(A.jma.L(i)),'Phi',num2str(A.jma.phi),'pow',num2str(A.jma.pow)]});
end

%tmw=tmw(A.TimeIndex,:);
varnames=(tmw.Properties.VariableNames);

varnamesBad={};
for i = 1 : length(varnames)
   if sum(tmw.(varnames{i})==inf|tmw.(varnames{i})==nan) >0
      varnamesBad=[varnamesBad;varnames{i}];
   end
end
