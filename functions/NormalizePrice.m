function [tmw] = NormalizePrice(tmw,varargin)

A.windowsize = [14*24, 0]; % 2 week backwards
A=parse_pv_pairs(A,varargin);
ttmw=tmw;
% Normalize with respects to Close prices
tmw.Close=(tmw.Close - movmin(ttmw.Low,A.windowsize))./(movmax(ttmw.High,A.windowsize) - movmin(ttmw.Low,A.windowsize));
tmw.Open=(tmw.Open - movmin(ttmw.Low,A.windowsize))./(movmax(ttmw.High,A.windowsize) - movmin(ttmw.Low,A.windowsize));
tmw.High=(tmw.High - movmin(ttmw.Low,A.windowsize))./(movmax(ttmw.High,A.windowsize) - movmin(ttmw.Low,A.windowsize)); 
tmw.Low=(tmw.Low - movmin(ttmw.Low,A.windowsize))./(movmax(ttmw.High,A.windowsize) - movmin(ttmw.Low,A.windowsize));
tmw.Volume=(tmw.Volume - movmin(tmw.Volume,A.windowsize))./(movmax(tmw.Volume,A.windowsize) - movmin(tmw.Volume,A.windowsize));



%tmw.Open=(tmw.Open - movmin(tmw.Open,A.windowsize))./(movmax(tmw.Open,A.windowsize) - movmin(tmw.Open,A.windowsize));
%tmp = tmw.High./tmw.Close;
%tmw.High=tmw.Close.*tmp;
%tmp = tmw.Low./tmw.Close;
%tmw.Low=tmw.Close.*tmp;
%tmw.Volume=(tmw.Volume - movmin(tmw.Volume,A.windowsize))./(movmax(tmw.Volume,A.windowsize) - movmin(tmw.Volume,A.windowsize));



