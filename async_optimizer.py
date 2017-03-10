import sys
import os

sys.path.append(os.path.abspath('/home/jph/Foersteaarsprojekt'))

from hyperopt import hp, fmin, tpe
from hyperopt.mongoexp import MongoTrials
    
from parse_brill import getSearchSpace, getExperiment, now, objective

exp_label = '{}_{}'.format(getExperiment(), now())
limitsDict = {
    'guide_mid_width': [0, 0.1],
    'guide_mid_height': [0, 0.1],
    'guide_linxw': [0, 80],
    'guide_loutxw': [0, 80],
    'guide_linyh': [0, 80],
    'guide_loutyh': [0, 80]
}

trials = MongoTrials('mongo://localhost:1234/exp_db/jobs', exp_key=exp_label)
best = fmin(objective, getSearchSpace(limitsDict), trials=trials, algo=tpe.suggest, max_evals=100)
with open("best.txt", "a") as myfile:
    myfile.write(str(best))
