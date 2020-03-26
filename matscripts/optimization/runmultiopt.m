for i = 1 : 100
   [BayesObject{i}] = optSetUp('onlysim',0);
save('/home/euphotic_/yangino-bot/matscripts/optimization/optimout.mat','BayesObject');
end
