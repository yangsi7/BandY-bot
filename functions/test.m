A.PredTimeIndex = timerange(datetime('01-Jan-2019','Locale','en_US'),datetime('11-Dec-2020','Locale','en_US'),'closed');

[tmwpred]=PredBuyIdx(tmw,Mdlr,'varnames',varnames,'method','fitrensemble','TimeIndex',A.PredTimeIndex);

% Remove first hours to avoid nans
x=tmwpred.yhat_fre;
x=x(100:end);
tmp=tmwNN(A.PredTimeIndex,:);
cclose=tmp.Close(100:end);
time = tmwpred.Time(100:end);
% Filter trends

windowSize=30*24;
y = filterSY(x,'windowSize',windowSize);

figure
subplot(3,1,1)
p1=plot(time,cclose); grid on;
subplot(3,1,2)
p1=plot(time,x); hold on; grid on;
p2=plot(time,y); hold off;
subplot(3,1,3)
p2=plot(time,x-y); grid on;

windowSize2=3*24;
x2=x-y;
y2 = filterSY(x2,'windowSize',windowSize2);

ttt=2000
figure
subplot(3,1,1)
p1=plot(time(end-ttt:end),cclose(end-ttt:end)); grid on;
subplot(3,1,2)
p1=plot(time(end-ttt:end),x2(end-ttt:end)); hold on; grid on;
p2=plot(time(end-ttt:end),y2(end-ttt:end)); hold off;
subplot(3,1,3)
p2=plot(time(end-ttt:end),x2(end-ttt:end)-y2(end-ttt:end)); grid on;


windowSize3=5;
x3=x2-y2;
y3 = filterSY(x3,'windowSize',windowSize3);

ttt=2000
figure
subplot(3,1,1)
p1=plot(time(end-ttt:end),cclose(end-ttt:end)); grid on;
subplot(3,1,2)
p1=plot(time(end-ttt:end),x3(end-ttt:end)); hold on; grid on;
p2=plot(time(end-ttt:end),y3(end-ttt:end)); hold off;
subplot(3,1,3)
p2=plot(time(end-ttt:end),x3(end-ttt:end)-y3(end-ttt:end)); grid on;
