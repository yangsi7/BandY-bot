function plotPerf(tmw,varargin)
A.method={'fitrensemble'};
A=parse_pv_pairs(A,varargin);


if strcmp(A.method,'fitcensemble')
        bbounds=[0 0.15 0.3 0.6 0.75 1];
	dpriceNorm = discretize(tmw.priceNorm,bbounds,'categorical');
	dpriceNormS=nan(size(dpriceNorm));
	dyhat_fceS=dpriceNormS;
	cats1=categories(dpriceNorm);
	cats2=categories(tmw.yhat_fce);
	ncats=length(bbounds)-1;
	for i = 1 : ncats
		idx = find(dpriceNorm==cats1(i));
		dpriceNormS(idx) = bbounds(i)+(bbounds(i+1)-bbounds(i))/2;
		idx = find(tmw.yhat_fce==cats2(i));
		dyhat_fceS(idx) = bbounds(i)+(bbounds(i+1)-bbounds(i))/2;
	end
	figure
        subplot(2,1,1)
        candle(tmw);hold on;grid on;
        plot(tmw.Time,tmw.hlc,'k','LineWidth',2); hold off;
        subplot(2,1,2)
        plot(tmw.Time,dpriceNormS,'k','LineWidth',2);hold on;grid on;
        plot(tmw.Time,dyhat_fceS,'r','LineWidth',2); hold off;	
end

if strcmp(A.method,'fitrensemble')
        figure
	subplot(2,1,1)
	%candle(tmw);hold on;grid on;
	plot(tmw.Time,tmw.hlc,'k','LineWidth',2); hold off;
	subplot(2,1,2)
	plot(tmw.Time,tmw.Hotness,'k','LineWidth',2);hold on;grid on;
	plot(tmw.Time,tmw.yhat_fre,'r','LineWidth',2); hold off;
end

