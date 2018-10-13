#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 09:50:16 2018

@author: qingtao
"""
import FitnessFunction 
import genetic_algo
import pandas as pd
import os
import datetime
import Fuzzy_Logic as fuzzy
import matplotlib.pyplot as plt


directory = ''

#configuration parameters.
GA_Iterations=51
SubGroupSize=0
TargetIndex=1000
dfType = 2 # 1: run datafile by min   2:run datafile by day 3: run datafile by hour
if dfType == 1:
    SubGroupSize = 200
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_Parsed.xlsx'))
elif dfType == 2:
    SubGroupSize = 200
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_ParsedByDay.xlsx'))
elif dfType == 3:
    #num_of_groups = 17
    SubGroupSize=250
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_ParsedByHour.xlsx'))    

print('--------------')
print("Total number of indexes: ",len(parsed))
NumberOfGroups = int((len(parsed) / SubGroupSize) -3)
print("Total number of groups: ",NumberOfGroups)
print('--------------')

y1=TargetIndex-(SubGroupSize* 2)
y2=0
y3=0
y4=0

totalAssets = []
AccountStatus = [1000000.0,0,0,0,0,0]
ClosePosition = False
for i in range (0,NumberOfGroups):
    #Close position when last test group done.In order to calculate total asset
    if i == NumberOfGroups-1:
        ClosePosition = True
    Collection = genetic_algo.generate_collection(20, 10, genetic_algo.rule_choices)
    print("Begin of group: ",i+1,datetime.datetime.now())
    y1 += SubGroupSize
    # yTmp = y1 + subGroupSize
    # y2 = yTmp + subGroupSize
    y2 = y1 + SubGroupSize
    y3 = y2 + SubGroupSize
    y4 = y3 + SubGroupSize
    print('Begin of training SubGroup: '+ str(y1))
    print('Begin of select SubGroup: '+ str(y2))
    print('Begin of testing SubGroup: '+ str(y3))
    print('End of testing SubGroup: '+ str(y4))
    
    #Apply first random rule on training section
    flogic = fuzzy.FuzzyLogic(y1, y3,parsed,True,True)
    FF =FitnessFunction.FitnessFunction(y1,y3,parsed,Collection,flogic,[1000000.0,0,0,0,0,0],True,False)
    result = FF.getRreturn()
    Collection = genetic_algo.evolve(Collection, genetic_algo.rule_choices, result.values, 0.7, 0.01)
    BestReturn=-10
    BestIndividual=[[]]
    rreturnLog=[]
    #Apply mutated individual(out of the best from last stage) to selection section and evolve 50 generations
    for j in range(0,GA_Iterations):#some code to keep track of the best individual!!!!
        #print("GA iteration ",j)
        FF =FitnessFunction.FitnessFunction(y2,y3,parsed,Collection,flogic,[1000000.0,0,0,0,0,0],True,False)
        result = FF.getRreturn()
        #print(result)
        if BestReturn < result.max(skipna=True):
            BestIndividual[0] = Collection[result.idxmax(axis=0,skipna=True)]
            rreturnLog.append(result.max(skipna=True))
            BestReturn = result.max(skipna=True)
        Collection = genetic_algo.evolve(Collection, genetic_algo.rule_choices, result.values, 0.7, 0.01)
    #Apply best individual to test section then record total asset.
    print(rreturnLog)
    Collection = BestIndividual
    FF =FitnessFunction.FitnessFunction(y3,y4,parsed,Collection,flogic,AccountStatus,ClosePosition,True)
    #store account status after applying best individual.
    AccountStatus = FF.getAccountStatus()
    totalAsset = FF.getTotalAsset(parsed)
    totalAssets.append(totalAsset)
    print("End of group: ",i+1,datetime.datetime.now())

print(len(totalAssets))
print(totalAssets)

df = pd.DataFrame(data=totalAssets, columns=['Total Assets'])
df['Group']=df.index+1
df = df[['Group','Total Assets']]
print(df)
writer = pd.ExcelWriter(os.path.join(directory,'data/TotalAssets.xlsx'), engine='xlsxwriter')
df.to_excel(writer)
writer.save()


plt.plot(totalAssets)
plt.ylabel('Total Assets')
plt.xlabel('Group')
plt.show()