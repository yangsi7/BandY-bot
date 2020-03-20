function y = filterSY(x,varargin)
A.windowSize = 30*24; % 30 days
A.filter=1;
A=parse_pv_pairs(A,varargin);

b = (1/A.windowSize)*ones(1,A.windowSize);
a = [1]
if A.filter == 0
   y = filtfilt(b,a,x);
end
if A.filter == 1
   y = filter(b,a,x);
end
