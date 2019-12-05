function tmw=getOpenClose(tmw,varargin)

A.windowsize = 16; % Window size for smoothing
A.gainThresh = 1.0;
A.nwins = 20; % number of windows to check for Fakouts
A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed');
A=parse_pv_pairs(A,varargin);

tmw=tmw(A.TimeIndex,:);
returnFunc = @(open,high,low,close,volume) (high +low + close)/3;;
tmw = [tmw,rowfun(returnFunc,tmw,'OutputVariableNames',{'hlc'})];

%pmmean = movmean(tmw.Close,A.windowsize);
pmmean = movmean(tmw.Close,A.windowsize);
lmax = islocalmax(pmmean,'ProminenceWindow',A.windowsize);
lmin = islocalmin(pmmean,'ProminenceWindow',A.windowsize);
bla=zeros(size(lmax));
bla(lmax)=1;bla(lmin)=-1;
tmw = addvars(tmw,pmmean);

% First pass: keep only buy signals with good return
buysig = lmin;
fakeBuysig = zeros(size(buysig));
indxBuy=find(lmin);
indxSell=find(lmax);
if indxBuy(1)<indxSell(1)
   buyOffset=0;SellOffset=1;
else
   buyOffset=1;SellOffset=0;
end
if indxBuy(end)<indxSell(end)
   iBend=length(indxBuy);iSend = length(indxSell)-1;
else
   iBend=length(indxBuy)-1;iSend =length(indxSell);
end

for i = 1 : iBend
   buyReturn(i) = (-tmw.Close(indxBuy(i))+tmw.Close(indxSell(i+buyOffset)))/tmw.Close(indxBuy(i))*100;
   if buyReturn(i) < A.gainThresh
      buysig(indxBuy(i))=0;
      fakeBuysig(indxBuy(i))=1;
   end
end 

% Second pass: keep only sell signals with good return
sellsig = lmax;
fakeSellsig = zeros(size(sellsig));
for i = 1 : iSend
   sellReturn(i) = (+tmw.Close(indxSell(i))-tmw.Close(indxBuy(i+SellOffset)))/tmw.Close(indxSell(i))*100;
   if sellReturn(i) < A.gainThresh
      sellsig(indxSell(i))=0;
      fakeSellsig(indxSell(i))=1;
   end
end 

indxsig=find(buysig|sellsig);

for i = 2 : length(indxsig)
   if buysig(i) & buysig(i-1)
      buysig(i)=0;
      fakeBuysig(i)=1;
   elseif sellsig(i) & sellsig(i-1)
      sellsig(i)=0;
      fakeSellsig(i)=1;
   end
end



%idxfakesell = find(fakeSellsig);
%idxfakebuy = find(fakeBuysig);  
%plot(tmw.Time,tmw.Close,'r','LineWidth',1);hold on;
%p=plot(tmw.Time,tmw.pmmean,'k',tmw.Time(sellsig),tmw.pmmean(sellsig),'rv',tmw.Time(buysig),tmw.pmmean(buysig),'g^', tmw.Time(fakeSellsig(idxfakesell)), tmw.pmmean(fakeSellsig(idxfakesell)),'kv',tmw.Time(idxfakebuy),tmw.pmmean(idxfakebuy),'k^');
%p(1).LineWidth=1;
%p(2).MarkerSize = 6;p(2).MarkerFaceColor='r';
%p(3).MarkerSize = 6;p(3).MarkerFaceColor='g';
%p(4).MarkerSize = 6;p(4).MarkerFaceColor='k';
%p(5).MarkerSize = 6;p(5).MarkerFaceColor='k';
%hold off;

indx = find(buysig | sellsig);
buyindex = nan(size(pmmean));
buyindex(sellsig)=1;
buyindex(buysig)=0;
priceNorm=nan(size(tmw.pmmean));
for i = 1 : length(indx)-1
	tmpPrice=tmw.pmmean(indx(i):indx(i+1));
	TNorm=ones(size(tmpPrice))*0.3;
	TNorm(1)=0;TNorm(end)=0;TNorm(2)=0.1;TNorm(end-1)=0.1;
	priceNorm(indx(i):indx(i+1))=(tmpPrice-min(tmpPrice))/(max(tmpPrice)-min(tmpPrice));
	priceNorm(indx(i):indx(i+1))=priceNorm(indx(i):indx(i+1))-TNorm;
end
tmw = addvars(tmw,priceNorm);

%figure
%plot(tmw.Time,tmw.priceNorm,'k','LineWidth',1);hold on; grid on;
%plot(tmw.Time,predPriceNorm,'--r','LineWidth',1);
%plot(tmw.Time,predPriceNNorm,'r','LineWidth',1);hold off;


