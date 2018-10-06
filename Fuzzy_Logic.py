# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 15:41:08 2018

@author: ytng0
"""
import numpy as np
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt 
import time
import pandas as pd
import MA_components as maComp

class FuzzyLogic:
    name = "FuzzyLogic"
            #100 for 100 training data (100 moving average)
    yearMN = np.zeros(shape=(12,100))
    bucketArray = np.zeros(7)
    
    MA_Type = [0,1,2,3]
    longMA = [10,20,50,100,150,200]
    shortMA = [1,3,5,10,15,20]
    
    permuationDict = {}
    
    def __init__(self, trainingPeriodStart, trainindPeriodEnd, dataframe):
        self.name = "FuzzyLogic"
        self.ComputeMovingAverageForYear(trainingPeriodStart, trainindPeriodEnd, dataframe)
        self.trainingLength = trainindPeriodEnd - trainingPeriodStart
        
    def RetriveDiffInValue(self,MAType, m, n):
        myKey = "%s %s %s" % (int(MAType),int(m), int(n))
        return self.permuationDict[myKey]
        
    def ComputeMovingAverageForYear(self, startIndex, endIndex, df):
        for MAType in self.MA_Type:       
            for Lma in self.longMA:               
                for Sma in self.shortMA:
                    if (Lma > Sma):
                        
#                       mValues = maComp.computeMA('sma', (trainingStart - M) , traningEnd, M, data)
                        mValues = maComp.computeMA(MAType, (startIndex - Lma), endIndex, Lma, df)
                        nValues = maComp.computeMA(MAType, (startIndex - Sma), endIndex, Sma, df)
                                                      
                        v =  np.subtract(mValues, nValues)
                        sortedArray =  np.sort(v)
                        myKey = "%s %s %s" % (int(MAType),int(Lma), int(Sma))
                        self.permuationDict[myKey] = sortedArray
        

        

    def ComputeQuadraticFunction(self, neighbourBucket, selfBucket, x):

        diffSquared = (neighbourBucket - selfBucket)**2
        a = -1.0 / diffSquared
        b = (x - selfBucket)**2
        y = (a * b) + 1
        return y
    

        
    def CheckIfInRange(self,a, b, x):
        maxValue = b
        minValue = a
        if (a >= b):
            maxValue = a
            minValue = b
        
        if (x >= minValue and x <= maxValue):
            return True
        else:
            return False
    
    def DrawInternalGraph(self, MAType, mLength, nLength, neighbourValue, SelfValue, side, buckekValue):

            degreeArray = []
            xArray = []
           
            if (side == 'left'):
                currentIndexValue = neighbourValue 
                while (currentIndexValue <= SelfValue):   #Clustering    
                    xArray.append(currentIndexValue)
                    y = self.ComputeQuadraticFunction(neighbourValue,SelfValue,currentIndexValue)   
                    degreeArray.append(y)
                    currentIndexValue += 0.1
            else:
                currentIndexValue = SelfValue 
                while (currentIndexValue <= neighbourValue):   #Clustering    
                    xArray.append(currentIndexValue)
                    y = self.ComputeQuadraticFunction(neighbourValue,SelfValue,currentIndexValue)   
                    degreeArray.append(y)
                    currentIndexValue += 0.1
            colorCode = 'C'+ str(buckekValue + 1)
            plt.plot(xArray, degreeArray,colorCode)

        
        
    def PlotGraph(self, MAType, mLength, nLength, clustering = False):
        #self.RetriveDiffInValue(MA_Type,m,n)
        sortedArray =  self.RetriveDiffInValue(int(MAType),int(mLength),int(nLength))
       
        #clustering
        kmeans = KMeans(n_clusters=7, random_state=0).fit(sortedArray.reshape(-1,1))
            
        clustersValues = kmeans.cluster_centers_[:,0] 
        clustersValues.sort()
       
        CIntervalues = np.zeros(7)
        
        if (clustering == True):
            CIntervalues[0] = clustersValues[0]
            CIntervalues[1] = clustersValues[1]
            CIntervalues[2] = clustersValues[2]
            CIntervalues[3] = clustersValues[3]
            CIntervalues[4] = clustersValues[4]
            CIntervalues[5] = clustersValues[5]
            CIntervalues[6] = clustersValues[6]
        
        else:
            idx = (np.abs(sortedArray - 0)).argmin() #Find the neartest index closest to 0
            lengthOfPositive = self.trainingLength - idx 
        
             
            CIntervalues[0] = sortedArray[0]
            CIntervalues[1] = sortedArray[int (idx * 0.33)]
            CIntervalues[2] = sortedArray[int (idx * 0.667)]
            CIntervalues[3] = sortedArray[idx]
            CIntervalues[4] = sortedArray[idx + int(lengthOfPositive * 0.33)]
            CIntervalues[5] = sortedArray[idx + int(lengthOfPositive * 0.667)]
            CIntervalues[6] = sortedArray[self.trainingLength - 1]
        
    
        print (CIntervalues)

        p = 6
        if (p == 6):

            leftValue = CIntervalues[p-1]
            pValue = CIntervalues[p]
            self.DrawInternalGraph  (MAType,mLength,nLength,leftValue,pValue,'left',p)

            
        p = 0
        if (p == 0):
             rightValue = CIntervalues[p+1]
             pValue = CIntervalues[p] 
             self.DrawInternalGraph  (MAType,mLength,nLength,rightValue,pValue,'right',p)

        
        p = 1
        while (p < 6):
            leftValue = CIntervalues[p-1]
            rightValue = CIntervalues[p+1]
            pValue = CIntervalues[p]
            
            self.DrawInternalGraph  (MAType,mLength,nLength,leftValue,pValue,'left',p)
            self.DrawInternalGraph  (MAType,mLength,nLength,rightValue,pValue,'right',p)
            p += 1         
 
      
        plt.xlabel('x - axis') 
        plt.ylabel('y - axis') 
        plt.show()  
        
        
    def ComputeMembership(self, value, m, n, MA_Type, bucket, Clustering = False):
    
        sortedArray =  self.RetriveDiffInValue(MA_Type,m,n)

        #clustering
        if (Clustering == True):
            
            kmeans = KMeans(n_clusters=7, random_state=0).fit(sortedArray.reshape(-1,1))
                
            clustersValues = kmeans.cluster_centers_[:,0] 
            clustersValues.sort()
           
            self.bucketArray[0] = clustersValues[0]
            self.bucketArray[1] = clustersValues[1]
            self.bucketArray[2] = clustersValues[2]
            self.bucketArray[3] = clustersValues[3]
            self.bucketArray[4] = clustersValues[4]
            self.bucketArray[5] = clustersValues[5]
            self.bucketArray[6] = clustersValues[6]
        else:
            
            #Find Value closest to 0 and set it to p4
            idx = (np.abs(sortedArray - 0)).argmin()
            lengthOfPositive = self.trainingLength - idx - 1
        
            self.bucketArray[0] = sortedArray[0] #P1
            self.bucketArray[1] = sortedArray[int (idx * 0.33)]
            self.bucketArray[2] = sortedArray[int (idx * 0.667)]
            self.bucketArray[3] = sortedArray[idx]
            self.bucketArray[4] = sortedArray[idx + int(lengthOfPositive * 0.33)]
            self.bucketArray[5] = sortedArray[idx + int(lengthOfPositive * 0.667)]
            self.bucketArray[6] = sortedArray[self.trainingLength - 1] #P7

        membershipdegree = -1.0
        
        if (bucket == 0): #P1
            if (value <  self.bucketArray[0]):
                membershipdegree = 1.0      
            elif (self.CheckIfInRange(self.bucketArray[0], self.bucketArray[1], value) == True): #rightside
                membershipdegree = self.ComputeQuadraticFunction(self.bucketArray[1], self.bucketArray[0], value)      
        elif (bucket == 6): #p7
            if (value >  self.bucketArray[6]):
                membershipdegree = 1.0      
            elif ((self.CheckIfInRange(self.bucketArray[5], self.bucketArray[6], value)) == True): #leftside
                membershipdegree = self.ComputeQuadraticFunction(self.bucketArray[5], self.bucketArray[6], value)
        elif ((bucket > 0) and (bucket < 6)):
            if (value < self.bucketArray[bucket]): #left side of the curve
                membershipdegree = self.ComputeQuadraticFunction(self.bucketArray[bucket-1], self.bucketArray[bucket], value)
            else:
                membershipdegree = self.ComputeQuadraticFunction(self.bucketArray[bucket+1], self.bucketArray[bucket], value)                            
        else:
            return -1.0
        return membershipdegree



def costly_func():
    start = time.clock()
    for i in range (100000):
     
        floglic.ComputeMembership(50,200,10,0,4)  
    print (time.clock() - start)
    






















