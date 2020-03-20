function [buySig, shortSig, closeBuySig, closeShortSig] = strategy(tmw,varargin)

% strategy: 'yhat_fre', 'yhat_fce'
A.strategy = 'yhat_fre';
A.thrLong=0.2;
A.thrShort=0.8;
A.thrCloseLong=0.6;
A.thrCloseShort=0.4;
A.adx = 20;
A=parse_pv_pairs(A,varargin);

% Initialize signals
buySig=false(size(tmw.Close)); shortSig=false(size(tmw.Close));
closeBuySig=false(size(tmw.Close)); closeShortSig=false(size(tmw.Close));

% Strat (1) 'yhat_fre'
if strcmp(A.strategy,'yhat_fre')
   buySig(tmw.yhat_fre<A.thrLong & tmw.BB==1)=true;
   shortSig(tmw.yhat_fre>A.thrShort& tmw.BB==0)=true;
   closeBuySig(tmw.yhat_fre>A.thrCloseLong)=true;
   closeShortSig(tmw.yhat_fre<A.thrCloseShort)=true;
end

if strcmp(A.strategy,'yhat_fr2')
   buySig(tmw.yhat_fre<A.thrLong )=true;
   shortSig(tmw.yhat_fre>A.thrShort)=true;
   closeBuySig(tmw.yhat_fre>A.thrCloseLong)=true;
   closeShortSig(tmw.yhat_fre<A.thrCloseShort)=true;
end

if strcmp(A.strategy,'signal')
   buySig(tmw.signal<A.thrLong & tmw.BB==1)=true;
   shortSig(tmw.signal>A.thrShort& tmw.BB==0)=true;
   closeBuySig(tmw.signal>A.thrCloseLong)=true;
   closeShortSig(tmw.signal<A.thrCloseShort)=true;
end

if strcmp(A.strategy,'adx')
   buySig(tmw.signal<A.thrLong & tmw.BB==1)=true;
   shortSig(tmw.signal>A.thrShort& tmw.BB==0)=true;

   ttrend=tmw.pdiW15-tmw.mdiW15;
   buySig(ttrend<0&tmw.adxW15>A.adx)=false;
   shortSig(ttrend>0&tmw.adxW15>A.adx)=false;

   closeBuySig(tmw.signal>A.thrCloseLong)=true;
   closeShortSig(tmw.signal<A.thrCloseShort)=true;
end

% Strat (3) 'yhat_fce'
if strcmp(A.strategy,'yhat_f2e')
   bbounds=[0 0.15 0.3 0.6 0.75 1];
   dpriceNorm = discretize(tmw.priceNorm,bbounds,'categorical');
   cats = categories(dpriceNorm);
   buyCats= cats(1);sellCats=cats(end)
   buySig(ind == buyCats) = true;
   sellSig(ind == sellCats)=true;
end

