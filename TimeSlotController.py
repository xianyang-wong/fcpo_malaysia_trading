import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

directory = '/Users/qingtao/OneDrive - National University of Singapore/MTech/01 KE5207/computational intelligence ii/Lecture Notes/Day 3 (Sam GU Zhan)/GA-Fuzzy CA - Algorithmic Trading System/'
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

#plots = parsed[['Close', 'Volume']].plot(subplots=True, figsize=(10, 10))
#plt.show()




print(parsed.shape)

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
