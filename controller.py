#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 09:50:16 2018

@author: qingtao
"""

import pandas as pd
import parse as parsed
import os

directory = '/Users/qingtao/OneDrive - National University of Singapore/MTech/01 KE5207/computational intelligence ii/Lecture Notes/Day 3 (Sam GU Zhan)/GA-Fuzzy CA - Algorithmic Trading System/'
data = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS.xlsx'))
data.columns = data.columns.str.strip()
parsed = parsed.parse_futures_data(data, ['Open','High','Low','Close','Volume'])

parsed['flag'] = parsed['Date'].diff()
parsed.loc[parsed.Date != parsed.Date.shift(-1), 'flag'] = 2 # 2=closing time
parsed.loc[parsed['flag']>2,'flag']=1 # 1=opening time

print('--------------')
print(len(parsed))
groupSize = int(len(parsed)/69)
subGroupSize = int(groupSize/4)
print(groupSize)
print(subGroupSize)
print('--------------')

x=0
y1=0
y2=0
y3=0
y4=0

for i in range (0, 69):
    x += groupSize
    print('Group'+ str(i+1) + ' Size: ' + str(x))
    for j in range (0,4):
        y1 += subGroupSize
        y0 = y1 + subGroupSize
        y2 = y0 + subGroupSize
        y3 = y2
        y4 = y3 + subGroupSize
        print('Sub Group Index 1: '+ str(y1))
        print('Sub Group Index 2: '+ str(y2))
        print('Sub Group Index 3: '+ str(y3))
        print('Sub Group Index 4: '+ str(y4))
        break
    
    y1=y4
    # call fitness function
#    FF = FitnessFunction()
        
import datetime
now = datetime.datetime.now()
out_path = directory
writer = pd.ExcelWriter(os.path.join(directory,'data/FCPO_6_years_NUS '+ now.strftime("%Y-%m-%d %H-%M-%S")+'.xlsx'))
parsed.to_excel(writer)
writer.save()    