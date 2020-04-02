function [gains, drawdown,SumPerf,action] = plotSimOpt(Optim)

tstart=datetime('01-Oct-2019','Locale','en_US');
tend=datetime('05-Jan-2200','Locale','en_US');
ttime=timerange(tstart,tend,'closed');
Rroot='/home/euphotic_/yangino-bot/';
addpath(genpath(Rroot));
[~,TMW]=IngestBinance('rroot',Rroot);
strat = 2;
       [varnames,tmw] = TA.strat1(TMW.h, 'Timeindex',ttime,...
            'rfper',    round(Optim.ParOpt(1)),...
            'rfmult',   Optim.ParOpt(2),...
            'rsiper',   round(Optim.ParOpt(3)),...
            'jmaL',     round(Optim.ParOpt(4)),...
            'jmaphi',   round(Optim.ParOpt(5)),...
            'jmapow',  Optim.ParOpt(6),...
            'adxper',   round(Optim.ParOpt(7)),...
            'bollper',   round(Optim.ParOpt(8)),...
            'macdfast',  round(Optim.ParOpt(9)),...
            'macdsignal',round(Optim.ParOpt(10)),...
            'macdlong',  round(Optim.ParOpt(11)),...
            'sarinc',    Optim.ParOpt(12),...
            'sarmmax',   Optim.ParOpt(13),...
            'svolper',   round(Optim.ParOpt(14)),...
            'svolf',     Optim.ParOpt(15)...
            );
      [gains, drawdown,SumPerf,action] = cryptoSimulation_andyopt(tmw,'params',2,...
         'slscale1', Optim.ParOpt(16),...
         'slscale2', Optim.ParOpt(17),...
         'slscale3', Optim.ParOpt(18),...
         'slscale4', Optim.ParOpt(19),...
         'slmax', Optim.ParOpt(20),...
         'prelstop', Optim.ParOpt(21),...
         'presstop', Optim.ParOpt(22),...
         'adxth', Optim.ParOpt(23),...
         'rsiobos', Optim.ParOpt(24)...
         );


idxLongopen = find(action.long.open);
idxLongclose = find(action.long.close);
idxLongsl = find(action.long.sl);
idxLongtp1 = find(action.long.tp1);
idxLongtp2 = find(action.long.tp2);

idxShortopen = find(action.short.open);
idxShortclose = find(action.short.close);
idxShortsl = find(action.short.sl);
idxShorttp1 = find(action.short.tp1);
idxShorttp2 = find(action.short.tp2);

gr=[31, 82, 27]/255;
re=[150, 25, 18]/255;
bl=[43, 38, 135]/255;

keeph = 24*14*2;
Rroot='/home/euphotic_/yangino-bot/';

ttmw = tmw(end-keeph:end,:);

idxLongopen = find(action.long.open(end-keeph:end))+1;
idxLongclose = find(action.long.close(end-keeph:end))+1;
idxLongsl = find(action.long.sl(end-keeph:end));
idxLongtp1 = find(action.long.tp1(end-keeph:end));
idxLongtp2 = find(action.long.tp2(end-keeph:end));

