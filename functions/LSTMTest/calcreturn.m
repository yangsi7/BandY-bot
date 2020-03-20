function [returnLong,returnShort] = calcreturn(price,high,low,varargin)
A.stop = 0.01;
A=parse_pv_pairs(A,varargin);

returnShort=nan(size(price));
returnLong=nan(size(price));
for l = 1 : length(price)
   stopLong = price(l)*(1-A.stop);
   for k = l+1 : length(price)
      if low(k)<=stopLong
         returnLong(l) = (stopLong - price(l))./price(l);
         break;
      else
         if stopLong < price(k)*(1-A.stop)
            stopLong = price(k)*(1-A.stop);
         end
      end
   end
end

for l = 1 : length(price)
   stopShort = price(l)*(1+A.stop);
   for k = l+1 : length(price)
      if high(k)>=stopShort
         returnShort(l) = (-stopShort + price(l))./price(l);
         break;
      else
         if stopShort > price(k)*(1+A.stop);
            stopShort = price(k)*(1+A.stop);
         end
      end
   end
end

