function tmw=getOpenClose(tmw,varargin)

A.windowsize = 16; % Window size for smoothing
A.gainThresh = 1.0;
A.nwins = 20; % number of windows to check for Fakouts
A.TimeIndex = timerange(datetime('01-Jan-2000','Locale','en_US'),datetime('31-Dec-2030','Locale','en_US'),'closed');
A=parse_pv_pairs(A,varargin);

A.TimeIndex=A.TrainTimeIndex;
tmw=tmw(A.TimeIndex,:);
tmwNP = TMW.h(A.TimeIndex,:);
returnFunc = @(open,high,low,close,volume) (high +low + close)/3;;
tmwNP = [tmwNP,rowfun(returnFunc,tmwNP,'OutputVariableNames',{'hlc'})];
pmmeanNP = movmean(tmwNP.Close,A.windowsize);
tmwNP = addvars(tmwNP,pmmeanNP);

pmmean = movmean(tmw.Close,A.windowsize);
lmax = islocalmax(pmmean,'ProminenceWindow',A.windowsize);
lmin = islocalmin(pmmean,'ProminenceWindow',A.windowsize);
tmw = addvars(tmw,pmmean);

% Filter out bad signals
A.gainThresh = 5.0;

buyindex = nan(size(pmmean));
buyindex(lmax)=1;
buyindex(lmin)=0;
taxis=(1:length(buyindex));
indx=find(~isnan(buyindex));
FakeSig=0;
for i = 2 : length(indx)-1
	if buyindex(indx(i))==nan; continue; end;
	tmpidx1=indx(i)-A.nwins*A.windowsize;
	tmpidx1(tmpidx1<1)=1;
	tmpidx2=indx(i)+A.nwins*A.windowsize; 
	tmpidx2(tmpidx2>length(buyindex))=length(buyindex);

	meanPrice = nanmean(tmw.Close(tmpidx1:tmpidx2));
	relGain = abs(tmw.Close(indx(i+1)) - tmw.Close(indx(i)))/meanPrice*100;


	if relGain < A.gainThresh
		if FakeSig == 1
	 		buyindex(indx(i))=nan;
		end
		buyindex(indx(i+1))=nan;
		FakeSig=1;
	else
		FakeSig=0;
	end
end

newMax = find(buyindex==1); newMin=find(buyindex==0);
lmaxOut=lmax;lmaxOut(lmaxOut==1&~isnan(buyindex))=0;
lminOut=lmin;lminOut(lminOut==1&~isnan(buyindex))=0;
lmaxIn=lmax;lmaxIn(lmaxIn==1&isnan(buyindex))=0;
lminIn=lmin;lminIn(lminIn==1&isnan(buyindex))=0;

%candle(tmw);
%hold on;
plot(tmw.Time,tmwNP.hlc,'r','LineWidth',1);hold on;
p=plot(tmw.Time,tmwNP.pmmeanNP,'k',tmw.Time(lmaxIn),tmwNP.pmmeanNP(lmaxIn),'rv',tmw.Time(lminIn),tmwNP.pmmeanNP(lminIn),'g^', tmw.Time(lmaxOut), tmwNP.pmmeanNP(lmaxOut),'kv',tmw.Time(lminOut),tmwNP.pmmeanNP(lminOut),'k^');
p(1).LineWidth=1;
p(2).MarkerSize = 6;p(2).MarkerFaceColor='r';
p(3).MarkerSize = 6;p(3).MarkerFaceColor='g';
p(4).MarkerSize = 6;p(4).MarkerFaceColor='k';
p(5).MarkerSize = 6;p(5).MarkerFaceColor='k';
hold off;

indx = find(lmaxIn | lminIn);
buyindex = nan(size(pmmean));
buyindex(lmaxIn)=1;
buyindex(lminIn)=0;
pumpsig = zeros(size(buyindex));
pumpsig(lminIn)=1;
dumpsig = zeros(size(buyindex));
dumpsig(lmaxIn)=1;
tmw = addvars(tmw,pumpsig,dumpsig);
for i = 1 : length(indx)-1
	if buyindex(indx(i)) == buyindex(indx(i+1)) & lmaxIn(indx(i))
		tmp=[indx(i),indx(i+1)];
		[~,idxDiscard] = min([tmw.pmmean(indx(i)),tmw.pmmean(indx(i+1))]);
		lmaxIn(tmp(idxDiscard))=0;
	elseif buyindex(indx(i)) == buyindex(indx(i+1)) & lminIn(indx(i))
		tmp=[indx(i),indx(i+1)];
		[~,idxDiscard] = max([tmw.pmmean(indx(i)),tmw.pmmean(indx(i+1))]);
		lminIn(tmp(idxDiscard))=0;
	end
end


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


