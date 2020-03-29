function [ccost maxdrawdown SumPerf action] = cryptoSim(tmw,varargin)

A.params=3;
A.StartFund=10000;
A.useFund=0.95;
A.reInvest=1;
A.Leverage=3;
A.MakerFee=0.020/100;
A.TakerFee=0.040/100;
A.strat = 'Andy';
if A.params == 1
   A.tp1=0.05;
   A.tp2=0.0097;
   A.tp1scale=1;
   A.tp2scale=1;
   A.dnSL=0;
   A.ftp=0.1;
   A.slfix = 1;
   A.slscale1 = 4.01;
   A.slscale2 = 1.217;
   A.slscale3 = 0.2244;
   A.slscale4 = 0.661;
   A.slmax = 0.0405;
   A.prelstop = 0.001;
   A.presstop = 0.001;
   A.adxth=5;
   A.rsiobos=74;
elseif A.params == 2
   A.tp1=1;
   A.tp2=1;
   A.tp1scale=1;
   A.tp2scale=1;
   A.dnSL=1;
   A.ftp=0.47;
   A.slfix = 0;
   A.slscale1 = 3.1702;
   A.slscale2 = 0.71158;
   A.slscale3 = 0.52269;
   A.slscale4 = 0.51605;
   A.slmax = 0.040519;
   A.prelstop = 0.00648;
   A.presstop = 0.01077;
   A.adxth=13.7;
   A.rsiobos=62.1;
elseif A.params == 3
   A.tp1=1;
   A.tp2=1;
   A.tp1scale=1;
   A.tp2scale=1;
   A.dnSL=1;
   A.ftp=0.47;
   A.slfix = 0;
   A.slscale1 = 5;
   A.slscale2 = 1.39;
   A.slscale3 = 0.001;
   A.slscale4 = 0.5;
   A.slmax = 0.0551;
   A.prelstop = 0.036035;
   A.presstop = 0.031029;
   A.adxth=5;
   A.rsiobos=80;
end

A=parse_pv_pairs(A,varargin);
A.tp2 = A.tp1 + A.tp2;

ccost = [];
maxdrawdown = [];
SumPerf = [];
action = [];

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
action.long.sl=zeros(1,size(tmw,1));
action.long.tp1=zeros(1,size(tmw,1));
action.long.tp2=zeros(1,size(tmw,1));
action.long.slPrice=zeros(1,size(tmw,1));
action.long.tp1Price=zeros(1,size(tmw,1));
action.long.tp2Price=zeros(1,size(tmw,1));
action.long.open=zeros(1,size(tmw,1));
action.long.close=zeros(1,size(tmw,1));
action.short.sl=zeros(1,size(tmw,1));
action.short.tp1=zeros(1,size(tmw,1));
action.short.tp2=zeros(1,size(tmw,1));
action.short.slPrice=zeros(1,size(tmw,1));
action.short.tp1Price=zeros(1,size(tmw,1));
action.short.tp2Price=zeros(1,size(tmw,1));
action.short.open=zeros(1,size(tmw,1));
action.short.close=zeros(1,size(tmw,1));
stopLoss = nan(1,size(tmw,1));
limitOrder=nan(1,size(tmw,1));

   % Get buy & sell signals
   [buySig, shortSig]=strategy(tmw,'strat',A.strat,'adxth',A.adxth,...
      'rsiobos',A.rsiobos);
   idxSigs = find(buySig|shortSig);
   idxBuySigs = find(buySig);
   idxShortSigs = find(shortSig);
   if isempty(idxBuySigs) | isempty(idxShortSigs)
      ccost = -10000;
      maxdrawdown = 100;
      return
   end
   % Initialize funds
   Funds=nan(1,size(tmw,1));Funds(1:idxSigs(1))=A.StartFund;
   
   % Check First transaction to be made
   buyFirst=false; if idxBuySigs(1)<idxShortSigs(1); buyFirst=true;end;
   
   %if i == idxSigs(1) & ~buyFirst; continue; end;
  maxFund = 0; maxdrawdown = 0;
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
      if ~A.slfix
         %xx = tmw.atr(i)./tmw.jma(i);
         xxlo = tmw.fbolllo(i);
         xxup = tmw.fbollup(i);
         A.lstop = A.prelstop+ A.slscale1.*(xxlo.^A.slscale2); % Need to make adaptative to volatility
         A.sstop = A.presstop+ A.slscale3.*(xxup.^A.slscale4); % Need to make adaptative to volatility
         A.lstop(A.lstop>A.slmax)=A.slmax;
         A.sstop(A.sstop>A.slmax)=A.slmax;
