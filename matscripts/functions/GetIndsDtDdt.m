function [varnames,tmw] = GetIndsDtDdt(tmw,varnames,varargin)
A.option=[];
A=parse_pv_pairs(A,varargin);
ttmw=tmw;

for ff = 1 : length(varnames)
	dt = ttmw(:,varnames{ff}); dt{:,varnames{ff}}=nan; 
	dt{2:end,varnames{ff}} = diff(ttmw.(varnames{ff}));
        dt.Properties.VariableNames{varnames{ff}}=['d_',varnames{ff}];

	ddt = ttmw(:,varnames{ff}); ddt{:,varnames{ff}}=nan;
	ddt{3:end,varnames{ff}} = diff(ttmw.(varnames{ff}),2);
        ddt.Properties.VariableNames{varnames{ff}}=['dd_',varnames{ff}];	

	tmw = [tmw,dt(:,['d_',varnames{ff}]),ddt(:,['dd_',varnames{ff}])];
	varnames=[varnames,['d_',varnames{ff}],['dd_',varnames{ff}]];
end



