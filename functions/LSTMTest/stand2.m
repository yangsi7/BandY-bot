function [datastand, p] = stand(data,varargin)
A.stand=1;
A.win = [24*30,0];
A.params = [];
A=parse_pv_pairs(A,varargin);

 if A.stand
   open = data(1,:);
   low = data(3,:);
   high = data(4,:);
   close = data(2,:);
   volume = data(5,:);
   if isempty(A.params)
      p.uclose = movmean(close,A.win);
      p.sclose = movstd(close,A.win);
      p.uvolume = movmean(volume,A.win);
      p.svolume = movstd(volume,A.win);
   else
      p = A.params;
   end

   closeNorm = (close-p.uclose)./p.sclose;
   volumeNorm = (volume-p.uvolume)./p.svolume;

   closemin=min(closeNorm);
   closeNorm = closeNorm-closemin;
   datastand = [open./close.*closeNorm+closemin;closeNorm+closemin...
         ;low./close.*closeNorm+closemin;high./close.*closeNorm+closemin;volumeNorm];
 else
    fopen = data(1,:)./data(2,:);
    flow = data(3,:)./data(2,:);
    fhigh = data(4,:)./data(2,:);    

    close = (data(2,:).*p.sclose)+uclose;
    volume = (data(5,:).*p.volume)+uvolume;
    datastand = [fopen.*close; close;flow.*close;fhigh.*close;volume];
 end
