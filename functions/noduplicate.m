function [indxBuy,indxSell] = noduplicate(tmw,indxBuy,indxSell)

indxsigs = sort([indxBuy;indxSell]);
for i = 1 : length(indxsigs)
   if isnan(indxsigs(i)); continue; end
   count =0;
   if sum(indxsigs(i) == indxBuy) >0
      count =0;
      while 1
         if  i+count > length(indxsigs)
            break;
         elseif sum(indxsigs(i+count) == indxBuy) == 1
            count = count + 1;
         else
            break;
         end
      end
      if count > 1
         [~,idkeep] = nanmin(tmw.Close(indxsigs(i:i-1+count)));
         for j = 1 : count
            if j ~= idkeep
               idx = find(indxBuy == indxsigs(i+j-1));
               i
               idx
               indxBuy(idx)=nan;
               indxsigs(i+j-1) = nan;
            end
         end
      end
   elseif sum(indxsigs(i) == indxSell) > 0
      count = 0;
      while 1
         if  i+count > length(indxsigs)
            break;
         elseif sum(indxsigs(i+count) == indxSell) == 1
            count = count + 1;
         else
            break;
         end
      end
      if count > 1
         [~,idkeep] = nanmax(tmw.Close(indxsigs(i:i+count-1)));
         for j = 1 : count
            if j ~= idkeep
               idx = find(indxSell == indxsigs(i+j-1));
               indxSell(idx)=nan;
               indxsigs(i+j-1) = nan;
            end
         end
      end
   end
end


indxBuy = indxBuy(~isnan(indxBuy));
indxSell = indxSell(~isnan(indxSell));
