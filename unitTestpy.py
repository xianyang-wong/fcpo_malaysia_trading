# -*- coding: utf-8 -*-
"""
Created on Sun Sep 30 23:04:01 2018

@author: ytng0
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import MA_components as maComp

data = pd.read_excel('data/dummy.xlsx')

print("Start testing")


trainingStart= 5000
traningEnd = 7000
M = 10
N = 1


print ("test")
mValues = maComp.computeMA(3, trainingStart, traningEnd, M, data)
print (len(mValues))
##print (data[195:200])
#
#
nValues = maComp.computeMA(3, trainingStart, traningEnd, N, data)
print (len(nValues))
#

