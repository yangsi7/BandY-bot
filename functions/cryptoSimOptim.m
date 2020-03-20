function SumPerf = cryptoSim(tmw,varargin)

A.StartFund=10000;
A.useFund=0.3;
A.reInvest=1;
A.Leverage=20;
A.MakerFee=0.020/100;
A.TakerFee=0.040/100;
A.thrLong=0.2;
A.thrShort=0.8;
A.thrCloseLong=0.6;
A.thrCloseShort=0.4;
A.strategy = 'yhat_fre';
A.StopBuy1 = 0.015; % Need to make adaptative to volatility
A.StopBuy2 = 0.001;
A.StopSell1 = 0.015; % Idem
A.StopSell2 = 0.001;
A=parse_pv_pairs(A,varargin);

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
stopLoss = nan(1,size(tmw,1));
limitOrder=nan(1,size(tmw,1));

try
   % Get buy & sell signals
   [buySig, shortSig, closeBuySig, closeShortSig]=strategy(tmw,'strategy',A.strategy,'thrLong',A.thrLong,'thrShort',A.thrShort);
   idxSigs = find(buySig|shortSig);
   idxBuySigs = find(buySig);
   idxShortSigs = find(shortSig);
   % Initialize funds
   Funds=nan(1,size(tmw,1));Funds(1:idxSigs(1))=A.StartFund;
   
   % Check First transaction to be made
   buyFirst=false; if idxBuySigs(1)<idxShortSigs(1); buyFirst=true;end;
   
   %if i == idxSigs(1) & ~buyFirst; continue; end;
   
   for i = idxSigs(1) : idxSigs(end)
      % Init
      if i == 1; bought.status(i) = 0; else bought.status(i) = bought.status(i-1); end;
      if i == 1; short.status(i) = 0; else short.status(i) = short.status(i-1); end
      if i == 1; Funds(i) = Funds(1); else Funds(i) = Funds(i-1); end;
      if i == 1; stopLoss(i) = stopLoss(1); else; stopLoss(i)=stopLoss(i-1);end   
      if i == 1; limitOrder(i) = limitOrder(1); else; limitOrder(i)=limitOrder(i-1);end 
      if i == 1; bought.dollsBought(i) = bought.dollsBought(1); ...
         else; bought.dollsBought(i) = bought.dollsBought(i-1); end
      if i == 1; bought.sharesBought(i) = bought.sharesBought(1); ...
         else; bought.sharesBought(i) = bought.sharesBought(i-1); end;
      if i == 1; short.dollsSold(i) = short.dollsSold(1); ...
         else; short.dollsSold(i) = short.dollsSold(i-1); end;
      if i == 1; short.sharesSold(i) = short.sharesSold(1); ...
         else;short.sharesSold(i) = short.sharesSold(i-1);end;
   
   
      % Update Stop Loss Sell if not closed
      if bought.status(i) == 1
         if closeBuySig(i) == 1
   		   tt=A.StopSell2;
   	   else
   		   tt=A.StopSell1;
   	   end
         % Check for previous existing stop loss.
         if tmw.Low(i) < stopLoss(i)
            bought.dollsSold(i) = (1-A.MakerFee).*bought.sharesBought(i)*stopLoss(i);
            Funds(i)=Funds(i)+bought.dollsSold(i)-bought.dollsBought(i);
            stopLoss(i)=0;
            profit.bought(i) = -bought.dollsBought(i) + bought.dollsSold(i);
            bought.dollsBought(i)=0;
            bought.sharesBought(i)=0;
            bought.status(i)=0;
            stopLoss(i)==nan;
         else
            stopLoss(i) = (1-tt).*tmw.Close(i);
         end
      end
   
      % Update Stop Loss Buy if not closed
      if short.status(i) ==1
         if closeShortSig(i) == 1
            tt=A.StopBuy2;
         else
            tt=A.StopBuy1;
         end
         % Check for previous existing stop loss.
         if tmw.High(i) > limitOrder(i)
            short.dollsBought(i) = (1+A.MakerFee).*short.sharesSold(i)*limitOrder(i);
            Funds(i)=Funds(i)+short.dollsSold(i)-short.dollsBought(i);
            limitOrder(i)=inf;
            profit.short(i) = -short.dollsBought(i) + short.dollsSold(i);
            short.dollsSold(i)=0;
            short.sharesSold(i)=0;
            short.status(i)=0;
            limitOrder(i)=nan;
         else
            limitOrder(i) = (1+tt).*tmw.Close(i);
         end
      end
   
      % Buy
      if buySig(i) & bought.status(i) == 0
         % Start market Order
         bought.dollsBought(i) = (1+A.TakerFee).*Funds(i).*A.useFund.*A.Leverage;
         bought.sharesBought(i) = (Funds(i).*A.useFund)/tmw.Close(i).*A.Leverage;      
         %Funds(i)=Funds(i)-bought.dollsBought(i);
         bought.status(i)=1;
         stopLoss(i) = (1-A.StopSell1).*tmw.Close(i);
      end
   
      % Shorting
      if shortSig(i) & short.status(i) == 0
         % Start short Order (Market price)
         short.dollsSold(i) = (1-A.TakerFee).*Funds(i).*A.useFund.*A.Leverage;
         short.sharesSold(i) = (Funds(i).*A.useFund)/tmw.Close(i).*A.Leverage;      
         %Funds(i) = Funds(i) + short.dollsSold(i)/.A.Leverage; 
         short.status(i)=1;
         limitOrder(i) = (1+A.StopBuy1).*tmw.Close(i);
      end
   
   end
   
%   SumPerf=sum(sign(profit.bought).*profit.bought.^2+sign(profit.short).*profit.short.^2);
   SumPerf=sum(profit.bought+profit.short);
%   profit=profit.bought+profit.short;
%   idxLoss = profit<0;
%   idxGain = profit>0;
%   SumPerf=sum(profit(idxGain))+ sum(profit(idxLoss)*1.5);
catch
   SumPerf = -10^9;
end



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

