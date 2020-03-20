function [long, short] = strategy(tmw,varargin)

A.strategy = 'Andy';
a.adx.th = 17;
A.rsi.obos = 52;
A=parse_pv_pairs(A,varargin);

% Initialize signals

% Strat (1) 'yhat_fre'
if strcmp(A.strategy,'Andy')
   long = false(size(tmw.Close));
   blong.jma = false(size(tmw.Close));
   blong.rf = false(size(tmw.Close));
   blong.adx = false(size(tmw.Close));
   blong.sar = false(size(tmw.Close));
   blong.rsi = false(size(tmw.Close));
   blong.macd = false(size(tmw.Close));
   blong.vol = false(size(tmw.Close));

   short = false(size(tmw.Close));
   bshort.jma = false(size(tmw.Close));
   bshort.rf = false(size(tmw.Close));
   bshort.adx = false(size(tmw.Close));
   bshort.sar = false(size(tmw.Close));
   bshort.rsi = false(size(tmw.Close));
   bshort.macd = false(size(tmw.Close));
   bshort.vol = false(size(tmw.Close));

   blong.jma(tmw.djma > 0) = true;
   blong.rf(tmw.High>tmw.rf_hb & tmw.rf_uwrd > 0) = true;
   blong.adx(tmw.adx_dip > tmw.adx_dim & tmw.adx > a.adx.th) = true;
   blong.sar(tmw.sar < tmw.Close) = true;
   blong.rsi(tmw.rsi_v > A.rsi.obos) = true;
   blong.macd(tmw.macdH > 0) = true;
   blong.vol(tmw.Volume > tmw.svol) = true;

   bshort.jma(tmw.djma < 0) = true;
   bshort.rf(tmw.Low<tmw.rf_lb & tmw.rf_dwrd > 0) = true;
   bshort.adx(tmw.adx_dip < tmw.adx_dim & tmw.adx > a.adx.th) = true;
   bshort.sar(tmw.sar > tmw.Close) = true;
   bshort.rsi(tmw.rsi_v < A.rsi.obos) = true;
   bshort.macd(tmw.macdH < 0) = true;
   bshort.vol(tmw.Volume > tmw.svol) = true;

   long(blong.jma & blong.rf & blong.adx & blong.sar ...
      & blong.rsi & blong.macd & blong.vol) = true;
   short(bshort.jma & bshort.rf & bshort.adx & bshort.sar ...
      & bshort.rsi & bshort.macd & bshort.vol) = true;
end


