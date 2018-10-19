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
import numpy as np
import itertools
import random


directory = ''

#configuration parameters.

GA_Iterations= 2

#SubGroupSize=0# No need to change
TargetIndex=1000
TradeWhenIntersection=True #set to True if only trade at intersection or False if trade at every data point
dfType = 2 # 1: run datafile by min   2:run datafile by day 3: run datafile by hour
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

    rule_choices = genetic_algo.generate_rule_choices('different',  # Parameters: 'same' or 'different'
                                                      [0,1,2,3],  # Choices for MA type
                                                      [10,20,50,100,150,200], # Choices for m
                                                      [1,3,5,10,15,20]) # Choices for n

    # Generate initial collection of rulesets
    collection_records = [genetic_algo.generate_collection(20, 10, rule_choices)]

    # To log results from train period
    rreturnLog = []
    iteration_final_values = []
    iteration_final_values_max = []

    for j in range(0,GA_Iterations):
        print("Processing Group ", i+1, "out of ", NumberOfGroups, "GA iteration ", j+1, "out of ", GA_Iterations)
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

        flogicTrain = fuzzy.FuzzyLogic(y1, y3,parsed.loc[:,:],True,True)
        FFTrain =FitnessFunction.FitnessFunction(y1,y3,parsed.loc[:,:],collection_records[j],flogicTrain,[10000000.0,0,0,0,0,0,0],True,False,TradeWhenIntersection)
        resultTrain = FFTrain.getRreturn(parsed.loc[:,:])
        iteration_final_values.append(resultTrain.values)
        iteration_final_values_max.append(resultTrain.values.max())

        BestReturnTrain=resultTrain.max()
        BestIndividualTrain=collection_records[j][resultTrain.idxmax(axis=0)]

        flogicSelection = fuzzy.FuzzyLogic(y2, y3, parsed.loc[:, :], True, True)
        FFSelection =FitnessFunction.FitnessFunction(y2,y3,parsed.loc[:,:],collection_records[j],flogicSelection,[10000000.0,0,0,0,0,0,0],True,False,TradeWhenIntersection)
        resultSelection = FFSelection.getRreturn(parsed.loc[:,:])

        BestReturnSelection = resultSelection.max()
        BestIndividualSelection = collection_records[j][resultSelection.idxmax(axis=0)]

        # Comparing Selection and Train returns after normalizing train returns to same period length as selection
        if BestReturnSelection - (((1+BestReturnTrain)**0.5)-1) > 0.05:
            BestIndividual = BestIndividualSelection
            rreturnLog.append(((1+BestReturnSelection)**2)-1)
            BestReturn = ((1+BestReturnSelection)**2)-1
        else:
            BestIndividual = BestIndividualTrain
            rreturnLog.append(BestReturnTrain)
            BestReturn = BestReturnTrain

        collection_new = genetic_algo.evolve(collection_records[j], rule_choices, [i + np.abs(resultTrain.values.min() + 0.0000001) for i in resultTrain.values], 0.7, 0.01)
        collection_records.append(collection_new)

    #Apply best individual to test section then record total asset.
    print(rreturnLog)
    TestCollection = collection_records[0].copy()
    TestCollection[0] = BestIndividual

    FFTest =FitnessFunction.FitnessFunction(y3,y4,parsed.loc[:,:],TestCollection,flogicTrain,AccountStatus,FirstPosition,True,TradeWhenIntersection)
    #store account status after applying best individual.
    AccountStatus = FFTest.getAccountStatus()
    totalAsset = FFTest.getTotalAsset(parsed.loc[:,:])
    totalAssets.append(totalAsset)
    print("End of group: ",i+1,datetime.datetime.now())
    if y4 == (len(parsed)-1):
        break
    print("--------------------------------------")

    if i == 0:
         ### CHECK OF COLLECTION RECORDS
         iteration_final_values_df = pd.DataFrame({'GA Iteration': np.arange(1, GA_Iterations + 1),
                                                   'Fitness Values': iteration_final_values,
                                                   'Max Fitness Value': iteration_final_values_max})
         print('C Check')
         for c in range(0, len(collection_records[0])):
             if collection_records[1][c] in collection_records[0]:
                 print(c)
         print('F Check')
         for f in range(0, len(iteration_final_values_df['Fitness Values'][0])):
             if iteration_final_values_df['Fitness Values'][1][f] in iteration_final_values_df['Fitness Values'][0]:
                 print(f)
         iteration_final_values_df.to_csv(os.path.join(directory, 'data/'+'Group'+str(i+1)+'_iteration_final_values.csv'))

print(len(totalAssets))
print(totalAssets)

df = pd.DataFrame(data=totalAssets, columns=['Total Assets'])
df['Group']=df.index+1
df = df[['Group', 'Total Assets']]
print(df)
writer = pd.ExcelWriter(os.path.join(directory,'data/TotalAssets.xlsx'), engine='xlsxwriter')
df.to_excel(writer)
writer.save()


#plt.plot(totalAssets)
#plt.ylabel('Total Assets')
#plt.xlabel('Group')
#plt.show()

