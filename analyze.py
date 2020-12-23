import pandas as pd
import numpy as np
from os.path import expanduser
import warnings
warnings.filterwarnings("ignore")
import os

temp = {
    'system' :[],
    'cpu': [],
    'steps': []
}
home = expanduser("~")
df = pd.read_csv('./model-results-2x-not-that-late-1x-33p.csv')

for system_id in range(300):
    system_id += 1
    system_id = str(system_id)
    
    core_count = df[df.approach == 'BNV2-4.0'][df.system == 'system_' + system_id].max_total_core.values[0] * 2
    n_iter = df[df.approach == 'BNV2-4.0'][df.system == 'system_' + system_id].steps.values[0]
    
    if not os.path.exists('./results/'+system_id+'.txt'): continue
    
    with open('./results/'+system_id+'.txt') as f:
        lines = f.read().split('\n')
        lines = [line for line in lines if len(line.strip()) > 0]
        lines = [line for line in lines if 'info' not in line]
    
    initial_samples = 5
    if n_iter + initial_samples > len(lines):
        continue
    temp['system'].append('system_' + system_id)
#     print(system_id)
    cpu = 1e10
    step = 1e10
    for iter_id, line in enumerate(lines):
        meets = line.split(' ')[1] == 'True'
        total = np.round(float(line.split(' ')[2]),2)
#         print(meets, total)
        if meets == False: 
            continue
        
        if cpu > total:
#             print('updated', cpu, step)
            cpu = total
            step = iter_id + 1
#     print()
    temp['cpu'].append(cpu)
    temp['steps'].append(step)
df_mobo = pd.DataFrame(temp)
# df_mobo

print('mobo didnt find anything valid in ', df_mobo[df_mobo.cpu > 1e9].shape[0], 'out of', df_mobo.shape[0])

df_mobo = df_mobo[df_mobo.cpu < 1e9]
df_bnv2_4 = df[df.approach == 'BNV2-4.0']

mobo_is_cheaper = []
diffs = []
systems = df_mobo.system.values
for system in systems:
    mobo_cpu = df_mobo[df_mobo.system == system].cpu.values[0]
    bnv2_4_cpu = df_bnv2_4[df_bnv2_4.system == system].max_total_core.values[0]
    if mobo_cpu < bnv2_4_cpu:
        mobo_is_cheaper.append(system)
    diffs.append((mobo_cpu - bnv2_4_cpu) / (bnv2_4_cpu))
    
print(len(mobo_is_cheaper),'caces mobo is better', '( total is ', len(systems),')', 'for rest didnt find anything')
print('on average MOBO uses',str(int(np.round(np.mean(diffs) * 100))) + '%','more than BNV2-4.0 CPU shares to meet the SLAs')

df_bnv1_4 = df[df.approach == 'BNV1-4.0']
mobo_is_cheaper = []
diffs = []
systems = df_mobo.system.values
for system in systems:
    mobo_cpu = df_mobo[df_mobo.system == system].cpu.values[0]
    bnv1_4_cpu = df_bnv1_4[df_bnv1_4.system == system].max_total_core.values[0]
    if mobo_cpu < bnv1_4_cpu:
        mobo_is_cheaper.append(system)
    diffs.append((mobo_cpu - bnv1_4_cpu) / (bnv1_4_cpu))

print(len(mobo_is_cheaper),'caces mobo is better', '( total is ', len(systems),')', 'for rest didnt find anything')
print('on average MOBO uses',str(int(np.round(np.mean(diffs) * 100))) + '%','more than BNV1-4.0 CPU shares to meet the SLAs')

df_bnv1_4 = df[df.approach == 'BNV1-2.0']
mobo_is_cheaper = []
diffs = []
systems = df_mobo.system.values
for system in systems:
    mobo_cpu = df_mobo[df_mobo.system == system].cpu.values[0]
    bnv1_4_cpu = df_bnv1_4[df_bnv1_4.system == system].max_total_core.values[0]
    if mobo_cpu < bnv1_4_cpu:
        mobo_is_cheaper.append(system)
    diffs.append((mobo_cpu - bnv1_4_cpu) / (bnv1_4_cpu))

print(len(mobo_is_cheaper),'caces mobo is better', '( total is ', len(systems),')', 'for rest didnt find anything')
print('on average MOBO uses',str(int(np.round(np.mean(diffs) * 100))) + '%','more than BNV1-2.0 CPU shares to meet the SLAs')
