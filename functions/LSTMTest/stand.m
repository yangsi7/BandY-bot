function [datastand, p] = stand(data,varargin)
A.stand=1;
A.params = [];
A=parse_pv_pairs(A,varargin);

 if A.stand
   open = data(1,:);
   low = data(3,:);
   high = data(4,:);
   close = data(2,:);
   volume = data(5,:);
   if isempty(A.params)
      p.uclose = mean(close);
      p.sclose = std(close);
      p.uvolume = mean(volume);
      p.svolume = std(volume);
   else
      p = A.params;
   end

   closeNorm = (close-p.uclose)./p.sclose;
   volumeNorm = (volume-p.uvolume)./p.svolume;

   datastand = [open./close.*closeNorm;closeNorm...
         ;low./close.*closeNorm;high./close.*closeNorm;volumeNorm];
 else
    fopen = data(1,:)./data(2,:);
    flow = data(3,:)./data(2,:);
    fhigh = data(4,:)./data(2,:);    

    close = (data(2,:).*p.sclose)+uclose;
    volume = (data(5,:).*p.volume)+uvolume;
    datastand = [fopen.*close; close;flow.*close;fhigh.*close;volume];
 end
