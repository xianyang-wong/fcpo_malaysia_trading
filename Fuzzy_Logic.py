# -*- coding: utf-8 -*-
"""
Created on Sun Sep 23 15:41:08 2018

@author: ytng0
"""
import numpy as np
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt 
import pandas as pd
import MA_components as maComp

class FuzzyLogic:
    name = "FuzzyLogic"
            #100 for 100 training data (100 moving average)
    yearMN = np.zeros(shape=(12,100))
    
    MA_Type = [0,1,2,3]
    MA_Type2= [0,1,2,3]
    longMA = [10,20,50,100,150,200]
    shortMA = [1,3,5,10,15,20]

    permuationDict = {}
    usingTwoMAs = False
    
    def __init__(self, trainingPeriodStart, trainindPeriodEnd, dataframe, cluster = False, usingDifferentMA = False):
        self.name = "FuzzyLogic"
        self.trainingLength = trainindPeriodEnd - trainingPeriodStart
        self.usingTwoMAs = usingDifferentMA
        self.ComputeMovingAverageForYear(trainingPeriodStart, trainindPeriodEnd, dataframe, cluster, usingDifferentMA)
      
            
    def RetriveDiffInValue(self,MAType, m, n, MATypeTwo = -1):
        if (self.usingTwoMAs == True):
            myKey = "%s %s %s %s" % (int(MAType), int(MATypeTwo), int(m), int(n))  
        else:
            myKey = "%s %s %s" % (int(MAType),int(m), int(n))
        return self.permuationDict[myKey]
        
    def ComputeMovingAverageForYear(self, startIndex, endIndex, df, clustering = False, usingDifferentMAType = False):
        
         
        for MAType in self.MA_Type:    
            for MAType2 in self.MA_Type2:
                for Lma in self.longMA:               
                    for Sma in self.shortMA:
                        if (Lma > Sma):
                            
                            mValues = maComp.computeMA(MAType, (startIndex), endIndex, Lma, df)
                            if (usingDifferentMAType == True):
                                nValues = maComp.computeMA(MAType2, (startIndex), endIndex, Sma, df)
                            else:
                                nValues = maComp.computeMA(MAType, (startIndex), endIndex, Sma, df)
    
                            if (len(mValues) != len(nValues)):
                                print("TO TAKE NOTE!!! MA_TYpe " , MAType, "M values ", Lma,  "N values ", Sma)
                                continue
                            
                            v =  np.subtract(nValues, mValues)
                            sortedArray =  np.sort(v)
                         
                                                            
    						#Set Clustering code here
                            CIntervalues = np.zeros(7)
                            if (clustering == True):
                                #clustering #Temp. to put logic at initalization
                                kmeans = KMeans(n_clusters=7, random_state=0).fit(sortedArray.reshape(-1,1))
                                    
                                clustersValues = kmeans.cluster_centers_[:,0] 
                                clustersValues.sort()
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
                                
                            if (usingDifferentMAType):
                                myKey = "%s %s %s %s" % (int(MAType),int(MAType2), int(Lma), int(Sma))
                            else:
                                myKey = "%s %s %s" % (int(MAType), int(Lma), int(Sma))
            
                            self.permuationDict[myKey] = CIntervalues
              

    def ComputeQuadraticFunction(self, neighbourBucket, selfBucket, x):
        diffSquared = (neighbourBucket - selfBucket)**2
        if (diffSquared == 0):
            diffSquared = 0.00001
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
    
    def DrawInternalGraph(self, mLength, nLength, neighbourValue, SelfValue, side, buckekValue):

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

        
        
    def PlotGraph(self, MAType, mLength, nLength, MATypeTwo = -1):
        #self.RetriveDiffInValue(MA_Type,m,n)
        CIntervalues =  self.RetriveDiffInValue(int(MAType),int(mLength),int(nLength), MATypeTwo)
       
    
        print (CIntervalues)

        p = 6
        if (p == 6):

            leftValue = CIntervalues[p-1]
            pValue = CIntervalues[p]
            self.DrawInternalGraph  ( mLength,nLength,leftValue,pValue,'left',p)

            
        p = 0
        if (p == 0):
             rightValue = CIntervalues[p+1]
             pValue = CIntervalues[p]   
             self.DrawInternalGraph  ( mLength,nLength,rightValue,pValue,'right',p)

                
             

        
        p = 1
        while (p < 6):
            leftValue = CIntervalues[p-1]
            rightValue = CIntervalues[p+1]
            pValue = CIntervalues[p]
            
            self.DrawInternalGraph  (mLength,nLength,leftValue,pValue,'left',p)
            self.DrawInternalGraph  (mLength,nLength,rightValue,pValue,'right',p)
            p += 1         
 
      
        plt.xlabel('x - axis') 
        plt.ylabel('y - axis') 
        plt.show()  
        
        
    def ComputeMembership(self, value, m, n, MA_Type, bucket, MA_TypeTwo = -1):
    
        CIntervalues =  self.RetriveDiffInValue(MA_Type,m,n, MA_TypeTwo)
        
        membershipdegree = -1.0
        
        if (bucket == 0): #P1
            if (value <  CIntervalues[0]):
                membershipdegree = 1.0      
            elif (self.CheckIfInRange(CIntervalues[0], CIntervalues[1], value) == True): #rightside
                membershipdegree = self.ComputeQuadraticFunction(CIntervalues[1], CIntervalues[0], value)     
                
        elif (bucket == 6): #p7
            if (value >  CIntervalues[6]):
                membershipdegree = 1.0      
            elif ((self.CheckIfInRange(CIntervalues[5], CIntervalues[6], value)) == True): #leftside
                membershipdegree = self.ComputeQuadraticFunction(CIntervalues[5], CIntervalues[6], value)
                
        elif ((bucket > 0) and (bucket < 6)):
            if (value < CIntervalues[bucket]): #left side of the curve
                membershipdegree = self.ComputeQuadraticFunction(CIntervalues[bucket-1], CIntervalues[bucket], value)
            else:
                membershipdegree = self.ComputeQuadraticFunction(CIntervalues[bucket+1], CIntervalues[bucket], value)                            
        else:
            membershipdegree = 0
            
        if (membershipdegree < 0):
            membershipdegree = -1
        if (membershipdegree > 1):
            membershipdegree = -1
        return membershipdegree

#
#
#print ("Test")
#
#
#data = pd.read_excel('data/FCPO_6_years_NUS_ParsedByDay.xlsx')
#trainingStart= 500
#print (len(data) )
#traningEnd = 2000
#floglic = FuzzyLogic(trainingStart, traningEnd,data, False, True) #False for Cluster, True for using 2 MA Values
#floglic.PlotGraph(3, 200, 10, 1) #Last value for the 2nd MA Type
#floglic.PlotGraph(3, 200, 10, 3) #Last value for the 2nd MA Type
#for i in range(-10, 10):  
#    print (i)
#    print (floglic.ComputeMembership( i,200,10,0,1,3)) # value, m, n, MA_Type, bucket, MA_Type2
#    print (floglic.ComputeMembership( i,200,10,3,1,2)) 
#
#
#floglic = FuzzyLogic(trainingStart, traningEnd,data, False, False) #False for Cluster, False for using 2 MA Values
#floglic.PlotGraph(3, 200, 10)
#
#for i in range(-10, 10):  
#    print (i)
#    print (floglic.ComputeMembership( i,200,10,0,1)) # value, m, n, MA_Type, bucket
#    print (floglic.ComputeMembership( i,200,10,3,1)) 
#
#
#







