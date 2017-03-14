#!/usr/bin/env python

"""
@file: This file includes all interactions with hyperopt.
"""

from hyperopt import hp, fmin, tpe
from hyperopt.mongoexp import MongoTrials
import multiprocessing as mp
from subprocess import Popen
import json

from mcstas_utils import getExperiment, now, getLimits, compile_mcstas
from simulation_analysis_utils import objective, getWorkingDir, getResultsFile

# Declare some helpful variables.
workerDb = 'localhost:1234/exp_db'
masterDb = 'mongo://{}/jobs'.format(workerDb)

# Array to hold open processes
workers = []

# Converts a simple dict to a hyperopt search space
def getSearchSpace(parameterLimits):
    choice_space = []

    for key in parameterLimits.keys():
        choice_space.append(hp.uniform(key, parameterLimits[key][0], parameterLimits[key][1]))
    
    return choice_space

# Run the optimization using hyperopt.
def runOptimizations(evals):
    limitsDict = getLimits()
    exp_label = '{}_{}'.format(getExperiment(), now())
    
    # Allow parallelizing 
    trials = MongoTrials(masterDb, exp_key=exp_label)
    
    # Use hyperopt to optimize function
    best = fmin(objective, getSearchSpace(limitsDict), trials=trials, algo=tpe.suggest, max_evals=evals)
    
    # Write results to a file
    with open(getResultsFile(), "a") as myfile:
        myfile.write('{}\n'.format(json.dumps(best)))

    return best

# Open a worker for each idle CPU.
def startWorkers():
    workerBoot = [
        #'PYTHONPATH=$PYTHONPATH:{}/'.format(getWorkingDir()), 
        'hyperopt-mongo-worker', 
        '--mongo={}'.format(workerDb), 
        '--poll-interval=1'
    ]

    for i in range(mp.cpu_count()):
        workers.append(Popen(workerBoot, shell = False, stdin = None, stdout = None, stderr = None, close_fds = True, cwd=getWorkingDir()))

if __name__ == "__main__":
    # Compile the experiment first, this ensures it's always up to date
    compile_mcstas(getExperiment())
    
    # Start a worker for each core on the system
    startWorkers()
    
    # Run the actual optimization.
    best = runOptimizations(1000)

    # The optimization is done, kill the workers
    for worker in workers:
        worker.terminate()
    
