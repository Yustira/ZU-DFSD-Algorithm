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
    
    # row penalty
    for i in m:
        if len(n) == 1:
            data.loc[i, 'Penalty'] = data.loc[i][:-2][0]
        else:
            data.loc[i, 'Penalty'] = np.round(data.loc[i][:-2].to_numpy().std(), 2)
    
    # column penalty
    for j in n:
        if len(m) == 1:
            data.loc['Penalty', j] = data[j][:-2][0]
        else:
            data.loc['Penalty', j] = np.round(data[j][:-2].to_numpy().std(), 2)
    
    return data

def cell_allocation(data):
    pr_max = data['Penalty'][:-2].max()
    pc_max = data.loc['Penalty'][:-2].max()
    
    m = data[data['Penalty'] == pr_max].index
    n = data.loc['Penalty'][data.loc['Penalty'] == pc_max].index
    
    glc = {}
    if pr_max == pc_max:
        for i in m:
            glc[data.loc[i][:-2].min()] = i
        for j in n:
            glc[data[j][:-2].min()] = j
        rc = glc[max(glc)]
        if rc in m:
            ri = rc
            cj = data.loc[ri][:-2][data.loc[ri][:-2] == max(glc)].index[0]
        else:
            cj = rc
            ri = data[cj][:-2][data[cj][:-2] == max(glc)].index[0]
    elif pr_max > pc_max:
        for i in m:
            glc[data.loc[i][:-2].min()] = i
        ri = glc[max(glc)]
        cj = data.loc[ri][:-2][data.loc[ri][:-2] == max(glc)].index[0]
    else:
        for j in n:
            glc[data[j][:-2].min()] = j
        cj = glc[max(glc)]
        ri = data[cj][:-2][data[cj][:-2] == max(glc)].index[0]
        
    print('Allocation to {:s} and {:s}'.format(ri, cj))
    return ri, cj

def cost_allocation(ri, cj, data):
    ai = data.loc[ri, 'Supply']
    bi = data.loc['Demand', cj]
    
    if ai > bi:
        val = (bi * data.loc[ri, cj]).astype(int)
        cost.append(val)
        data.loc[ri, 'Supply'] = ai - bi
        data.drop(cj, axis=1, inplace=True)
    else:
        val = (ai * data.loc[ri, cj]).astype(int)
        cost.append(val)
        data.loc['Demand', cj] = bi - ai
        data.drop(ri, axis=0, inplace=True)
    print('Cost: {:d}'.format(val))
    return data

print()
d = str(input('Enter file name: '))
data = pd.read_excel("data/"+d+".xlsx")
data.set_index('Index', inplace=True)
print()
print(data, '\n')
data = is_balanced(data)
print()
cost = []
i = 0
while True:
    i += 1
    print('-'*15)
    print(' Iteration: {:d}'.format(i))
    print('-'*15, '\n')
    data = penalty(data)
    print(data, '\n')
    m = data.index[:-2]
    n = data.columns[:-2]
    if len(m) == 1 and len(n) == 1:
        ri = m[0]
        cj = n[0]
        ai = data.loc[ri, 'Supply']
        val = (ai * data.loc[ri, cj]).astype(int)
        cost.append(val)
        print('Allocation to {:s} and {:s}'.format(ri, cj))
        print('Cost: {:d}'.format(val))
        break
    else:
        ri, cj = cell_allocation(data)
        data = cost_allocation(ri, cj, data)
    print()
print()
print("-"*23)
print('  Total Cost: {:d}'.format(sum(cost)))
print('-'*23, '\n')