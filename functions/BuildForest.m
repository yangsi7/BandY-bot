function [Mdl,varSelect]=BuildForest(tmw,varargin)
A.TimeIndex = timerange(datetime('01-Jan-2019','Locale','en_US'),datetime('01-May-2019','Locale','en_US'),'closed');
A.PredictorImportance = 1;
A.normWin=150;
A.varnames={'Open','High','Low','Close','Volume'};
A=parse_pv_pairs(A,varargin);

tmw = tmw(A.TimeIndex,:);
idxNnan=~isnan(tmw.Hotness(:));
tmw=tmw(idxNnan,:);

X=table2array(tmw(:,A.varnames));

if A.PredictorImportance
	t = templateTree('NumVariablesToSample','all',...
	    'PredictorSelection','interaction-curvature','Surrogate','on');
	Mdl = fitrensemble(X,tmw.Hotness,'Method','Bag','NumLearningCycles',200, ...
	    'Learners',t);
        options = statset('UseParallel',true);
	impr.OOB = oobPermutedPredictorImportance(Mdl,'Options',options);
%	[impr.Gain,impr.predAssociation] = predictorImportance(Mdl);
	try
		fig=figure
		set(fig, 'Units', 'centimeters', 'Position', [0, 0, 55,20], 'PaperUnits', 'centimeters', 'PaperSize', [55 20]);
		[~,idx]=sort(impr.OOB,'descend');
		bar(impr.OOB(idx))
		title('Unbiased Predictor Importance Estimates (OOB pred-permutation)')
		ylabel('Importance')
		h = gca;
		tticks=(1:length(A.varnames));
		h.XTick=tticks;
		h.XTickLabel = A.varnames(idx);
		h.XTickLabelRotation = 45;
		h.TickLabelInterpreter = 'none';
                impr.OOB=impr.OOB(idx);
                varSelect=A.varnames(idx(1:100));
                X = X(:,idx(1:100));
	catch
	end
else
	varSelect=A.varnames;
end
t = templateTree('PredictorSelection','interaction-curvature','Surrogate','off');
Mdl = fitrensemble(X,tmw.Hotness,'Method','Bag','NumLearningCycles',500, ...
    'Learners',t);
