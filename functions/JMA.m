function jma = JMA(tmw,varargin)
 A.L=200;
 A.phi=50;
 A.pow=2;
 A=parse_pv_pairs(A,varargin);

%Phase ratio
 if A.phi<-100; phi_r=0.5; elseif A.phi>100; phi_r=2.5; else; phi_r=A.phi/100+1.5;end;

%Beta
 Beta = (0.45*(A.L-1))./(0.45*(A.L-1)+2);

%Alpha
 Alpha = Beta.^A.pow;

 price = tmw.Close;
 e0 = nan(size(tmw.Close)); e0(1)=(1-Alpha)*price(1);
 e1 = nan(size(tmw.Close)); e1(1)=(price(1)-e0(1))*(1-Beta);
 e2 = nan(size(tmw.Close)); e2(1)=(e0(1)+phi_r*e1(1));
 e3 = nan(size(tmw.Close)); e3(1)=e2(1)*(1-Alpha)^2;
 jma = nan(size(tmw.Close)); jma(1)=e3(1);
 for i = 2 : length(tmw.Close)
   e0(i) = (1-Alpha)*price(i) + Alpha*e0(i-1);
   e1(i) = (price(i)-e0(i))*(1-Beta)+Beta*(e1(i-1));
   e2(i) = e0(i) + phi_r*e1(i);
   e3(i) = (e2(i) - jma(i-1))*(1-Alpha)^2+Alpha^2*e3(i-1);
   jma(i) = e3(i)+jma(i-1);
 end


