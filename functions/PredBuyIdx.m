function [tmw]=predBuyIdx(tmw,Mdl,varargin)
A.TimeIndex = timerange(datetime('01-May-2019','Locale','en_US'),datetime('30-Jun-2019','Locale','en_US'),'closed');
A.normWin=72;
A.method='fitrensemble';
A.varnames={'Open','High','Low','Close','Volume'};
A=parse_pv_pairs(A,varargin);
tmw=tmw(A.TimeIndex,:);
X=table2array(tmw(:,A.varnames));
predPriceNorm=predict(Mdl,X);

if strcmp(A.method,'fitcensemble')
    yhat_fce=predPriceNorm;
    tmw = addvars(tmw,yhat_fce);    
end

if strcmp(A.method,'fitrensemble')
    yhat_fre=predPriceNorm;
            yhat_fre=(predPriceNorm-movmin(predPriceNorm, A.normWin))./(movmax(predPriceNorm, A.normWin)-movmin(predPriceNorm, A.normWin));
    tmw = addvars(tmw,yhat_fre);
end

if strcmp(A.method,'fitcecoc')
    yhat_fcecoc=predPriceNorm;
    tmw = addvars(tmw,yhat_fcecoc);
end
