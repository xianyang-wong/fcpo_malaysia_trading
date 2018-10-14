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
GA_Iterations=3
#SubGroupSize=0# No need to change
TargetIndex=1000
TradeWhenIntersection=False #set to True if only trade at intersection or False if trade at every data point
dfType = 2 # 1: run datafile by min   2:run datafile by day 3: run datafile by hour
if dfType == 1:
    SubGroupSize = 200
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_Parsed.xlsx'))
elif dfType == 2:
    SubGroupSize = 200
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_ParsedByDay.xlsx'))
elif dfType == 3:
    SubGroupSize=250
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_ParsedByHour.xlsx'))    

print('--------------')
print("Total number of indexes: ",len(parsed))
NumberOfGroups = int((len(parsed) / SubGroupSize) -3)
print("Total number of groups: ",NumberOfGroups)
print('--------------')

dfTmp = parsed[parsed['Date']== '2014-01-02']
TargetIndex = dfTmp.index.values[0]
print('Test Index: ',TargetIndex)

y1=TargetIndex-(SubGroupSize* 3)
y2=0
y3=0
y4=0

totalAssets = []
AccountStatus = [10000000.0,0,0,0,0,0,0]
FirstPosition = True
for i in range (0,NumberOfGroups):
    #Close position when last test group done.In order to calculate total asset
    if i != 0:
        FirstPosition = False
    Collection = genetic_algo.generate_collection(20, 10, genetic_algo.rule_choices)
    print("--------------------------------------")
    print("Begin of group: ",i+1,datetime.datetime.now())
    y1 += SubGroupSize
    y2 = y1 + SubGroupSize
    y3 = y2 + SubGroupSize
    y4 = y3 + SubGroupSize
    print('Begin of training SubGroup: '+ str(y1))
    print('Begin of select SubGroup: '+ str(y2))
    print('Begin of testing SubGroup: '+ str(y3))
    if (y4+SubGroupSize)>len(parsed):
        y4=len(parsed)-1
        print('End of testing SubGroup: '+ str(y4)) 
        break
    #Apply first random rule on training section
    flogic = fuzzy.FuzzyLogic(y1, y3,parsed.loc[:,:],True,True)
    FF =FitnessFunction.FitnessFunction(y1,y3,parsed.loc[:,:],Collection,flogic,[10000000.0,0,0,0,0,0,0],True,False,TradeWhenIntersection)
    result = FF.getRreturn(parsed.loc[:,:])
    Collection = genetic_algo.evolve(Collection, genetic_algo.rule_choices, result.values, 0.7, 0.01)
    BestReturn=-10
    BestIndividual=[[]]
    rreturnLog=[]
    #Apply mutated individual(out of the best from last stage) to selection section and evolve 50 generations
    for j in range(0,GA_Iterations):#some code to keep track of the best individual!!!!
        print("Processing GA iteration ",j)
        FF =FitnessFunction.FitnessFunction(y2,y3,parsed.loc[:,:],Collection,flogic,[10000000.0,0,0,0,0,0,0],True,False,TradeWhenIntersection)
        result = FF.getRreturn(parsed.loc[:,:])
        #print(result)
        if BestReturn < result.max(skipna=True):
            BestIndividual[0] = Collection[result.idxmax(axis=0,skipna=True)]
            rreturnLog.append(result.max(skipna=True))
            BestReturn = result.max(skipna=True)
        
        Collection = genetic_algo.evolve(Collection, genetic_algo.rule_choices, result.values, 0.7, 0.01)
    #Apply best individual to test section then record total asset.
    print(rreturnLog)
    Collection = BestIndividual
    FF =FitnessFunction.FitnessFunction(y3,y4,parsed.loc[:,:],Collection,flogic,AccountStatus,FirstPosition,True,TradeWhenIntersection)
    #store account status after applying best individual.
    AccountStatus = FF.getAccountStatus()
    totalAsset = FF.getTotalAsset(parsed.loc[:,:])
    totalAssets.append(totalAsset)
    print("End of group: ",i+1,datetime.datetime.now())
    print("--------------------------------------")

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