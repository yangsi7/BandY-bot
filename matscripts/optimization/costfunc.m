function out = costfunc(SumPerf,varargin)
A.tscale = 14*24; % in hours
A.func = 1;
A.step = 24;
A=parse_pv_pairs(A,varargin);

n = length(SumPerf.Funds);

[lgTot, stTot, allTot] =  evalperf(SumPerf);

out.lgTot=lgTot;
out.stTot=stTot;
out.allTot=allTot;

for j = 1 : A.step:n-A.tscale
   tmp.Funds = SumPerf.Funds(j:j+A.tscale);
   tmp.profit.bought = SumPerf.profit.bought(j:j+A.tscale);
   tmp.profit.short = SumPerf.profit.short(j:j+A.tscale);
   [ttmplg, ttmpst, ttmpall] =  evalperf(tmp);
   if j == 1
      tmplg=ttmplg;
      tmpst=ttmpst;
      tmpall=ttmpall;
   elseif j >1
      tmplg=[tmplg,ttmplg];
      tmpst=[tmpst,ttmpst];
      tmpall=[tmpall,ttmpall];
   end
end

ffields = fields(tmpall);
for ff = 1 : length(ffields)
   try
      all.(ffields{ff}) = cat(1,tmpall.(ffields{ff}));
      lg.(ffields{ff}) = cat(1,tmplg.(ffields{ff}));
      st.(ffields{ff}) = cat(1,tmpst.(ffields{ff}));
   end
end

out.cycle.nwins = mean(all.nwins);
out.cycle.nloses = mean(all.nloses);
out.cycle.rwin = nanmean(all.nwins./(all.nwins+all.nloses));
out.cycle.NP = mean(all.NP);
out.cycle.avg_rtrn = mean(all.avg_rtrn);
out.cycle.NP = mean(all.NP);
out.cycle.GP = mean(all.GP);
out.cycle.GL = mean(all.GL);
all.PR(isnan(all.PR)|all.PR==-inf|all.PR==inf)=nan;
out.cycle.avgPR = nanmean(all.PR);
out.cycle.avginvPR =1./out.cycle.avgPR; 
out.cycle.PR = out.cycle.GP./out.cycle.GL;
out.cycle.invPR = out.cycle.GL./out.cycle.GP;
out.cycle.netPR =out.cycle.NP./out.cycle.GL ;
out.cycle.netinvPR = 1./out.cycle.netPR;
out.cycle.stdPR =out.cycle.PR.*out.cycle.netPR;
out.cycle.invstdPR = 1./out.cycle.stdPR;

   function [lg,st,all] = evalperf(sumry)
      rtrn = zeros(size(sumry.Funds));
      rtrn(2:end) = (sumry.Funds(2:end)-sumry.Funds(1:end-1))./sumry.Funds(1:end-1)*100;
      % Buys
      lg.idwins = find(sumry.profit.bought>0);
      lg.idloses = find(sumry.profit.bought<0);
      lg.idtrades = find(sumry.profit.bought~=0);
      lg.ntrades = length(lg.idtrades);
      lg.nloses = length(lg.idloses);
      lg.nwins = length(lg.idwins);
      lg.GP = sum(sumry.profit.bought(lg.idwins));
      lg.GL = sum(sumry.profit.bought(lg.idloses))*-1;
      lg.NP = lg.GP-lg.GL;
      lg.PR = lg.GP./lg.GL;
      lg.invPR = lg.GL./lg.GP;
      lg.avg_GPrtrn = mean(rtrn(lg.idwins));
      lg.avg_GLrtrn = mean(rtrn(lg.idloses))*-1;
      lg.PRrtrn = lg.avg_GPrtrn./lg.avg_GLrtrn;
      lg.invPRrtrn = lg.avg_GLrtrn./lg.avg_GPrtrn*-1;
      lg.avg_rtrn = mean(rtrn(lg.idtrades));
      
      st.idwins = find(sumry.profit.short>0);
      st.idloses = find(sumry.profit.short<0);
      st.idtrades = find(sumry.profit.short~=0);
      st.ntrades = length(st.idtrades);
      st.nloses = length(st.idloses);
      st.nwins = length(st.idwins);
      st.GP = sum(sumry.profit.short(st.idwins));
      st.GL = sum(sumry.profit.short(st.idloses))*-1;
      st.NP = st.GP-st.GL;
      st.PR = st.GP./st.GL;
      st.invPR = st.GL./st.GP;
      st.avg_GPrtrn = mean(rtrn(st.idwins));
      st.avg_GLrtrn = mean(rtrn(st.idloses))*-1;
      st.PRrtrn = st.avg_GPrtrn./st.avg_GLrtrn*-1;
      st.invPRrtrn = st.avg_GLrtrn./st.avg_GPrtrn*-1;
      st.avg_rtrn = mean(rtrn(st.idtrades));
      
      all.idwins = find(sumry.profit.short>0 | sumry.profit.bought>0);
      all.idloses = find(sumry.profit.short<0 | sumry.profit.bought<0);
      all.idtrades = find(sumry.profit.short~=0 | sumry.profit.bought~=0);
      all.ntrades = length(all.idtrades);
      all.nloses = length(all.idloses);
      all.nwins = length(all.idwins);
      all.GP = lg.GP + st.GP;
      all.GL = lg.GL + st.GL;
      all.NP = all.GP-all.GL;
      all.PR = all.GP./all.GL;
      all.invPR = all.GL./all.GP;
      all.avg_GPrtrn = mean(rtrn(all.idwins));
      all.avg_GLrtrn = mean(rtrn(all.idloses))*-1;
      all.PRrtrn = all.avg_GPrtrn./all.avg_GLrtrn*-1;
      all.invPRrtrn = all.avg_GLrtrn./all.avg_GPrtrn*-1;
      all.avg_rtrn = mean(rtrn(all.idtrades));
      all.cwins(1) = 0;
      all.closes(1)=0;
      for i = 1 : all.ntrades
         Bwins(i) = sum(all.idtrades(i)==all.idwins)>0;
         Bloses(i) = sum(all.idtrades(i)==all.idloses)>0;
         if i==1
            if Bwins(1);  all.cwins(1) = 1; else all.cwins(1) =0;end;
            if Bloses(1);  all.closes(1) = 1; else all.closes(1) = 0;end;
         else
            if  Bwins(i) & all.cwins(i-1) >0 
               all.cwins(i) = all.cwins(i-1)+ 1;
            elseif Bwins(i) & all.cwins(i-1) == 0
               all.cwins(i) = 1;
            else
               all.cwins(i) = 0;
            end
            if  Bloses(i) & all.closes(i-1) >0 
               all.closes(i) = all.closes(i-1)+ 1;
            elseif  Bloses(i) & all.closes(i-1) ==0
               all.closes(i) = 1;
            else 
               all.closes(i) =0;
            end
         end
      end
      all.maxcwins = max(all.cwins);
      all.maxcloses = max(all.closes);
   end
end

