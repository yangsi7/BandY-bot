function [long, short] = strategy(tmw,varargin)

A.strat = 'Andy';
A.adxth = 15;
A.adx_jma = 1;
A.rsiobos = 58.7;

A=parse_pv_pairs(A,varargin);

if strcmp(A.strat,'Andy')
   A.usejma=1;
   A.userf=1;
   A.usepsar=1;
   A.useadx=1;
   A.usersi=1;
   A.usemacd=1;
   A.usevolume=1;
elseif strcmp(A.strat,'Andy2')
   A.usejma=1;
   A.userf=1;
   A.usepsar=0;
   A.useadx=1;
   A.usersi=1;
   A.usemacd=1;
   A.usevolume=1;
end
% Initialize signals

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
   if A.adx_jma
      blong.adx(tmw.adx_jma_dip > tmw.adx_jma_dim & tmw.adx_jma > A.adxth) = true;
   else
      blong.adx(tmw.adx_dip > tmw.adx_dim & tmw.adx > A.adxth) = true;
   end
   blong.sar(tmw.sar < tmw.Close) = true;
   blong.rsi(tmw.rsi_v > A.rsiobos) = true;
   blong.macd(tmw.macdH > 0) = true;
   blong.vol(tmw.Volume > tmw.svol) = true;

   bshort.jma(tmw.djma < 0) = true;
   bshort.rf(tmw.Low<tmw.rf_lb & tmw.rf_dwrd > 0) = true;
   if A.adx_jma
      bshort.adx(tmw.adx_jma_dip < tmw.adx_jma_dim & tmw.adx_jma > A.adxth) = true;
   else
      bshort.adx(tmw.adx_jma_dip < tmw.adx_jma_dim & tmw.adx_jma > A.adxth) = true;
   end
   bshort.sar(tmw.sar > tmw.Close) = true;
   bshort.rsi(tmw.rsi_v < A.rsiobos) = true;
   bshort.macd(tmw.macdH < 0) = true;
   bshort.vol(tmw.Volume > tmw.svol) = true;

   if !A.userf; blong.rf = 1; bshort.rf=1;end
   if !A.usepsar; blong.sar = 1; bshort.sar=1;end
   if !A.useadx; blong.adx = 1; bshort.adx=1;end
   if !A.usersi; blong.rsi = 1; bshort.rsi=1;end
   if !A.usemacd; blong.macd = 1; bshort.macd=1;end
   if !A.usevolume; blong.vol = 1; bshort.vol=1;end
      

   long(blong.jma & blong.rf & blong.adx & blong.sar ...
      & blong.rsi & blong.macd & blong.vol) = true;
   short(bshort.jma & bshort.rf & bshort.adx & bshort.sar ...
      & bshort.rsi & bshort.macd & bshort.vol) = true;


