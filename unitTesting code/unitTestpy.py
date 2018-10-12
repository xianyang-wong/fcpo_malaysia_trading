# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 23:04:01 2018

@author: ytng0
"""
import sys
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import MA_components as maComp
import time

##data = pd.read_excel('data/dummy.xlsx')
data = pd.read_excel('data/FCPO_6_years_NUS_ParsedByDay.xlsx')
print("Start testing")


trainingStart= 2205
traningEnd = 2950
M = 150
N = 200

print ("test")
start_time = time.time()
mValues = maComp.computeMA(1, trainingStart, traningEnd, M, data)
print (len(mValues))
print("mruntime: --- %s seconds ---" % (time.time() - start_time))

##print (data[195:200])
#
start_time = time.time()
nValues = maComp.computeMA(1, trainingStart, traningEnd, N, data)
print (len(nValues))
print("nruntime: --- %s seconds ---" % (time.time() - start_time))
#

