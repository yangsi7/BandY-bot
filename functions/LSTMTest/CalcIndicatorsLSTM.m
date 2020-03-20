function [varnames,tmw,varnamesBad] = CalcIndicators(tmw,varargin)

% select all if no time index is provided
A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed'); 
 
A.ParamStruct = [];
 
% Default parameters
% ma
%price-volume-trend
A.Norm=0;
 A.ma.windowsize = 15;
 % ema
 A.ema.windowsize = [6, 12, 24, 48, 96];%[5  10 15 30 50];
 % T3
 A.T3.v = 0.7;
 %tsom
 A.tsom.numperiod = 12;
 % rsi
 A.rsi.windowsize = [6, 12, 24, 48, 96];%[5  10 15 30 50];
 %bollinger
 A.bollin.windowsize=[6, 12, 24, 48, 96];%[5  10 15 30 50];
 A.bollin.matype = 0; % 0: normal, 1: linear moving average
 A.bollin.numstd = 2; % Number of standard deviations for the upper and lower bounds
 %PVT
 A.pvt.windowsize=[7, 15, 30];
 %chaikvolat
 A.chaikvolat.numperiods = 10;
 A.chaikvolat.windowsize = [6, 12, 24, 48, 96];%[5  10 15 30 50];
 % Jurik MA
 A.jma.L=[6, 12, 24, 48, 96];
 A.jma.phi=50;
 A.jma.pow=2;

 A.adx.windowsize=[6, 12, 24, 48, 96];
 A.macd.scale=[0.5,1,2];
 A.T3.volfact = [0.5, 0.7, 0.9]

 A.cci.ws=[6, 12, 24, 48, 96];
 A.cci.cst=0.015;

 A.mfi.ws = [6, 12, 24, 48, 96];

 A.sar.scale=[0.5, 1, 2];

A=parse_pv_pairs(A,varargin);
if ~isempty(A.ParamStruct); A=A.ParamStruct;end;

ttmw=tmw;

% HLC average
returnFunc = @(open,high,low,close,volume) (high +low + close)/3;;
tmw = [tmw,rowfun(returnFunc,ttmw,'OutputVariableNames',{'hlc'})]; 

% exponential moving average 
endi=length(A.ema.windowsize);
for i = 1 : endi
% EMA
   ema = indicators(ttmw.Close,'ema',A.ema.windowsize(i));
   tmw=addvars(tmw,ema,'NewVariableNames',['emaW',num2str(A.ema.windowsize(i))]);

% T3
endii = length(A.T3.volfact);
   for j = 1 : endii
      t3  = indicators(ttmw.Close,'t3',A.ema.windowsize(i),A.T3.volfact(j));
      tmw=addvars(tmw,t3,'NewVariableNames',['t3W',num2str(A.ema.windowsize(i)),'VF',num2str(j)]);
   end
end   

% mfi
endi=length(A.mfi.ws);
for i = 1 : endi
   mfi = indicators([ttmw.High,ttmw.Low,ttmw.Close,ttmw.Volume],'mfi',A.mfi.ws(i));
   tmw=addvars(tmw,ema,'NewVariableNames',['mfiW',num2str(A.mfi.ws(i))]);   
end

% simple moving average
endi=length(A.ma.windowsize);
for i = 1 : endi
    ma.(['w',num2str(A.ma.windowsize(i))]) = movavg(ttmw(:,'Close'),'simple',A.ma.windowsize(i),'fill');
    ma.(['w',num2str(A.ma.windowsize(i))]).Properties.VariableNames{'Close'} = ['maw',num2str(A.ma.windowsize(i))];
    tmw=[tmw,ma.(['w',num2str(A.ma.windowsize(i))])];
end
   % MACD
endi=length(A.macd.scale);
for i = 1 : endi
   short=round(12*A.macd.scale(i)); long=round(26*A.macd.scale(i)); signal = round(9*A.macd.scale(i));
   a = indicators(ttmw.Close,'macd',short,long,signal);
   macdH=a(:,3);
   tmw=addvars(tmw,macdH,'NewVariableNames',['macdH',num2str(i)]);
end

% tsmom -- momentum indicator
%tmw.Volume = []; % remove VOLUME field
MomTsom.(['np',num2str(A.tsom.numperiod)]) = tsmom(ttmw(:,'Close'),'NumPeriods',A.tsom.numperiod); 
MomTsom.(['np',num2str(A.tsom.numperiod)]).Properties.VariableNames{'Close'} = ['MomTsomnp',num2str(A.tsom.numperiod)];
tmw=[tmw,MomTsom.(['np',num2str(A.tsom.numperiod)])];

%ADX
endi=length(A.adx.windowsize);
for i = 1 : endi
	a=indicators([tmw.High,tmw.Low,tmw.Close],'adx');
	pdimdi=a(:,1)-a(:,2);
	adx=a(:,3);

	tmw=addvars(tmw,adx,'NewVariableNames',['adxW',num2str(A.adx.windowsize(i))]);
	tmw=addvars(tmw,pdimdi,'NewVariableNames',['pdimdiW',num2str(A.adx.windowsize(i))]);
end

% Commodity channel indicator
endi=length(A.cci.ws);
for i = 1 : endi
   cci = indicators([tmw.High,tmw.Low,tmw.Close],'cci',A.cci.ws(i),A.cci.ws(i),A.cci.cst);
   tmw = addvars(tmw,cci,'NewVariableNames',['cciW',num2str(A.cci.ws(i))]);
end


%RSI
endi=length(A.rsi.windowsize);
for i = 1 : endi
    rsi.(['w',num2str(A.rsi.windowsize(i))]) = rsindex(ttmw(:,'Close'),'WindowSize',A.rsi.windowsize(i));
    rsi.(['w',num2str(A.rsi.windowsize(i))]).Properties.VariableNames{'RelativeStrengthIndex'} = ['rsiw',num2str(A.rsi.windowsize(i))];
    tmw=[tmw,rsi.(['w',num2str(A.rsi.windowsize(i))])];
end


%adline
% Calculate the Accumulation/Distribution Line.
tADline = tmw.Volume .* ((tmw.Close - tmw.Low) - (tmw.High - tmw.Close)) ./ ...
(tmw.High-tmw.Low);
% Handle denominator is 0 issue.
tADline(isinf(tADline)) = NaN;
ADline = cumsum(tADline,'omitnan');
tmw=addvars(tmw, ADline,'NewVariableNames','ADLine');

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
endi=length(A.sar.scale);
for i = 1 : endi
   step = 0.02 * A.sar.scale(i) ;maximum = 0.2 * A.sar.scale(i);
   sar = indicators([ttmw.High,ttmw.Low],'sar',step,maximum);
   tmw=addvars(tmw,sar,'NewVariableNames',{['sar',num2str(i)]});
end

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
