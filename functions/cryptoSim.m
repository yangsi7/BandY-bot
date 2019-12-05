function SumPerf = cryptoSim(tmw,varargin)

A.StartFund=10000;
A.useFund=0.5;
A.reInvest=1;
A.MOf=0.075/100;
A.strategy = 'yhat_fre';
A.TrStpLoss = 0; % Need to make adaptative to volatility
A.TrLmtOrder = 0; % Idem
A=parse_pv_pairs(A,varargin)


%Initialize first transaction arrays
bought.sharesBought = zeros(1,size(tmw,1));
bought.dollsBought = zeros(1,size(tmw,1));
bought.sharesSold = zeros(1,size(tmw,1));
bought.dollsSold = zeros(1,size(tmw,1));
bought.status = zeros(1,size(tmw,1));
short.sharesSold = zeros(1,size(tmw,1));
short.dollsSold = zeros(1,size(tmw,1));
short.sharesBought = zeros(1,size(tmw,1));
short.dollsBought = zeros(1,size(tmw,1));
short.status = zeros(1,size(tmw,1));
profit.bought=zeros(1,size(tmw,1));
profit.short=zeros(1,size(tmw,1));
stopLoss = zeros(1,size(tmw,1));
limitOrder=zeros(1,size(tmw,1)).*inf;

% Get buy & sell signals
[buySig,sellSig]=strategy(tmw.(A.strategy),'strategy',A.strategy);
idxSigs = find(buySig|sellSig);
idxBuySigs = find(buySig);
idxSellSigs = find(sellSig);
% Initialize funds
Funds=nan(1,size(tmw,1));Funds(1:idxSigs(1))=A.StartFund;

% Check First transaction to be made
buyFirst=false; if idxBuySigs(1)<idxSellSigs(1); buyFirst=true;end;

%if i == idxSigs(1) & ~buyFirst; continue; end;

for i = idxSigs(1) : idxSigs(end)
   % Buying
   if i == 1; bought.status(i) = 0; else bought.status(i) = bought.status(i-1); end;
   if i == 1; Funds(i) = Funds(1); else Funds(i) = Funds(i-1); end;
   if i == 1; stopLoss(1); else; stopLoss(i)=stopLoss(i-1);end   
   if i == 1; limitOrder(1); else; limitOrder(i)=limitOrder(i-1);end   
   if buySig(i) & bought.status(i) == 0
      % Start market Order
      bought.dollsBought(i) = (1+A.MOf).*Funds(i).*A.useFund;
      bought.sharesBought(i) = (Funds(i).*A.useFund)/tmw.Close(i);      
      Funds(i)=Funds(i)-bought.dollsBought(i);
      bought.status(i)=1;
   else
      if i == 1
         bought.dollsBought(i) = bought.dollsBought(1);
         bought.sharesBought(i) = bought.sharesBought(1);
       else 
         bought.dollsBought(i) = bought.dollsBought(i-1);
         bought.sharesBought(i) = bought.sharesBought(i-1);
      end
   end

   % Shorting
   if i == 1; short.status(i) = 0; else short.status(i) = short.status(i-1); end   
   if sellSig(i) & short.status(i) == 0
      % Start short Order (Market price)
      short.dollsSold(i) = (1+A.MOf).*Funds(i).*A.useFund;
      short.sharesSold(i) = (Funds(i).*A.useFund)/tmw.Close(i);      
      Funds(i) = Funds(i) + short.dollsSold(i); 
      short.status(i)=1;
   else
      if i == 1
         short.dollsSold(i) = short.dollsSold(1);
         short.sharesSold(i) = short.sharesSold(1);
      else
         short.dollsSold(i) = short.dollsSold(i-1);
         short.sharesSold(i) = short.sharesSold(i-1);
      end
   end

   % Closing buy
   if sellSig(i) & bought.status(i) == 1
      % Check for previous existing stop loss.
      if tmw.Low(i) < stopLoss(i)
         bought.dollsSold(i) = (1+A.MOf).*bought.sharesBought(i)*stopLoss(i);
         Funds(i)=Funds(i)+bought.dollsSold(i);
         stopLoss(i)=0;
         profit.bought(i) = -bought.dollsBought(i) + bought.dollsSold(i);
         bought.dollsBought(i)=0;
         bought.sharesBought(i)=0;
         bought.status(i)=0;
      else
         stopLoss(i) = (1-A.TrStpLoss).*tmw.Close(i);
      end
   end

   % Closing Short
   if buySig(i) & short.status(i) == 1
      % Check for previous existing stop loss.
      limitOrder(i)=limitOrder(i-1);
      if tmw.High(i) > limitOrder(i)
         short.dollsBought(i) = (1+A.MOf).*short.sharesSold(i)*limitOrder(i);
         Funds(i)=Funds(i)-short.dollsBought(i);
         limitOrder(i)=inf;
         profit.short(i) = -short.dollsBought(i) + short.dollsSold(i);
         short.dollsSold(i)=0;
         short.sharesSold(i)=0;
         short.status(i)=0;
      else
         limitOrder(i) = (1+A.TrLmtOrder).*tmw.Close(i);
      end
   end   
end

SumPerf.Funds = Funds;
SumPerf.profit=profit;
SumPerf.profitTot=(profit.bought+profit.short);


%fig=figure
%subplot(2,1,2)Fun
%plot(tmw.Time,cumsum(Profit),'k','LineWidth',2);
%ylabel('USD');
%title('Simulated Profits (start fund: 10000 USD, use 50%, no leverage, reinvest 100%)');
%subplot(2,1,1)
%candle(tmw);
%title('Bitcoin price');
%ylabel('USD')
%plot(tmw.Time, Funds-Funds(1),'k','LineWidth',2);
%plot(tmw.Time, movmean(Funds-Funds(1),24*15),'r','LineWidth',3); hold off;
%ylabel('USD');
%title('Yangy Crypto Bot simulated profits')

