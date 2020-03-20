function [trainInd, valInd, testInd]=divideIndCycle(yy,varargin)

 A.nblocks=1000;
 A.nsplit=[0.7,0.15,0.15];
 A= parse_pv_pairs(A,varargin);
 nidx=length(yy);

 for i = 1 : floor(nidx/A.nblocks)+1
   ini1=(i-1)*A.nblocks+1;
   ini2 = ini1+A.nblocks*A.nsplit(1);
   ini3 = ini1+A.nblocks*(A.nsplit(1)+A.nsplit(2));
   trainInd{i} = (ini1:ini2-1);
   valInd{i} = (ini2:ini3-1);
   testInd{i} = (ini3:i*A.nblocks);
 end
 i=floor(nidx/A.nblocks)+1;
 nblocksLeft=nidx-floor(nidx/A.nblocks)*A.nblocks;
 ini1=(floor(nidx/A.nblocks))*A.nblocks+1;
 ini2 = ini1+round(nblocksLeft*A.nsplit(1));
 ini3 = ini1+round(nblocksLeft*A.nsplit(1))+round(nblocksLeft*A.nsplit(2));
 trainInd{i} = (ini1:ini2-1);
 valInd{i} = (ini2:ini3-1);
 testInd{i} = (ini3:nidx);

 totids=length([trainInd{:}]) +length([valInd{:}]) +length([testInd{:}]);

 if totids ~= nidx
    error('Could not split properly');
 end

 trainInd=[trainInd{:}];
 valInd = [valInd{:}];
 testInd = [testInd{:}];
