classdef viewBot
   methods(Static)
      function out = plotBot()
         out=[];
         tstart=datetime('01-Nov-2019','Locale','en_US');
         tend=datetime('05-Jan-2200','Locale','en_US');
         ttime=timerange(tstart,tend,'closed');
         Rroot='/home/euphotic_/yangino-bot/';
         marSize = 12;
         addpath(genpath(Rroot));
         [~,TMW]=IngestBinance('rroot',Rroot);
         strat = 3;
         if strat == 2
            [varnames,tmw] = TA.strat1(TMW.h,'Timeindex', ttime,...
               'rfper',15,...
               'rfmult',1.68,...
               'rsiper',18,...
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
         elseif strat == 3
            [varnames,tmw] = TA.strat1(TMW.h,'Timeindex', ttime,...
                  'rfper',35,...
                  'rfmult',1.773387316083307,...
                  'rsiper',20,...
                  'jmaL',16,...
                  'jmaphi', 37,...
                  'jmapow',2.667985158500809,...
                  'adxper',19,...
                  'bollper',19,...
                  'macdfast',6,...
                  'macdsignal',2,...
                  'macdlong',13,...
                  'sarinc',0.136927458933461,...
                  'sarmmax',0.109025275697910,...
                  'svolper',59,...
                  'svolf',2 ...
               );
            else
            [varnames,tmw] = TA.strat1(TMW.h,'Timeindex', ttime);
         end
         [gains, drawdown,SumPerf,action] = cryptoSimulation(tmw,'params',2);
         
         
         idxLongopen = find(action.long.open);
         idxLongclose = find(action.long.close);
         idxLongsl = find(action.long.sl);
         idxLongSig = find(action.buySig);
         
         idxShortopen = find(action.short.open);
         idxShortclose = find(action.short.close);
         idxShortsl = find(action.short.sl);
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
         idxLongSig = find(action.buySig(end-keeph:end))+1;
         
         idxShortopen = find(action.short.open(end-keeph:end))+1;
         idxShortclose = find(action.short.close(end-keeph:end))+1;
         idxShortsl = find(action.short.sl(end-keeph:end));
         idxShortSig = find(action.shortSig(end-keeph:end))+1;
         
         
         histbot = viewBot.getBotHist(); 
         
         
         fig=figure('visible','off');
         set(fig, 'Units', 'centimeters', 'Position', [0, 0, 30, 25], 'PaperUnits', 'Inches', 'PaperSize', [30, 25]);
         subplot(2,1,2)
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
                  'MarkerEdgeColor','k','Marker','^','MarkerFaceColor',gr,'SizeData',marSize);
               t=labeldots(ttmw.Time(idxLongopen),ttmw.Low(idxLongopen),'LG','Color',gr);
            end
            if ~isempty(idxLongsl)
               ttmp=action.long.slPrice(end-keeph:end);
               s=scatter(ttmw.Time(idxLongsl),ttmp(idxLongsl) ,...
                  'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr);
               s.SizeData=marSize;
               t=labeldots(ttmw.Time(idxLongsl),ttmw.Low(idxLongsl),'SL','Color',gr);
            end
            if ~isempty(idxLongclose)
               s=scatter(ttmw.Time(idxLongclose),ttmw.Open(idxLongclose) ,...
                  'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr,'SizeData',marSize);
               s.SizeData=marSize;
               t=labeldots(ttmw.Time(idxLongclose),ttmw.Low(idxLongclose),'SL','Color',gr);
            end
            if ~isempty(idxShortSig)
               for i = 1 : length(idxShortSig)
                  xline(ttmw.Time(idxShortSig(i)),'Color',re,'LineWidth',2.75,'alpha',0.25);
               end
            end 
            if ~isempty(idxShortopen)
               s=scatter(ttmw.Time(idxShortopen),ttmw.Open(idxShortopen) ,...
                  'MarkerEdgeColor','k','Marker','^','MarkerFaceColor',re,'SizeData',marSize);
               t=labeldots(ttmw.Time(idxShortopen),ttmw.High(idxShortopen),'ST','Color',re,'dy',0.04);
            end
            if ~isempty(idxShortsl)
               ttmp=action.short.slPrice(end-keeph:end);
               s=scatter(ttmw.Time(idxShortsl),ttmp(idxShortsl),...
                  'MarkerEdgeColor',re,'Marker','o','MarkerFaceColor',re);
               s.SizeData=marSize;
               t=labeldots(ttmw.Time(idxShortsl),ttmw.High(idxShortsl),'SL','Color',re,'dy',0.04);
            end
            if ~isempty(idxShortclose)
               s=scatter(ttmw.Time(idxShortclose),ttmw.Open(idxShortclose) ,...
                  'MarkerEdgeColor',re,'Marker','o','MarkerFaceColor',re,'SizeData',marSize);
               s.SizeData=marSize;
               t=labeldots(ttmw.Time(idxShortclose),ttmw.High(idxShortclose),'SL','Color',re,'dy',0.04);
            end
            xlim([ttmw.Time(1),ttmw.Time(end)]);
         
            hold off;
         subplot(2,1,1)
            candle(ttmw,'k');hold on;
            title('Bitcoin price');
            ylabel('USD')
            if ~isempty(idxLongSig)
               for i = 1 : length(idxLongSig)
                  xline(ttmw.Time(idxLongSig(i)),'Color',gr,'LineWidth',2.75,'alpha',0.25);
               end
            end
            if ~isempty(histbot.idxLongopen)
               s=scatter(histbot.times(histbot.idxLongopen),histbot.Longopenprice ,...
                  'MarkerEdgeColor','k','Marker','^','MarkerFaceColor',gr,'SizeData',marSize);
               t=labeldots(histbot.times(histbot.idxLongopen),histbot.Longopenprice,'LG','Color',gr);
            end
            if ~isempty(histbot.idxLongsl)
               s=scatter(histbot,times(histbot.idxLongsl),histbot.LongSLprice,...
                  'MarkerEdgeColor',gr,'Marker','o','MarkerFaceColor',gr);
               s.SizeData=marSize;
               t=labeldots(histbot,times(histbot.idxLongsl),histbot.LongSLprice,'SL','Color',gr);
            end
            if ~isempty(idxShortSig)
               for i = 1 : length(idxShortSig)
                  xline(ttmw.Time(idxShortSig(i)),'Color',re,'LineWidth',2.75,'alpha',0.25);
               end
            end 
            if ~isempty(histbot.idxShortopen)
               s=scatter(histbot.times(histbot.idxShortopen),histbot.Shortopenprice ,...
                  'MarkerEdgeColor','k','Marker','^','MarkerFaceColor',re,'SizeData',marSize);
               t=labeldots(histbot.times(histbot.idxShortopen),histbot.Shortopenprice,'ST','Color',re,'dy',0.04);
            end
%            if ~isempty(histbot.idxShortsl)
%               s=scatter(histbot.times(histbot.idxShortsl),histbot.ShortSLprice,...
%                  'MarkerEdgeColor',re,'Marker','o','MarkerFaceColor',re);
%               s.SizeData=marSize;
%               t=labeldots(histbot.times(histbot.idxShortsl),histbot.ShortSLprice,'SL','Color',re,'dy',0.04);
%            end
            xlim([ttmw.Time(1),ttmw.Time(end)]);
         
            hold off;
         saveas(fig,'/home/euphotic_/yangino-bot/figures/bothist','png');


      end %plotBot

      function idxout = notconsecutive(idx)
         idxout=[];
         for i = 1 : length(idx)
            if i == 1
               count = 1;
               idxout(1) = idx(1);
            else
               if idx(i)-1 ~= idx(i-1)
                  count = count + 1;
                  idxout(count) = idx(i);
               end
            end
         end
      end % notconsecutive

      function histbot = getBotHist()
         csvhistpath = '/home/euphotic_/yangino-bot/pythonBinance/Data/BinchBTCUSDT1h_Dec2019_Journal.csv';
         opts = detectImportOptions(csvhistpath);
         csvhist = readtable(csvhistpath,opts);
         refTime = datenum([1970,01,01,01,01,01]);
         histbot.times = datetime(refTime + (csvhist.timestmp-3600)./(86400),'ConvertFrom','datenum');
         histbot.idxLongopen = viewBot.notconsecutive(find(strcmp(csvhist.BlO,{'True'})));
         if ~isempty(histbot.idxLongopen)
            histbot.Longopenprice = csvhist.BprlO(histbot.idxLongopen);
         end
         histbot.idxLongsl = viewBot.notconsecutive(find(strcmp(csvhist.BlSLh,{'True'})));
         if ~isempty(histbot.idxLongsl)
            histbot.LongSLprice = csvhist.BprlSL;
         end
         histbot.idxShortopen = viewBot.notconsecutive(find(strcmp(csvhist.BsO,{'True'})));
         if ~isempty(histbot.idxShortopen)
            histbot.Shortopenprice = csvhist.BprsO(histbot.idxShortopen);
         end
         histbot.idxShortsl= viewBot.notconsecutive(find(strcmp(csvhist.BsSLh,{'True'})));
         if ~isempty(histbot.idxShortsl)
            histbot.ShortSLprice = csvhist.BprsSL(histbot.idxShortsl);
         end
      end % getBotHist
   end
end
   
