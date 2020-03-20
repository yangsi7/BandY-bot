 function [tmw] = runStackedModel(tmw,ms,varargin)
   B.PredTimeIndex = timerange(datetime('01-Jul-2018','Locale','en_US'),datetime('31-Dec-2018','Locale','en_US'),'closed');
   B=parse_pv_pairs(B,varargin);

 [tmw1] = NormalizePrice(tmw,'windowsize',ms.varParams.normWinSize1);
 [varnames1,tmw1,varnamesBad]=CalcIndicators2(tmw1,'ParamStruct',ms.A);
 [varnames1, tmw1] = GetIndsDtDdt(tmw1,varnames1);
 [tmwpred1]=PredBuyIdx(tmw1,ms.Mdlr1,'varnames',ms.varNames.varSelect1,'method',...
   'fitrensemble','TimeIndex',B.PredTimeIndex);
 sigProcVar={'yhat_fre'};
 for i = 1: length(ms.varParams.wins)
    tmpSig = indicators(tmwpred1.yhat_fre,'ema',ms.varParams.wins(i));
    tmwpred1 = addvars(tmwpred1,tmpSig,'NewVariableNames',['yhat_freW',num2str(ms.varParams.wins(i))]);
    sigProcVar=[sigProcVar,['yhat_freW',num2str(ms.varParams.wins(i))]];
 end

 sig1=tmwpred1.yhat_fre;

 [tmw2] = NormalizePrice(tmw,'windowsize',ms.varParams.normWinSize2);
 [varnames2,tmw2,varnamesBad]=CalcIndicators2(tmw2,'ParamStruct',ms.A);
 [varnames2, tmw2] = GetIndsDtDdt(tmw2,varnames2);
 [tmwpred2]=PredBuyIdx(tmw2,ms.Mdlr2,'varnames',ms.varNames.varSelect2,'method',...
   'fitrensemble','TimeIndex',B.PredTimeIndex);
 sigProcVar={'yhat_fre'};
 for i = 1: length(ms.varParams.wins)
    tmpSig = indicators(tmwpred2.yhat_fre,'ema',ms.varParams.wins(i));
    tmwpred2 = addvars(tmwpred2,tmpSig,'NewVariableNames',['yhat_freW',num2str(ms.varParams.wins(i))]);
    sigProcVar=[sigProcVar,['yhat_freW',num2str(ms.varParams.wins(i))]];
 end

  sig2=tmwpred2.yhat_fre;

 XX=[table2array(tmwpred1(:,[ms.varNames.varSelect1(1:ms.varParams.netVarSelect),...
      ms.varNames.sigProcVar])),table2array(tmwpred2(:,[ms.varNames.varSelect2(1:ms.varParams.netVarSelect)...
      ,ms.varNames.sigProcVar]))]';

 xx=XX(:,ms.varParams.wins(end):end);

 signal=ms.net(xx);
 signal=[nan(1,ms.varParams.wins(end)-1),signal]';
 dd_T3w48 = tmwpred1.dd_t3W48VF2;
 dd_T3w96 = tmwpred1.dd_t3W96VF2;

 tmw = addvars(tmw,signal,sig1,sig2,dd_T3w48,dd_T3w96);
