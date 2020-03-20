function SumPerf = cryptoSim(tmw,varargin)

A.StartFund=10000;
A.useFund=0.95;
A.reInvest=1;
A.Leverage=3;
A.MakerFee=0.020/100;
A.TakerFee=0.040/100;
A.tp1=0.7/100;
A.tp2=2.1/100;
A.dnSL=0;
A.strategy = 'Andy';
A.slscale = 0.097059572248244;
A=parse_pv_pairs(A,varargin);


%Initialize first transaction arrays
bought.sharesBought = zeros(1,size(tmw,1));
bought.dollsBought = zeros(1,size(tmw,1));
bought.sharesSold = zeros(1,size(tmw,1));
bought.dollsSold = zeros(1,size(tmw,1));
bought.status = zeros(1,size(tmw,1));
bought.tp1 = zeros(1,size(tmw,1));
short.sharesSold = zeros(1,size(tmw,1));
short.dollsSold = zeros(1,size(tmw,1));
short.sharesBought = zeros(1,size(tmw,1));
short.dollsBought = zeros(1,size(tmw,1));
short.status = zeros(1,size(tmw,1));
short.tp1 = zeros(1,size(tmw,1));
profit.bought=zeros(1,size(tmw,1));
profit.short=zeros(1,size(tmw,1));
stopLoss = nan(1,size(tmw,1));
limitOrder=nan(1,size(tmw,1));

   % Get buy & sell signals
   [buySig, shortSig]=strategy_andy(tmw,'strategy',A.strategy);
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
      if i == 1; bought.tp1(i) = 0; else bought.tp1(i) = bought.tp1(i-1); end;
      if i == 1; short.tp1(i) = 0; else short.tp1(i) = short.tp1(i-1); end;

      A.lstop = (tmw.atr(i)).^A.slscale1.*A.slscale2; % Need to make adaptative to volatility
      A.lstop(isnan(A.lstop))=0.04;
      A.lstop(A.lstop>0.1)=0.1;
      A.lstop(A.lstop<0.0001)=0.0001;
      A.sstop = A.lstop; % Idem 
   
      % Update Stop Loss Sell if not closed
      if bought.status(i) == 1
   	 tt=A.lstop;
         pprice = bought.dollsBought(i)./bought.sharesBought(i);
         tmpprofit = (tmw.High(i) - pprice)/pprice;
         % Check for previous existing stop loss.
         if isnan(stopLoss(i))
            stopLoss(i) = (1-tt).*tmw.Close(i);
         elseif tmw.Low(i) < stopLoss(i)
            bought.dollsSold(i) = (1-A.MakerFee).*bought.sharesBought(i)*stopLoss(i);
            Funds(i)=Funds(i)+bought.dollsSold(i)-bought.dollsBought(i);
            stopLoss(i)=nan;
            profit.bought(i) = -bought.dollsBought(i) + bought.dollsSold(i);
            bought.dollsBought(i)=0;
            bought.sharesBought(i)=0;
            bought.status(i)=0;
            stopLoss(i) = nan;
            bought.tp1(i) = 0;
         elseif tmpprofit > A.tp1 & ~bought.tp1(i) & tmpprofit < A.tp2
            bought.dollsSold(i) = (1-A.MakerFee).*0.5.*bought.dollsBought(i).*(1+A.tp1);
            Funds(i)=Funds(i)+bought.dollsSold(i)-0.5.*bought.dollsBought(i);
            profit.bought(i) = -0.5.*bought.dollsBought(i) + bought.dollsSold(i);
            bought.dollsBought(i) = 0.5.*bought.dollsBought(i);
            bought.sharesBought(i) = 0.5.*bought.sharesBought(i); 
            stopLoss(i) = (1-tt).*tmw.Close(i);
            bought.tp1(i) = 1;
         elseif tmpprofit > A.tp2  
            bought.dollsSold(i) = (1-A.MakerFee).*bought.dollsBought(i).*(1+A.tp2);
            Funds(i)=Funds(i)+bought.dollsSold(i)- bought.dollsBought(i);
            profit.bought(i) = -bought.dollsBought(i) + bought.dollsSold(i);
            bought.dollsBought(i) = 0;
            bought.sharesBought(i) = 0; 
            stopLoss(i) = nan;
            bought.status(i)=0;
            bought.tp1(i)=0;
         elseif A.dnSL
            stopLoss(i) = (1-tt).*tmw.Close(i);
         end

      end
   
      % Update Stop Loss Buy if not closed
      if short.status(i) ==1
         tt=A.sstop;
         pprice = short.dollsSold(i)./short.sharesSold(i);
         tmpprofit = (pprice - tmw.Low(i))/pprice;
         % Check for previous existing stop loss.
         if tmw.High(i) > limitOrder(i) 
            short.dollsBought(i) = (1-A.MakerFee).*short.sharesSold(i)*limitOrder(i);
            Funds(i)=Funds(i)+short.dollsSold(i)-short.dollsBought(i);
            profit.short(i) = -short.dollsBought(i) + short.dollsSold(i);
            short.dollsSold(i)=0;
            short.sharesSold(i)=0;
            short.status(i)=0;
            limitOrder(i)=nan;
            short.tp1(i) = 0;
         elseif tmpprofit > A.tp1 & ~short.tp1(i) & tmpprofit < A.tp2
            short.dollsBought(i) = (1-A.MakerFee).*0.5.*short.dollsSold(i).*(1-A.tp1);
            Funds(i)=Funds(i)+0.5.*short.dollsSold(i)-short.dollsBought(i);
            profit.short(i) = -short.dollsBought(i) + 0.5.*short.dollsSold(i);
            short.dollsSold(i) = 0.5.*short.dollsSold(i);
            short.sharesSold(i) = 0.5.*short.sharesSold(i); 
            limitOrder(i) = (1+tt).*tmw.Close(i);
            short.tp1(i) = 1;
         elseif tmpprofit > A.tp2  
            short.dollsBought(i) = (1-A.MakerFee).*short.dollsSold(i).*(1-A.tp2);
            Funds(i)=Funds(i)+short.dollsSold(i)- short.dollsBought(i);
            profit.short(i) = -short.dollsBought(i) + short.dollsSold(i);
            short.dollsSold(i) = 0;
            short.sharesSold(i) = 0; 
            limitOrder(i) = nan;
            short.status(i)=0;
            short.tp1(i)=0;
         elseif A.dnSL
            limitOrder(i) = (1+tt).*tmw.Close(i);
         end
      end
   
      % Buy
      if buySig(i) & bought.status(i) == 0
         % Start market Order
         bought.dollsBought(i) = (1+A.TakerFee).*Funds(i).*A.useFund.*A.Leverage;
         bought.sharesBought(i) = (Funds(i).*A.useFund)/tmw.Close(i).*A.Leverage;      
         bought.status(i)=1;
         stopLoss(i) = (1-A.sstop).*tmw.Close(i);
      end
   
      % Shorting
      if shortSig(i) & short.status(i) == 0
         % Start short Order (Market price)
         short.dollsSold(i) = (1-A.TakerFee).*Funds(i).*A.useFund.*A.Leverage;
         short.sharesSold(i) = (Funds(i).*A.useFund)/tmw.Close(i).*A.Leverage;      
         short.status(i)=1;
         limitOrder(i) = (1+A.lstop).*tmw.Close(i);
      end
   
   end
   
   SumPerf.profit=sum(profit.bought+profit.short);
   SumPerf.profit_long = profit.bought;
   SumPerf.profit_short =profit.short;
   SumPerf.Funds=Funds;   
   SumPerf.bought = bought;
   SumPerf.short = short;


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

