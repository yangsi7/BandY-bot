function [t] = labeldots(x,y,str,varargin)
A.dx = -0.005;
A.dy = -0.04;
A.Color=[0,0,0];
A=parse_pv_pairs(A,varargin);

yrange = range(ylim);

dx = A.dx * range(xlim);
dy = A.dy * range(ylim);

c = cellstr(str);
t=text(x+dx, y+dy, c,'Color',A.Color,'Fontsize', 6);
