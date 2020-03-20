function [net]=BuildNet(X,varargin)
A.TimeIndex = timerange(datetime('01-Jan-2019','Locale','en_US'),datetime('14-Sep-2019','Locale','en_US'),'closed');
A.normWin=150;
A.varnames={'Open','High','Low','Close','Volume'};
A=parse_pv_pairs(A,varargin);
tmw = tmw(A.TimeIndex,:);


idxNnan=~isnan(tmwpred.Hotness(:));
tmwpred=tmwpred(idxNnan,:);

X=table2array(tmwpred(:,[A.varnames,'yhat_fre']))';

net = fitnet([10,10]);
net = train(net,X(1:100,:),tmwpred.Hotness(idxNnan)');