idxShortopen = find(action.short.open(end-keeph:end))+1;
idxShortclose = find(action.short.close(end-keeph:end))+1;
idxShortsl = find(action.short.sl(end-keeph:end));
idxShorttp1 = find(action.short.tp1(end-keeph:end));
idxShorttp2 = find(action.short.tp2(end-keeph:end));
dy = 0;
fig=figure
set(fig, 'Units', 'centimeters', 'Position', [0, 0, 30, 10], 'PaperUnits', 'Inches', 'PaperSize', [30, 10]);
   candle(ttmw,'k');hold on;
   title('Bitcoin price');
   ylabel('USD')
   if ~isempty(idxLongopen)
      s=scatter(ttmw.Time(idxLongopen),ttmw.Low(idxLongopen).*(1-dy) ,...
         'MarkerEdgeColor','k','Marker','^','MarkerFaceColor',gr);
      t=labeldots(ttmw.Time(idxLongopen),ttmw.Low(idxLongopen),'LG','Color',gr);
   end
   if ~isempty(idxLongsl)
      ttmp=action.long.slPrice(end-keeph:end);
      s=scatter(ttmw.Time(idxLongsl),ttmp(idxLongsl) ,...
         'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr);
      s.SizeData=20;
      t=labeldots(ttmw.Time(idxLongsl),ttmw.Low(idxLongsl),'SL','Color',gr);
   end
   if ~isempty(idxLongclose)
      s=scatter(ttmw.Time(idxLongclose),ttmw.Low(idxLongclose) ,...
         'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr);
      s.SizeData=20;
      t=labeldots(ttmw.Time(idxLongclose),ttmw.Low(idxLongclose),'SL','Color',gr);
   end
   if ~isempty(idxLongtp1)
      ttmp=action.long.tp1Price(end-keeph:end);
      s=scatter(ttmw.Time(idxLongtp1),ttmp(idxLongtp1) ,...
         'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr);
      t=labeldots(ttmw.Time(idxLongtp1),ttmw.Low(idxLongtp1),'TP1','Color',bl);
   end
   if ~isempty(idxLongtp2)
      ttmp=action.long.tp2Price(end-keeph:end);
      s=scatter(ttmw.Time(idxLongtp2),ttmp(idxLongtp2) ,...
         'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr);
      t=labeldots(ttmw.Time(idxLongtp2),ttmw.Low(idxLongtp2),'TP2','Color',bl);
   end

   if ~isempty(idxShortopen)
      s=scatter(ttmw.Time(idxShortopen),ttmw.High(idxShortopen).*(1+dy) ,...
         'MarkerEdgeColor','k','Marker','^','MarkerFaceColor',re);
      t=labeldots(ttmw.Time(idxShortopen),ttmw.High(idxShortopen),'ST','Color',re,'dy',0.04);
   end
   if ~isempty(idxShortsl)
      ttmp=action.short.slPrice(end-keeph:end);
      s=scatter(ttmw.Time(idxShortsl),ttmp(idxShortsl),...
         'MarkerEdgeColor',re,'Marker','o','MarkerFaceColor',re);
      s.SizeData=20;
      t=labeldots(ttmw.Time(idxShortsl),ttmw.High(idxShortsl),'SL','Color',re,'dy',0.04);
   end
   if ~isempty(idxShortclose)
      s=scatter(ttmw.Time(idxShortclose),ttmw.High(idxShortclose) ,...
         'MarkerEdgeColor',re,'Marker','o','MarkerFaceColor',re');
      s.SizeData=20;
      t=labeldots(ttmw.Time(idxShortclose),ttmw.High(idxShortclose),'SL','Color',re,'dy',0.04);
   end
   if ~isempty(idxShorttp1)
      ttmp=action.long.tp1Price(end-keeph:end);
      s=scatter(ttmw.Time(idxShorttp1),ttmp(idxShorttp1) ,...
         'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr);
      t=labeldots(ttmw.Time(idxShorttp1),ttmw.Low(idxShorttp1),'TP1','Color',bl);
   end
   if ~isempty(idxShorttp2)
      ttmp=action.long.tp2Price(end-keeph:end);
      s=scatter(ttmw.Time(idxShorttp2),ttmp(idxShorttp2) ,...
         'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr);
      t=labeldots(ttmw.Time(idxShorttp2),ttmw.Low(idxShorttp2),'TP2','Color',bl);
   end
   xlim([ttmw.Time(1),ttmw.Time(end)]);

   hold off;

fig=figure
   set(fig, 'Units', 'centimeters', 'Position', [0, 0, 30, 10],...
      'PaperUnits', 'Inches', 'PaperSize', [30, 10]);
   plot(tmw.Time,SumPerf.Funds,'k','LineWidth',2);
   grid on;
   ylabel('USD');
   title('Simulated Profits (start fund: 10000 USD, use 50%, no leverage, reinvest 100%)');
   title('Yangy Crypto Bot simulated profits')