%         A.tp1 = A.tp1 + A.tp1scale.*xx;
%         A.tp2 = A.tp2+ A.tp2scale.*xx;
      else
         A.lstop = A.prelstop;
         A.sstop = A.lstop;
      end
   
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
            profit.bought(i) = -bought.dollsBought(i) + bought.dollsSold(i);
            bought.dollsBought(i)=0;
            bought.sharesBought(i)=0;
            bought.status(i)=0;
            action.long.slPrice(i) =  stopLoss(i);
            stopLoss(i) = nan;
            bought.tp1(i) = 0;
            action.long.sl(i) = 1;
         elseif tmpprofit >= A.tp1 & ~bought.tp1(i)
            action.long.tp1Price(i) =  (1+A.tp1).*bought.dollsBought(i)./bought.sharesBought(i);
            bought.dollsSold(i) = (1-A.MakerFee).*A.ftp.*bought.dollsBought(i).*(1+A.tp1);
            Funds(i)=Funds(i)+bought.dollsSold(i)-A.ftp.*bought.dollsBought(i);
            profit.bought(i) = -A.ftp.*bought.dollsBought(i) + bought.dollsSold(i);
            bought.dollsBought(i) = (1-A.ftp).*bought.dollsBought(i);
            bought.sharesBought(i) = (1-A.ftp).*bought.sharesBought(i); 
            bought.tp1(i) = 1;
            action.long.tp1(i) = 1;
         elseif tmpprofit >= A.tp2  & bought.tp1(i)
            action.long.tp2Price(i) =  (1+A.tp2).*bought.dollsBought(i)./bought.sharesBought(i);
            bought.dollsSold(i) = (1-A.MakerFee).*bought.dollsBought(i).*(1+A.tp2);
            Funds(i)=Funds(i)+bought.dollsSold(i)- bought.dollsBought(i);
            profit.bought(i) = -bought.dollsBought(i) + bought.dollsSold(i);
            bought.dollsBought(i) = 0;
            bought.sharesBought(i) = 0; 
            stopLoss(i) = nan;
            bought.status(i)=0;
            bought.tp1(i)=0;
            action.long.tp2(i) = 1;
         end
         if A.dnSL
            if stopLoss(i) < (1-tt).*tmw.Close(i)
               stopLoss(i) = (1-tt).*tmw.Close(i);
            end
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
            action.short.slPrice(i) =  limitOrder(i);
            limitOrder(i)=nan;
            short.tp1(i) = 0;
            action.short.sl(i) = 1;
         elseif tmpprofit >= A.tp1 & ~short.tp1(i)
            action.short.tp1Price(i) =  (1-A.tp1).*short.dollsSold(i)./short.sharesSold(i);
            short.dollsBought(i) = (1-A.MakerFee).*A.ftp.*short.dollsSold(i).*(1-A.tp1);
            Funds(i)=Funds(i)+A.ftp.*short.dollsSold(i)-short.dollsBought(i);
            profit.short(i) = -short.dollsBought(i) + A.ftp.*short.dollsSold(i);
            short.dollsSold(i) = (1-A.ftp).*short.dollsSold(i);
            short.sharesSold(i) = (1-A.ftp).*short.sharesSold(i); 
            short.tp1(i) = 1;
            action.short.tp1(i) = 1;
         elseif tmpprofit >= A.tp2  & short.tp1(i)
            action.short.tp2Price(i) =  (1-A.tp2).*short.dollsSold(i)./short.sharesSold(i);
            short.dollsBought(i) = (1-A.MakerFee).*short.dollsSold(i).*(1-A.tp2);
            Funds(i)=Funds(i)+short.dollsSold(i)- short.dollsBought(i);
            profit.short(i) = -short.dollsBought(i) + short.dollsSold(i);
            short.dollsSold(i) = 0;
            short.sharesSold(i) = 0; 
            limitOrder(i) = nan;
            short.status(i)=0;
            short.tp1(i)=0;
            action.short.tp2(i) = 1;
         end
         if A.dnSL
            if limitOrder(i) > (1+tt).*tmw.Close(i)
               limitOrder(i) = (1+tt).*tmw.Close(i);
            end
         end
      end
  
      if shortSig(i) & bought.status(i) == 1
         bought.dollsSold(i) = (1-A.MakerFee).*bought.sharesBought(i)*tmw.Close(i);
         Funds(i)=Funds(i)+bought.dollsSold(i)-bought.dollsBought(i);
         profit.bought(i) = -bought.dollsBought(i) + bought.dollsSold(i);
         bought.dollsBought(i)=0;
         bought.sharesBought(i)=0;
         bought.status(i)=0;
         stopLoss(i) = nan;
         bought.tp1(i) = 0;
         action.long.close(i) = 1;
      end 
      if buySig(i) & short.status(i) ==1
         short.dollsBought(i) = (1-A.MakerFee).*short.sharesSold(i)*tmw.Close(i);
         Funds(i)=Funds(i)+short.dollsSold(i)-short.dollsBought(i);
         profit.short(i) = -short.dollsBought(i) + short.dollsSold(i);
         short.dollsSold(i)=0;
         short.sharesSold(i)=0;
         short.status(i)=0;
         limitOrder(i)=nan;
         short.tp1(i) = 0;
         action.short.close(i) = 1;
      end
      % Buy
      if buySig(i) & bought.status(i) == 0
         % Start market Order
         bought.dollsBought(i) = (1+A.TakerFee).*Funds(i).*A.useFund.*A.Leverage;
         bought.sharesBought(i) = (Funds(i).*A.useFund)/tmw.Close(i).*A.Leverage;      
         bought.status(i)=1;
         stopLoss(i) = (1-A.sstop).*tmw.Close(i);
         action.long.open(i) = 1;
      end
   
      % Shorting
      if shortSig(i) & short.status(i) == 0
         % Start short Order (Market price)
         short.dollsSold(i) = (1-A.TakerFee).*Funds(i).*A.useFund.*A.Leverage;
         short.sharesSold(i) = (Funds(i).*A.useFund)/tmw.Close(i).*A.Leverage;      
         short.status(i)=1;
         limitOrder(i) = (1+A.lstop).*tmw.Close(i);
         action.short.open(i) = 1;
      end
      if maxFund < Funds(i)
         maxFund = Funds(i);
      else
         tmpmaxdrawdown = (maxFund - Funds(i))/maxFund*100;
         maxdrawdown(maxdrawdown<tmpmaxdrawdown)=tmpmaxdrawdown;
      end
   
   end
   
   ccost=sum(profit.bought+profit.short);
   SumPerf.bought = bought;
   SumPerf.Funds = Funds;
   SumPerf.short=short;
   SumPerf.profit = profit;
   action.buySig = buySig;
   action.shortSig = shortSig;



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

