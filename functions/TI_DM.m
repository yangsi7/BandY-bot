function [ ADX, ADXR, PDI, MDI]=calcDMI( high, low, close, M, N)
% CALCDMI - calculate Directional Movement Index (DMI) for a given
% stock given high, low, close
%
% [ ADX, ADXR, PDI, MDI] = calcDMI( high, low, close, M, N),
% INPUT: 
% high - data vector of high prices
% low - data vector of low prices
% close - data vector of close prices
% M - days to avreage, optional
% N- days to sum +DI and -DI, optional
%
% OUTPUT:
% ADX - Directional Movement Index
% ADXR -  Directional movement rating
% PDI - +DM, plus Directional Indicator
% MDI - -DM, minus Directional Indicator
%
% EXAMPLES:
% % read JNJ stock from yahoo URL
% url2Read ='http://ichart.finance.yahoo.com/table.csv?s=JNJ&a=0&b=12&c=2010&d=9&e=23&f=2012&g=d&ignore=.csv';
% s=urlread( url2Read);
% 
% % reshape response
% s=strread(s,'%s','delimiter',',');
% s=reshape(s,[],length(s)/7)';
% disp(s);
% 
% % read data from s
% high =  str2double(s(2:end,3));
% low = str2double(s(2:end,4));
% close = str2double(s(2:end,5));
% 
% % call function
% [ ADX, ADXR, PDI, MDI] = calcDMI( high, low, close);
% information from http://www.trade10.com/Directional_Movement.html
% Directional movement is a system for providing trading signals to be used for price breaks from a trading range. 
% The system involves 5 indicators which are the Directional Movement Index (DX), the plus Directional Indicator (+DI), 
% the minus Directional Indicator (-DI), the average Directional Movement (ADX) and the Directional movement rating (ADXR). 
% The system was developed J. Welles Wilder and is explained thoroughly in his book, New Concepts in Technical Trading Systems .
% The basic Directional Movement Trading system involves plotting the 14day +DI and the 14 day -DI on top of each other. 
% When the +DI rises above the -DI, it is a bullish signal. 
% A bearish signal occurs when the +DI falls below the -DI. 
% To avoid whipsaws, Wilder identifies a trigger point to be the extreme price on the day the lines cross. 
% If you have received a buy signal, you would wait for the security to rise above the extreme price (the high price on the day the lines crossed). 
% If you are waiting for a sell signal the extreme point is then defined as the low price on the day's the line cross.
% 
% $License: BSD (use/copy/change/redistribute on own risk, mention the
% author) $
% History:
% 001:  Natanel Eizenberg: 14-May-2006 21:52, First version.
% 002:  Natanel Eizenberg: 04-Nov-2012 21:52, Edit for file exchange.
% all values should be lined
if size(high,1)~=1; high=high'; end;
if size(low,1)~=1; low=low'; end;
if size(close,1)~=1; close=close'; end;
% defults M,N   
if nargin==3 
    N=14;
    M=6;
end;
% max,min values
if N>100,
    N=100;
elseif N<2,
    N=2;
end;
if M>100,
    M=100;
elseif M<1,
    M=1;
end;
%  true range calculation (TR)
tmpTR=max( [high-low;...
        abs(high - [ high(1) close(1:end-1)]);...
        abs(low - [ low(1) close(1:end-1)])  ]);
win=ones(1,N);
TR=conv(tmpTR,win);
TR=TR(1:end-N+1);
% high and low Directional
HD = high-[ high(1) high(1:end-1)]; 
LD = [ low(1) low(1:end-1)]-low;
% init 
tmpDMP=zeros(size(HD));
tmpDMM=zeros(size(LD));
% find data for +DM
index=HD>0 & HD>LD;
tmpDMP(index)= HD(index); 
win=ones(1,N);
DMP=conv(tmpDMP,win);
DMP=DMP(1:end-N+1);
% find data for -DM
index=LD>0 & LD>HD;
tmpDMM(index)= LD(index);
win=ones(1,N);
DMM=conv(tmpDMM,win);
DMM=DMM(1:end-N+1);
% calc +DM and -DM
PDI= (DMP*100)./TR;
MDI= (DMM*100)./TR;
% calc Directional Movement Index
win=ones(1,M);
tmpADX=([abs(MDI-PDI)]./[(MDI+PDI)])*100;
tmpADX(1)=tmpADX(2); %remove inf
ADX= conv(tmpADX,win)/M;
ADX= ADX(1:end-M+1);
% calc Directional movement rating
ADXR=circshift(ADX',M)';
ADXR(1:M)=ADX(1:M);
ADXR=(ADX+ADXR)/2;
