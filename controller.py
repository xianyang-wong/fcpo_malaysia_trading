#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 09:50:16 2018

@author: qingtao
"""

import pandas as pd
import parse as parsed
import os


directory = '/Users/qingtao/OneDrive - National University of Singapore/MTech/01 KE5207/computational intelligence ii/CA/fcpo_malaysia_trading/'
parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_Parsed.xlsx'))

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
        yTmp = y1 + subGroupSize
        y2 = yTmp + subGroupSize
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

