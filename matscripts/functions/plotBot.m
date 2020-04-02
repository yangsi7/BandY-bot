function out = plotBot()
   out=[];
   tstart=datetime('01-Nov-2019','Locale','en_US');
   tend=datetime('05-Jan-2200','Locale','en_US');
   ttime=timerange(tstart,tend,'closed');
   Rroot='/home/euphotic_/yangino-bot/';
   addpath(genpath(Rroot));
   [~,TMW]=IngestBinance('rroot',Rroot);
strat = 2;
if strat == 2
   [varnames,tmw] = TA.strat1(TMW.h,'Timeindex', ttime,...
      'rfper',15,...
      'rfmult',1.68,...
      'rsiper',18.2,...
      'jmaL',22,...
      'jmaphi', 70,...
      'jmapow',2.8837,...
      'adxper',19,...
      'bollper',13,...
      'macdfast',9,...
      'macdsignal',12,...
      'macdlong',12,...
      'sarinc',0.65,...
      'sarmmax',0.041,...
      'svolper',42,...
      'svolf',1.77 ...
      );
else
   [varnames,tmw] = TA.strat1(TMW.h,'Timeindex', ttime);
end
   [gains, drawdown,SumPerf,action] = cryptoSimulation_andyopt(tmw);
   
   
   idxLongopen = find(action.long.open);
   idxLongclose = find(action.long.close);
   idxLongsl = find(action.long.sl);
   idxLongtp1 = find(action.long.tp1);
   idxLongtp2 = find(action.long.tp2);
   idxLongSig = find(action.buySig);
   
   idxShortopen = find(action.short.open);
   idxShortclose = find(action.short.close);
   idxShortsl = find(action.short.sl);
   idxShorttp1 = find(action.short.tp1);
   idxShorttp2 = find(action.short.tp2);
   idxShortSig = find(action.shortSig);
   
   gr=[31, 82, 27]/255;
   re=[150, 25, 18]/255;
   bl=[43, 38, 135]/255;
   
   keeph = 24*14;
   Rroot='/home/euphotic_/yangino-bot/';
   
   ttmw = tmw(end-keeph:end,:);
   
   idxLongopen = find(action.long.open(end-keeph:end))+1;
   idxLongclose = find(action.long.close(end-keeph:end))+1;
   idxLongsl = find(action.long.sl(end-keeph:end));
   idxLongtp1 = find(action.long.tp1(end-keeph:end));
   idxLongtp2 = find(action.long.tp2(end-keeph:end));
   idxLongSig = find(action.buySig(end-keeph:end))+1;
   
   idxShortopen = find(action.short.open(end-keeph:end))+1;
   idxShortclose = find(action.short.close(end-keeph:end))+1;
   idxShortsl = find(action.short.sl(end-keeph:end));
   idxShorttp1 = find(action.short.tp1(end-keeph:end));
   idxShorttp2 = find(action.short.tp2(end-keeph:end));
   idxShortSig = find(action.shortSig(end-keeph:end))+1;
   
   %csvhistpath = '/home/euphotic_/yangino-bot/pythonBinance/Data/BinchBTCUSDT1h_Dec2019_Journal.csv';
   %opts = detectImportOptions(csvhist)
   %csvhist = readtable(csvhist,opts);
   %refTime = datenum([1970,01,01,01,01,01]);
   %times = datestr(refTime + bla.timestmp./(86400));
   %histbot.idxLongopen = find(strcmp(csvhist.BlO,{'True'}));
   %histbot.idxLongsl = find(strcmp(csvhist.Blsl,{'True'}));
   %histbot.idxLongtp1 = find(strcmp(csvhist.Bltp1,{'True'}));
   %histbot.idxLongtp2 = find(strcmp(csvhist.Bltp2,{'True'}));
   %
   %histbot.idxShortopen = find(strcmp(csvhist.BsO,{'True'}));
   %histbot.idxShortsl = find(strcmp(csvhist.Bssl,{'True'}));
   %histbot.idxShorttp1 =  find(strcmp(csvhist.Bstp1,{'True'}));
   %histbot.idxShorttp2 =  find(strcmp(csvhist.Bstp2,{'True'}));
   %
   %histbot.
   
   
   fig=figure('visible','off');
   set(fig, 'Units', 'centimeters', 'Position', [0, 0, 30, 10], 'PaperUnits', 'Inches', 'PaperSize', [30, 10]);
      candle(ttmw,'k');hold on;
      title('Bitcoin price');
      ylabel('USD')
      if ~isempty(idxLongSig)
         for i = 1 : length(idxLongSig)
            xline(ttmw.Time(idxLongSig(i)),'Color',gr,'LineWidth',2.75,'alpha',0.25);
         end
      end
      if ~isempty(idxLongopen)
         s=scatter(ttmw.Time(idxLongopen),ttmw.Open(idxLongopen) ,...
            'MarkerEdgeColor','k','Marker','^','MarkerFaceColor',gr,'SizeData',10);
         t=labeldots(ttmw.Time(idxLongopen),ttmw.Low(idxLongopen),'LG','Color',gr);
      end
      if ~isempty(idxLongsl)
         ttmp=action.long.slPrice(end-keeph:end);
         s=scatter(ttmw.Time(idxLongsl),ttmp(idxLongsl) ,...
            'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr);
         s.SizeData=10;
         t=labeldots(ttmw.Time(idxLongsl),ttmw.Low(idxLongsl),'SL','Color',gr);
      end
      if ~isempty(idxLongclose)
         s=scatter(ttmw.Time(idxLongclose),ttmw.Open(idxLongclose) ,...
            'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr,'SizeData',10);
         s.SizeData=10;
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
  
      if ~isempty(idxShortSig)
         for i = 1 : length(idxShortSig)
            xline(ttmw.Time(idxShortSig(i)),'Color',re,'LineWidth',2.75,'alpha',0.25);
         end
      end 
      if ~isempty(idxShortopen)
         s=scatter(ttmw.Time(idxShortopen),ttmw.Open(idxShortopen) ,...
            'MarkerEdgeColor','k','Marker','^','MarkerFaceColor',re,'SizeData',10);
         t=labeldots(ttmw.Time(idxShortopen),ttmw.High(idxShortopen),'ST','Color',re,'dy',0.04);
      end
      if ~isempty(idxShortsl)
         ttmp=action.short.slPrice(end-keeph:end);
         s=scatter(ttmw.Time(idxShortsl),ttmp(idxShortsl),...
            'MarkerEdgeColor',re,'Marker','o','MarkerFaceColor',re);
         s.SizeData=10;
         t=labeldots(ttmw.Time(idxShortsl),ttmw.High(idxShortsl),'SL','Color',re,'dy',0.04);
      end
      if ~isempty(idxShortclose)
         s=scatter(ttmw.Time(idxShortclose),ttmw.Open(idxShortclose) ,...
            'MarkerEdgeColor',re,'Marker','o','MarkerFaceColor',re,'SizeData',10);
         s.SizeData=10;
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
   saveas(fig,'/home/euphotic_/yangino-bot/figures/bothist','png');
   
