function [varnames,tmw,varnamesBad] = CalcIndicators(tmw,varargin)

% select all if no time index is provided
A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed'); 
 
A.ParamStruct = [];
 
% Default parameters
% range filter
A.rf.per = 28;
A.rf.mult=1.3;

% rsi
A.rsi.per = 21;
A.rsi.obos = 52;

% Jurik MA
A.jma.L=20;
A.jma.phi=21;
A.jma.pow=2;

A.atr.per = 120;

%adx
A.adx.per = 17;

A.macd.fast=8;
A.macd.long=14;
A.macd.signal=11;

%sar
A.sar.inc=0.5;
A.sar.mmax=0.12;

%svol
A.svol.per = 42;
A.svol.f=1.2;

A=parse_pv_pairs(A,varargin);
if ~isempty(A.ParamStruct); A=A.ParamStruct;end;

% Range Filter

% Smooth average range
rng = nan(size(tmw.Close));
wper = round(A.rf.per/3.0)-1.0;
rng(2:end) = tmw.Close(2:end)-tmw.Close(1:end-1);
absrng = abs(rng);
avgrng = indicators(absrng,'sma',A.rf.per);
smthrng = indicators(avgrng,'sma',wper).*A.rf.mult;
smthrng(isnan(smthrng)) = 0;
% Range filter
rngflt = tmw.Close;

for i = 2 : length(rngflt)
   if tmw.Close(i) > rngflt(i-1)
      if tmw.Close(i) - smthrng(i) < rngflt(i-1)
         rngflt(i) = rngflt(i-1);
      else
         rngflt(i) = tmw.Close(i) - smthrng(i);
      end
   else
      if  tmw.Close(i) + smthrng(i) > rngflt(i-1)
         rngflt(i) = rngflt(i-1);
      else
         rngflt(i) = tmw.Close(i) + smthrng(i);
      end
   end
end
% Filter direction
uwrd = zeros(size(tmw.Close));
dwrd = uwrd;
rngflt_m1 = uwrd;
rngflt_m1(2:end) = rngflt(1:end-1);
uwrd(rngflt>rngflt_m1) = 1;
uwrd(rngflt<=rngflt_m1) = 0;
dwrd(rngflt<rngflt_m1) = 1;
dwrd(rngflt>=rngflt_m1) = 0;
% Target bands 
hband = rngflt + smthrng;
lband = rngflt - smthrng;
i=1;j=1;
tmw=addvars(tmw,hband,'NewVariableNames','rf_hb');
tmw=addvars(tmw,lband,'NewVariableNames','rf_lb');
tmw=addvars(tmw,uwrd,'NewVariableNames','rf_uwrd');
tmw=addvars(tmw,dwrd,'NewVariableNames','rf_dwrd');

%ATR
atr = indicators([tmw.High,tmw.Low,tmw.Close],'atr',A.atr.per);
tmw=addvars(tmw,atr,'NewVariableNames','atr');

% JMA
jma = JMA(tmw,'L',A.jma.L(i),'phi',A.jma.phi,'pow',A.jma.pow);
djma = nan(size(jma));
djma(2:end) = jma(2:end)-jma(1:end-1);
tmw=addvars(tmw,jma,'NewVariableNames','jma');
tmw=addvars(tmw,djma,'NewVariableNames','djma');

%ADX
	a=indicators([tmw.High,tmw.Low,tmw.Close],'adx',A.adx.per);
	adx_dip=a(:,1);
        adx_dim=a(:,2);
	adx=a(:,3);

	tmw=addvars(tmw,adx,'NewVariableNames','adx');
	tmw=addvars(tmw,adx_dip,'NewVariableNames','adx_dip');
	tmw=addvars(tmw,adx_dim,'NewVariableNames','adx_dim');

%sar
   sar = indicators([tmw.High,tmw.Low],'sar',A.sar.inc(i),A.sar.mmax);
   tmw=addvars(tmw,sar,'NewVariableNames','sar');

%VWAP
%vwap = nan(size(tmw.Close));
%vwap = movsum(tmw.Close.*tmw.Volume,[A.rsi.obos,0])./movsum(tmw.Volume,[A.rsi.obos,0]);

%RSI
%endi=length(A.rsi.per);
%for i = 1 : endi
%    rsi = indicators(vwap,'rsi',A.rsi.per);
%    tmw=addvars(tmw,rsi,'NewVariableNames',{['rsi_per',num2str(A.rsi.per)]});
%end

close_m1 = nan(size(tmw.Close));
close_m1(2:end) = tmw.Close(1:end-1);
up = zeros(size(tmw.Close));
tmp = abs(tmw.Close-close_m1).*tmw.Volume;
up(tmw.Close>close_m1) = tmp(tmw.Close>close_m1);
dn = zeros(size(tmw.Close));
dn(tmw.Close<close_m1) = tmp(tmw.Close<close_m1);
up_m1 = nan(size(tmw.Close));
up_m1(2:end) = up(1:end-1);
dn_m1 = nan(size(tmw.Close));
dn_m1(2:end) = dn(1:end-1);
upt = (up + up_m1.*(A.rsi.per - 1))./A.rsi.per;
dnt = (dn + dn_m1.*(A.rsi.per - 1))./A.rsi.per;
rsi_v = 100.*(upt./(upt+dnt));

tmw=addvars(tmw,rsi_v,'NewVariableNames','rsi_v');



% MACD
endi=length(A.macd.fast);
for i = 1 : endi
   short=A.macd.fast(i); long=A.macd.long(i); signal = A.macd.signal(i);
   a = indicators(tmw.Close,'macd',short,long,signal);
   macdH=a(:,3);
   tmw=addvars(tmw,macdH,'NewVariableNames','macdH');
end

% svol
endi=length(A.svol.per);
for i = 1 : endi
    svol = indicators(tmw.Volume,'sma',A.svol.per(i)).*A.svol.f;
    tmw=addvars(tmw,svol,'NewVariableNames','svol');
end


varnames=(tmw.Properties.VariableNames);

varnamesBad={};
for i = 1 : length(varnames)
   if sum(tmw.(varnames{i})==inf|tmw.(varnames{i})==nan) >0
      varnamesBad=[varnamesBad;varnames{i}];
   end
end

tmw = tmw(A.TimeIndex,:);
