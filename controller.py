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


directory = ''

#configuration parameters.
GA_Iterations=51

dfType = 2 # 1: run datafile by min   2:run datafile by day 3: run datafile by hour
if dfType == 1:
    num_of_groups = 69
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_Parsed.xlsx'))
elif dfType == 2:
    num_of_groups = 3
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_ParsedByDay.xlsx'))
elif dfType == 3:
    num_of_groups = 17
    parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_ParsedByHour.xlsx'))    

print('--------------')
print("Total number of indexes",len(parsed))
groupSize = int(len(parsed)/num_of_groups)
subGroupSize = int(groupSize/4)
groupLength = int(len(parsed)/subGroupSize) - 3
print("Group size",groupSize)
print("SubGroup size",subGroupSize)
print('--------------')

y1=0
y2=0
y3=0
y4=0

for i in range (0,groupLength):
    Collection = genetic_algo.generate_collection(20, 10, genetic_algo.rule_choices)
    print("Begin of group ",i+1,datetime.datetime.now())
    y1 = subGroupSize*9
    # yTmp = y1 + subGroupSize
    # y2 = yTmp + subGroupSize
    y2 = y1 + subGroupSize
    y3 = y2 + subGroupSize
    y4 = y3 + subGroupSize
    print('Begin of training SubGroup: '+ str(y1))
    print('Begin of select SubGroup: '+ str(y2))
    print('Begin of testing SubGroup: '+ str(y3))
    print('End of testing SubGroup: '+ str(y4))
    
    #Apply first random rule on training section
    flogic = fuzzy.FuzzyLogic(y1, y3,parsed,True)
    FF =FitnessFunction.FitnessFunction(y1,y3,parsed,Collection,flogic)
    result = FF.getRreturn()
    Collection = genetic_algo.evolve(Collection, genetic_algo.rule_choices, result.values, 0.7, 0.01)
    BestReturn=-10
    BestIndividual=[[]]
    rreturnLog=[]
    #Apply mutated individual(out of the best from last stage) to selection section and evolve 50 generations
    for j in range(0,GA_Iterations):#some code to keep track of the best individual!!!!
        print("GA iteration ",j)
        FF =FitnessFunction.FitnessFunction(y2,y3,parsed,Collection,flogic)
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
    FF =FitnessFunction.FitnessFunction(y3,y4,parsed,Collection,flogic)
    totalAsset = FF.getTotalAsset()
    print("End of group ",i+1,datetime.datetime.now())
    