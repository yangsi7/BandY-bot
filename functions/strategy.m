function [buySig, sellSig] = strategy(ind,varargin)

% strategy: 'yhat_fre', 'yhat_fce'
A.strategy = 'yhat_fre';
A=parse_pv_pairs(A,varargin);

% Initialize signals
buySig=false(size(ind)); sellSig=false(size(ind));

% Strat (1) 'yhat_fre'
if strcmp(A.strategy,'yhat_fre')
   thrBuy=0.2;thrSell=0.8;
   buySig(ind<thrBuy)=true;
   sellSig(ind>thrSell)=true;
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

