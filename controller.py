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

directory = ''
parsed = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_Parsed.xlsx'))

#configuration parameters.
GA_Iterations=51
Num_of_groups=69

print('--------------')
print(len(parsed))
groupSize = int(len(parsed)/Num_of_groups)
subGroupSize = int(groupSize/4)
groupLength = int(len(parsed)/subGroupSize) - 3
print(groupSize)
print(subGroupSize)
print('--------------')

y1=0
y2=0
y3=0
y4=0

for i in range (0,groupLength):
    Collection = genetic_algo.generate_collection(20, 10, genetic_algo.rule_choices)
    print("Begin of group ",i,datetime.datetime.now())
    print('Group: '+ str(i+1))
    y1 += subGroupSize
    # yTmp = y1 + subGroupSize
    # y2 = yTmp + subGroupSize
    y2 = y1 + subGroupSize
    y3 = y2 + subGroupSize
    y4 = y3 + subGroupSize
    print('Sub Group Index 1: '+ str(y1))
    print('Sub Group Index 2: '+ str(y2))
    print('Sub Group Index 3: '+ str(y3))
    print('Sub Group Index 4: '+ str(y4))

    
    #Apply first random rule on training section
    FF =FitnessFunction.FitnessFunction(y1,y3,parsed,Collection)
    result = FF.getRreturn()
    Collection = genetic_algo.evolve(Collection, genetic_algo.rule_choices, result.values, 0.7, 0.01)
    BestReturn=-101
    BestIndividual=[[]]
    debug=[]
    #Apply mutated individual(out of the best from last stage) to selection section and evolve 50 generations
    for j in range(0,GA_Iterations):#some code to keep track of the best individual!!!!
        #print("GA iteration ",j)
        FF =FitnessFunction.FitnessFunction(y2,y3,parsed,Collection)
        result = FF.getRreturn()
        #print(result)
        if BestReturn < result.max(skipna=True):
            BestIndividual[0] = Collection[result.idxmax(axis=0,skipna=True)]
            debug.append(result.max(skipna=True))
            BestReturn = result.max(skipna=True)
        Collection = genetic_algo.evolve(Collection, genetic_algo.rule_choices, result.values, 0.7, 0.01)
    #Apply best individual to test section then record total asset.
    print(debug)
    Collection = BestIndividual
    FF =FitnessFunction.FitnessFunction(y3,y4,parsed,Collection)
    FF.getTotalAsset()
    print("End of group ",i,datetime.datetime.now())