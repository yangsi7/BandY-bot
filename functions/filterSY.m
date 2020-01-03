function y = filterSY(x,varargin)
A.windowSize = 30*24; % 30 days
A=parse_pv_pairs(A,varargin);

b = (1/A.windowSize)*ones(1,A.windowSize);
a = 1;
y = filter(b,a,x);
