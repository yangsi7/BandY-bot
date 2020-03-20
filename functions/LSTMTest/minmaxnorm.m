function XNorm=minmaxnorm(X,varargin)
A.par.mmin = [];
A.par.mmax = [];
A=parse_pv_pairs(A,varargin);
if isempty(A.par.mmin)
   XNorm = (X-nanmin(X))./(nanmax(X)-nanmin(X));
 else
   XNorm = (X-A.par.mmin)./(A.par.mmax-A.par.mmin);
end
