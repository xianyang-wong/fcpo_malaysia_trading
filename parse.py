# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 10:01:12 2018

@author: XY
"""
import pandas as pd
import matplotlib.pyplot as plt
import os

directory = ''
data = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS.xlsx'))
data.columns = data.columns.str.strip()

def parse_futures_data(data, var2parse):
   
    for i in range(0,len(var2parse)):
        var = var2parse[i]
        temp = data[['General','Date','Time',var]].copy()
        
        temp = pd.pivot_table(temp,
                              index=['Date','Time'],
                              columns='General').reset_index()
        col_name1 = temp.columns.droplevel(1)
        col_name2 = temp.columns.droplevel(0)
        col_name = col_name1[0:2].append(col_name2[2:])
        temp.columns = col_name
        temp[var] = temp[col_name2[2:]].mean(axis=1)
        temp = temp[['Date','Time',var]]
        
        if i==0:
            parsed = temp.copy()
        else:
            parsed = parsed.merge(temp,
                                  how='left',
                                  left_on=['Date','Time'],
                                  right_on=['Date','Time'])
            
    return parsed

parsed = parse_futures_data(data, ['Open','High','Low','Close','Volume'])

parsed.describe()

plots = parsed[['Close', 'Volume']].plot(subplots=True, figsize=(10, 10))
plt.show()

parsed.describe()
