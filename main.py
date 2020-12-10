import numpy as np
import time
from tqdm import tqdm
import json
import os
import sys
import tempfile

# https://github.com/ppgaluzio/MOBOpt
# @article{GALUZIO2020100520,
# title = "MOBOpt — multi-objective Bayesian optimization",
# journal = "SoftwareX",
# volume = "12",
# pages = "100520",
# year = "2020",
# issn = "2352-7110",
# doi = "https://doi.org/10.1016/j.softx.2020.100520",
# url = "http://www.sciencedirect.com/science/article/pii/S2352711020300911",
# author = "Paulo Paneque Galuzio and Emerson Hochsteiner [de Vasconcelos Segundo] and Leandro dos Santos Coelho and Viviana Cocco Mariani"
# }
import json
import mobopt as mo
import numpy as np
import sys

import pandas as pd

import warnings
warnings.filterwarnings("ignore")

def load(path):
    with open(path) as f:
        return json.load(f)

system_id = int(sys.argv[1])
for _ in range(1):
    
    system_name = str(system_id)

    df = pd.read_csv('model-results-2x-not-that-late-1x-33p.csv')

    core_count = df[df.approach == 'BNV2-4.0'][df.system == 'system_' + system_name].max_total_core.values[0] * 2
    n_iter = df[df.approach == 'BNV2-4.0'][df.system == 'system_' + system_name].steps.values[0] 

    with open('results/'+str(system_id)+'.txt','a') as f:
        f.write('info ' + system_name + ' ' + str(n_iter) + '\n')
    f.close()

    # df[df.approach == 'BNV1-4.0'][df.system == 'system_' + system_name].max_total_core.values[0] * 2

    data = load('./systems/' + system_name + '.json')
    demands = data['demands']
    classes = data['classes']
    C = len(classes)
    resources = data['resources']
    K = len(resources)
    SLA = data['SLA']
    class_probs = data['class_probs']
    throughput = data['throughput']

    utilizations = {}
    responseTimes = {}

    for c in classes:
        res = ''
        for k in resources:
            f = '($N/(1 - ($D)))'
            flag = False
            if c+"_"+k in demands:
                flag =True
                f = f.replace('$N', '(' + str(demands[c+'_'+k]) + '/' + 'alphas["' + k + '"]' + ')')
                p = ''
                for c2 in classes:
                    if c2+'_'+k in demands:
                        p += '(('+str(class_probs[c2])+"*"+str(throughput) + "*" + str(demands[c2+'_'+k])+')/alphas["'+ k + '"]'+')'
                        p += '+'
                utilizations[k] = p[:-1]
                p = p[:-1]
                f = f.replace('$D',p)
            if flag:
                res += f + "+"
        res = res[:-1]
        responseTimes[c] = res


    python_code = """
def mean_response_timesF(alphas):
    A
    return B
def utilizationsF(alphas):
    return C
    """

    rts = ''
    ret = ''
    for key in range(C):
        key = str(key)
        value = responseTimes[key]
        rts += 'r' + key + ' = ' + value + '\n    '
        ret += 'r' + key + ' * 1000, '
    ret = ret[:-2]
    python_code = python_code.replace('A', rts)
    python_code = python_code.replace('B', ret)

    ut = ''
    for key in range(K):
        key = str(key)
        value = utilizations[key]
        ut += value + ', '
    ut = ut[:-2]
    python_code = python_code.replace('C', ut)

    exec(python_code, globals())

    cache = {}

    services_count = K
    request_count = C

    import time
    def objective(x):
        s = sum(x)
        allocations = [0] * services_count
        for i in range(services_count):
            allocations[i] = core_count * (x[i] / s)
            if allocations[i] < 1:
                allocations[i] = 1
        not_used = core_count - sum(allocations)
        
        config = {}
        for i in range(len(allocations)):
            config[str(i)] = allocations[i]

        SLA_target = SLA
        respones_times = [0] * request_count
        res = []
        
        feedbacks = mean_response_timesF(config)
        
        meets = True
        
        for i in range(request_count):
            if feedbacks[i] > SLA_target:
                respones_times[i] = feedbacks[i] - SLA_target
                meets = False
            res.append(respones_times[i])
        res.append(not_used)
        cache[key] = np.array(res)
        with open('results/'+str(system_id)+'.txt','a') as f:
            f.write('system_' + system_name + ' ' + str(meets) + ' ' +  str(sum(allocations)) + '\n')
        f.close()

        return np.array(np.array(res))

    st = 1 / core_count
    temp = [[st + 0.01, 0.94]] * (services_count+1)
    PB = np.asarray(temp)
    NParam = PB.shape[0]

    Optimizer = mo.MOBayesianOpt(target=objective,
                                NObj=request_count+1,
                                pbounds=PB,
                                verbose=False,
                                max_or_min='min', # whether the optimization problem is a maximization problem ('max'), or a minimization one ('min')
                                RandomSeed=10)

    Optimizer.initialize(init_points=5) 
    front, pop = Optimizer.maximize(n_iter=int(n_iter),
                                    prob=0.1,
                                    ReduceProb=False,
                                    q=0.5)
