# Created by:
# Iyas Yustira
# Dena Suprianto

import pandas as pd
import numpy as np

def is_balanced(data):
    sum_a = data['Supply'].sum()
    sum_b = data.loc['Demand'].sum()
    if sum_a == sum_b: 
        print('Supply = Demand : {:d}'.format(sum_a))
        pass
    elif sum_a < sum_b:
        print('Supply < Demand : {:d} < {:d}'.format(sum_a, sum_b))
        data_T = data.T
        dm = data_T.pop('Demand')
        data_T['Dum'] = np.zeros(len(dm)).astype(int)
        data_T['Demand'] = dm
        data = data_T.T
        data.loc['Dum', 'Supply'] = sum_b - sum_a
    else:
        print('Supply > Demand : {:d} > {:d}'.format(sum_a, sum_b))
        Supply = data.pop('Supply').reset_index()
        data['Dum'] = np.zeros(len(data.index)).astype(int)
        data['Supply'] = Supply.Supply.to_numpy()
        data.loc['Demand', 'Dum'] = sum_a - sum_b
    return data

def penalty(data):
    data['Penalty'] = np.zeros(data.shape[0]).astype(int)
    data.loc['Penalty'] = np.zeros(data.shape[1]).astype(int)
    
    m = data.index[:-2]    
    n = data.columns[:-2]
      
    # Row penalty
    if len(n) == 1 and len(m) <= 2:
        for i in m:
            data.loc[i, 'Penalty'] = data.loc[i][:-2].max()
    elif len(n) == 1 and len(m) > 2:
        for i in m:
            data.loc[i, 'Penalty'] = data.loc[i][:-2].max() + len(m)
    elif len(n) == 2 and len(m) <= 2:
        for i in m:
            xj_min = data.loc[i][:-2].min()
            data.loc[i, 'Penalty'] = (data.loc[i][:-2] - xj_min).sum()  
    else:
        for i in m:
            xj_min = data.loc[i][:-2].min()
            data.loc[i, 'Penalty'] = (data.loc[i][:-2] - xj_min).sum() + len(m)
    
    # Column penalty
    if len(m) == 1 and len(n) <= 2:
        for j in n:
            data.loc['Penalty', j] = data[j][:-2].max()
    elif len(m) == 1 and len(n) > 2:
        for j in n:
            data.loc['Penalty', j] = data[j][:-2].max() + len(n)
    elif len(m) == 2 and len(n) <= 2:
        for j in n:
            xi_min = data[j][:-2].min()
            data.loc['Penalty', j] = (data[j][:-2] - xi_min).sum()
    else:
        for j in n:
            xi_min = data[j][:-2].min()
            data.loc['Penalty', j] = (data[j][:-2] - xi_min).sum() + len(n)
        
    return data

def cell_allocation(data):
    rp_max = data['Penalty'][:-2].max()
    cp_max = data.loc['Penalty'][:-2].max()
    
    m = data['Penalty'][:-2][data['Penalty'][:-2] == rp_max].index
    n = data.loc['Penalty'][:-2][data.loc['Penalty'][:-2] == cp_max].index
    
    glc_r = {}
    glc_c = {}
    
    if rp_max == cp_max: 
        for i in m:
            glc_r[data.loc[i][:-2].min()] = i
        for j in n:
            glc_c[data[j][:-2].min()] = j   
        if max(glc_r) > max(glc_c):
            Ri = glc_r[max(glc_r)]
            Cj = data.loc[Ri][:-2][data.loc[Ri][:-2] == max(glc_r)].index[0]
        else:
            Cj = glc_c[max(glc_c)]
            Ri = data[Cj][:-2][data[Cj][:-2] == max(glc_c)].index[0]
    elif rp_max > cp_max:
        for i in m:
            glc_r[data.loc[i][:-2].min()] = i
        Ri = glc_r[max(glc_r)]
        Cj = data.loc[Ri][:-2][data.loc[Ri][:-2] == max(glc_r)].index[0]
    else:
        for j in n:
            glc_c[data[j][:-2].min()] = j
        Cj = glc_c[max(glc_c)]
        Ri = data[Cj][:-2][data[Cj][:-2] == max(glc_c)].index[0]       
    print('Alocation to {:s} and {:s}'.format(Ri, Cj))
    return Ri, Cj

def cost_allocation(data, Ri, Cj):
    ai = data.loc[Ri, 'Supply']
    bi = data.loc['Demand', Cj]
    if ai > bi:
        cost_val = (data.loc['Demand', Cj] * data.loc[Ri, Cj]).astype(int)
        cost.append(cost_val)
        data.loc[Ri, 'Supply'] = data.loc[Ri, 'Supply'] - data.loc['Demand', Cj]
        data.drop(Cj, axis=1, inplace=True)
    else:
        cost_val = (data.loc[Ri, 'Supply'] * data.loc[Ri, Cj]).astype(int)
        cost.append(cost_val)
        data.loc['Demand', Cj] = data.loc['Demand', Cj] - data.loc[Ri, 'Supply']
        data.drop(Ri, axis=0, inplace=True)
    print('Cost: {:d}'.format(cost_val))
    return data

print()
fn = str(input('Enter file name: '))
data = pd.read_excel("data/"+fn+".xlsx")
data.set_index('Index', inplace=True)
print('\n', data, '\n')
data = is_balanced(data)
print()
cost = []
i = 0
while True:
    i += 1
    m, n = data.index[:-2], data.columns[:-2]
    print("-"*15)
    print(' Iteration', i,)
    print("-"*15, '\n')
    if len(m) == 1 and len(n) == 1:
        if data['Supply'][:-2][0] == data.loc['Demand'][:-2][0]:
            penalty(data)
            print(data, '\n')
            cost_val = (data.loc['Demand'][:-2][0] * data.loc[m[0]][:-2][0]).astype(int)
            cost.append(cost_val)
            print('Alocation to {:s} and {:s}'.format(m[0], n[0]))
            print('Cost: {:d}'.format(cost_val))
        else:
            print('Error, demand not equal with supply')
        break
    else:    
        penalty(data)
        print(data, '\n')
        Ri, Cj = cell_allocation(data)
        cost_allocation(data, Ri, Cj)
    print()
print()
print("-"*23)
print('  Total cost:', sum(cost))
print("-"*23)

