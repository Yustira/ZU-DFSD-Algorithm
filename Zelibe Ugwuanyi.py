#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from time import sleep

def check_ds(data):
    demand = data.loc['Demand'].sum()
    supply = data['Supply'].sum()
    if demand == supply: 
        print('Total demand equal to total supply: {:d}'.format(int(demand)))
        pass
    elif demand > supply:
        print('Total demand more than total supply: {:d} > {:d}'.format(int(demand), int(supply)))
        data_T = data.T
        dm = data_T.pop('Demand')
        data_T['S0'] = np.zeros(len(dm))
        data_T['Demand'] = dm
        data = data_T.T
        data.loc['S0', 'Supply'] = demand - supply
    elif demand < supply:
        print('Total demand less than total supply: {:d} < {:d}'.format(int(demand), int(supply)))
        Supply = data.pop('Supply').reset_index()
        data['D0'] = np.zeros(len(data.index))
        data['Supply'] = Supply.Supply.to_numpy()
        data.loc['Demand', 'D0'] = data['Supply'].sum() - data.loc['Demand'].sum()
    else:
        print('Error in checking total demand and supply')
    return data

def penalty(data):
    data['Penalty'] = np.zeros(data.shape[0])
    data.loc['Penalty'] = np.zeros(data.shape[1])
    
    row = data.index[:-2].to_numpy()
    n_row = len(row)
    
    col = data.columns.to_numpy()[:-2]
    n_col = len(col)
    
    # penalty rows
    for Si in row: 
        if n_col == 1: 
            data.loc[Si, 'Penalty'] = data.loc[Si][:-2][0]
        else: 
            Si_min = data.loc[Si][:-2].min()
            if n_row <= 2: 
                data.loc[Si, 'Penalty'] = (data.loc[Si][:-2]-Si_min).sum()
            else:
                data.loc[Si, 'Penalty'] = (data.loc[Si][:-2]-Si_min).sum()+n_row
        if n_col == 2 and n_row == 2:
            data.loc[Si, 'Penalty'] = data.loc[Si][:-2].max()
        else:
            pass
        
    # penalty columns
    for Di in col:
        if n_row == 1:
            data[Di].loc['Penalty'] = data[Di][:-2][0]
        else:
            Di_min = data[Di][:-2].min()
            if n_row <= 2:
                data[Di].loc['Penalty'] = (data[Di][:-2]-Di_min).sum() 
            else:
                data[Di].loc['Penalty'] = (data[Di][:-2]-Di_min).sum()+n_col   
        if n_row == 2 and n_col == 2:
            data[Di].loc['Penalty'] = data[Di][:-2].max()
        else:
            pass
            
    return data


def RnC(data):
    # check the similar values in penalty rows
    sim_r = data['Penalty'][:-2][data['Penalty'][:-2].duplicated(keep=False)].unique()
    max_r = data['Penalty'][:-2].max()
    if len(sim_r) > 0:
        if sim_r[0] == max_r:
            pen_r = sim_r[0]
        else:
            pen_r = max_r
    else:
        pen_r = max_r
    
    # check the similar penalty values in a column
    sim_c = data.loc['Penalty'][:-2][data.loc['Penalty'][:-2].duplicated(keep=False)].unique()
    max_c = data.loc['Penalty'][:-2].max()
    if len(sim_c) > 0:
        if sim_c[0] == max_c:
            pen_c = sim_c[0]
        else:
            pen_c = max_c
    else: 
        pen_c = max_c
        
    # Determine the index S and D
    if pen_r > pen_c:
        m = data[data['Penalty'] == pen_r]
        Si = m.index[0]
        Di = m.loc[Si][:-2][m.loc[Si][:-2] == m.loc[Si][:-2].min()].index[0]
    else:
        if len(sim_c) > 0:
            if sim_c[0] == max_c:
                Di = data.loc['Demand'][:-2][data.loc['Demand'][:-2] == data.loc['Demand'][:-2].max()].index[0]
                Si = data[Di][:-2][data[Di][:-2] == data[Di][:-2].min()].index[0]
            else:
                Di = data.loc['Penalty'][data.loc['Penalty'] == pen_c].index[0]
                Si = data[Di][data[Di] == data[Di].min()].index[0]
        else:
            Di = data.loc['Penalty'][data.loc['Penalty'] == pen_c].index[0]
            Si = data[Di][data[Di] == data[Di].min()].index[0]
            
    print('Alocation to {:s} and {:s}'.format(Si, Di))
    return Si, Di

def alocation(data, loc_s, loc_d):
    supply = data.loc[loc_s, 'Supply']
    demand = data[loc_d]['Demand']
    if demand > supply:
        value = supply * data.loc[loc_s, loc_d]
        cost.append(value)
        data.loc['Demand', loc_d] = data.loc['Demand', loc_d] - supply
        data = data.drop(loc_s, axis=0)
        print('Cost: {:0.1f}'.format(value))
    else:
        value = demand * data.loc[loc_s, loc_d]
        cost.append(value)
        data.loc[loc_s, 'Supply'] = data.loc[loc_s, 'Supply'] - demand
        data = data.drop(loc_d, axis=1)
        print('Cost: {:0.1f}'.format(value))
        
    return data

#Data/balanced_data.xlsx
path = str(input('Enter Data path: '))
df = pd.read_excel(path)
df.set_index('Index', inplace=True)
sleep(2)
print('\n',df)

cost = []
data = check_ds(df)
i=0

sleep(2)
while True:
    print('\nIteration {:d}'.format(i+1))
    data = penalty(data)
    if len(data.index[:-2]) == 1 and len(data.columns[:-2]) == 1:
        if data.loc['Demand'][:-2][0] == data['Supply'][:-2][0]:
            loc_d = data.columns[:-2][0]
            loc_s = data.index[:-2][0]
            value = data.loc['Demand'][:-2][0]*data.loc[loc_s, loc_d]
            cost.append(value)
            print('Alocation to {:s} and {:s}'.format(loc_s, loc_d))
            print('Cost: ', value)
            break
        else:
            print('Error, demand not equal to supply')
    else:
        pass
    loc_s, loc_d = RnC(data)
    data = alocation(data, loc_s, loc_d)
    i+=1
    sleep(1)

cost = np.array(cost)
total_cost = cost.sum()
sleep(2)
print('\nTotal cost: ', total_cost)


