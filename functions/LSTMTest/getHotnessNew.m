function tmw=getOpenClose(tmw,varargin)

A.windowsize = 8; % Window size for smoothing
A.gainThresh = 1.0;
A.nwins = 20; % number of windows to check for Fakouts
A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed');
A=parse_pv_pairs(A,varargin);

tmw=tmw(A.TimeIndex,:);
returnFunc = @(open,high,low,close,volume) (high +low + close)/3;;
tmw = [tmw,rowfun(returnFunc,tmw,'OutputVariableNames',{'hlc'})];
pmmean = filterSY(tmw.Close,'windowSize',A.windowsize,'filter',0);
lmax = islocalmax(pmmean,'ProminenceWindow',A.windowsize,'FlatSelection', 'first');
lmin = islocalmin(pmmean,'ProminenceWindow',A.windowsize,'FlatSelection', 'first');
bla=zeros(size(lmax));
bla(lmax)=1;bla(lmin)=-1;
tmw = addvars(tmw,pmmean);

% First pass: keep only buy signals with good return
buysig =  zeros(size(lmax));
sellsig = zeros(size(lmax));
fakeBuysig = zeros(size(buysig));
indxBuy=find(lmin);
indxSell=find(lmax);

for i = 1 :length(indxBuy)
   [~,idxmin] = nanmin(tmw.Close(nanmax(1,indxBuy(i)-A.windowsize):nanmin(indxBuy(end),indxBuy(i)+A.windowsize)));
   indxBuy(i)=indxBuy(i)+idxmin-9;
end
for i = 1 :length(indxSell)
   [~,idxmax] = nanmax(tmw.Close(nanmax(1,indxSell(i)-A.windowsize):nanmin(indxSell(end),indxSell(i)+A.windowsize)));
   indxSell(i)=indxSell(i)+idxmax-+A.windowsize+1;
end
indxBuy=unique(indxBuy);
indxSell=unique(indxSell);

[indxBuy,indxSell] = noduplicate(tmw,indxBuy,indxSell);

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

iddBscard = [];
for i = 1 : iBend
      tmpid1 = indxBuy(i);
      ttmp=(indxSell-indxBuy(i)); ttmp(ttmp<0)=inf;
      [~, ii] = nanmin(ttmp);
      if isempty(ii)
         break;
      end
      tmpid2 = indxSell(ii);
      buyReturn(i) = (-tmw.Close(tmpid1)+tmw.Close(tmpid2))/tmw.Close(tmpid1)*100;
      if buyReturn(i) < A.gainThresh
         iddBscard = [iddBscard,i];
         fakeBuysig(indxBuy(i))=1;
      end
end

% Second pass: keep only sell signals with good return
fakeSellsig = zeros(size(sellsig));
iddSscard = []
for i = 1 : iSend
      tmpid1 = indxSell(i);
      ttmp=(indxBuy-indxSell(i)); ttmp(ttmp<0)=inf;
      [~, ii] = nanmin(ttmp);
      if isempty(ii)
         break;
      end
      tmpid2 = indxBuy(ii);
      sellReturn(i) = (+tmw.Close(tmpid1)-tmw.Close(tmpid2))/tmw.Close(tmpid1)*100;
      if sellReturn(i) < A.gainThresh
         iddSscard=[iddSscard,i];
         fakeSellsig(indxSell(i))=1;
      end
end 

indxBuy(iddBscard)=[];
indxSell(iddSscard)=[];

[indxBuy2,indxSell2] = noduplicate(tmw,indxBuy,indxSell);
buysig=zeros(size(tmw.Close));
sellsig=buysig;
buysig(indxBuy2)=1;
sellsig(indxSell2)=1;

%indxsig=find(buysig|sellsig);

%for i = 2 : length(indxsig)
%   if buysig(i) & buysig(i-1)
%      buysig(i)=0;
%      fakeBuysig(i)=1;
%   elseif sellsig(i) & sellsig(i-1)
%      sellsig(i)=0;
%      fakeSellsig(i)=1;
%   end
%end



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
buyindex(sellsig==1)=1;
buyindex(buysig==1)=0;
Hotness=nan(size(tmw.pmmean));
for i = 1 : length(indx)-1
	tmpPrice=tmw.pmmean(indx(i):indx(i+1));
	TNorm=ones(size(tmpPrice))*0.3;
	TNorm(1)=0;TNorm(end)=0;TNorm(2)=0.1;TNorm(end-1)=0.1;
	Hotness(indx(i):indx(i+1))=(tmpPrice-min(tmpPrice))/(max(tmpPrice)-min(tmpPrice));
	Hotness(indx(i):indx(i+1))=Hotness(indx(i):indx(i+1));
end

%idminus=1000
%figure
%subplot(2,1,1)
%plot(tmw.Time,tmw.Close);hold on; grid on;
%scatter(tmw.Time(buyindex==0),tmw.Close(buyindex==0),'filled','g');
%scatter(tmw.Time(buyindex==1),tmw.Close(buyindex==1),'filled','r');
%xlim([tmw.Time(end-idminus*2),tmw.Time(end-idminus)]);
%
%subplot(2,1,2)
%plot(Hotness(end-2*idminus:end-idminus));
%Hotness(end-A.windowsize:end)=nan;
tmw = addvars(tmw,Hotness);

%figure
%plot(tmw.Time,tmw.Hotness,'k','LineWidth',1);hold on; grid on;
%plot(tmw.Time,predPriceNorm,'--r','LineWidth',1);
%plot(tmw.Time,predPriceNNorm,'r','LineWidth',1);hold off;


