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

GA_Iterations= 1

#SubGroupSize=0# No need to change
TargetIndex=1000
TradeWhenIntersection=True #set to True if only trade at intersection or False if trade at every data point
dfType = 1 # 1: run datafile by min   2:run datafile by day 3: run datafile by hour
if dfType == 1:
    SubGroupSize = 1000
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_Parsed.xlsx'))
elif dfType == 2:
    SubGroupSize = 200
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_ParsedByDay.xlsx'))
elif dfType == 3:
    SubGroupSize=250
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_ParsedByHour.xlsx'))

#noOfDays = parsed.groupby(['Date']).aggregate({'Date':'count'})
#print('Number of Days: ', len(noOfDays))
print('--------------')
print("Total number of indexes: ",len(parsed))
# NumberOfGroups = int((len(parsed) / SubGroupSize) -3)
NumberOfGroups = int(len(parsed) / 2 / SubGroupSize)
print("Total number of groups: ",NumberOfGroups)
print('--------------')

dfTmp = parsed[parsed['Date']== '2014-01-02']
TargetIndex = dfTmp.index.values[0]
print('Target Index: ',TargetIndex)

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
    rule_choices = genetic_algo.generate_rule_choices('different', # Parameters: 'same' or 'different'
                                                      [0,1,2,3], # Choices for MA type
                                                      [10,20,50,100,150,200], # Choices for m
                                                      [1,3,5,10,15,20]) # Choices for n
    Collection = genetic_algo.generate_collection(20, 10, rule_choices)

    print("--------------------------------------")
    print("Begin of group: ",i+1,datetime.datetime.now())
    y1 += SubGroupSize
    y2 = y1 + SubGroupSize
    y3 = y2 + SubGroupSize
    y4 = y3 + SubGroupSize
    print('Begin of training SubGroup: '+ str(y1))
    print('Begin of select SubGroup: '+ str(y2))
    print('Begin of testing SubGroup: '+ str(y3))
    print('End of testing SubGroup: '+ str(y4))
    if (y4+SubGroupSize)>len(parsed):
        y4=len(parsed)-1
        print('Final end of testing SubGroup: '+ str(y4))
    #Apply first random rule on training section
    flogic = fuzzy.FuzzyLogic(y1, y3,parsed.loc[:,:],True,True)
    FF =FitnessFunction.FitnessFunction(y1,y3,parsed.loc[:,:],Collection,flogic,[10000000.0,0,0,0,0,0,0],True,False,TradeWhenIntersection)
    result = FF.getRreturn(parsed.loc[:,:])
    Collection = genetic_algo.evolve(Collection, rule_choices, [0 if i < 0 else i for i in result.values], 0.7, 0.01)

    BestReturn=-10
    BestIndividual=[[]]
    rreturnLog=[]

    iteration_final_values = []
    iteration_final_values_max = []
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

        iteration_final_values.append(result.values)
        iteration_final_values_max.append(result.values.max())
        Collection = genetic_algo.evolve(Collection, rule_choices, [0 if i < 0 else i for i in result.values], 0.7, 0.01)

    iteration_final_values_df = pd.DataFrame({'GA Iteration': np.arange(1,GA_Iterations+1),
                                              'Fitness Values': iteration_final_values,
                                              'Max Fitness Value': iteration_final_values_max})

    if i == 0:
        iteration_final_values_df.to_csv(os.path.join(directory, 'data/'+'Group'+str(i+1)+'_iteration_final_values.csv'))

    #Apply best individual to test section then record total asset.
    print(rreturnLog)
    Collection = BestIndividual
    FF =FitnessFunction.FitnessFunction(y3,y4,parsed.loc[:,:],Collection,flogic,AccountStatus,FirstPosition,True,TradeWhenIntersection)
    #store account status after applying best individual.
    AccountStatus = FF.getAccountStatus()
    totalAsset = FF.getTotalAsset(parsed.loc[:,:])
    totalAssets.append(totalAsset)
    print("End of group: ",i+1,datetime.datetime.now())
    if y4 == (len(parsed)-1):
        break
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


#plt.plot(totalAssets)
#plt.ylabel('Total Assets')
#plt.xlabel('Group')
#plt.show()