function xNorm = BackNorm(xx,varargin)

A.BackNormWin = 14*24; % 2 week backwards
A=parse_pv_pairs(A,varargin);

winSize=[A.BackNormWin,0];

%x=(xx-movmean(xx,winSize,'Endpoints','fill'))./movstd(xx,winSize/2,'Endpoints','fill');
x=xx;
xNorm = (x - movmin(x,winSize,'omitnan','Endpoints','fill'))./(movmax(x,winSize,'omitnan','Endpoints','fill') - movmin(x,winSize,'omitnan','Endpoints','fill'));
%ps=fft(idShort(end-100:end))
%n=length(idShort(end-100:end));
%f = (0:n-1)*(1/n);
%power = abs(ps).^2/n;
%plot(1./f/24,power)
%xlabel('Frequency')
%ylabel('Power')




