import pandas as pd
import MA_components as maComp
import numpy as np
import matplotlib.pyplot as plt
import os

pd.set_option('display.float_format', lambda x: '%.3f' % x)

class FitnessFunction:
    Deposit = 0.15
    #Holding   Deposit
    rfrate = 0.02
    #risk free return,year rate
    minTradeCost=30.0
    #caculate moving average at give index, will call SeeTing function ,here use SMA instead.
    def MA_Diff(self,MAType,m,n,index,df):#SMA as demo
        mValues = maComp.computeMA(MAType[0], int(index), int(index), int(m), df)
        nValues = maComp.computeMA(MAType[1], int(index), int(index), int(n), df)
        v =  np.subtract(nValues,mValues)
        return v[0]

    def Average(self,list):
        if len(list) == 0:
            return -1
        else:
            return sum(list)/len(list)
    
    #ListInitialState is the account status,[a,b,c,d,e,f] a:initial balance , b: profit ,c:holding position ,d: accumulated cost of trading, e: risk free income ,f:deposit
    #FirstPosition takes 'True','False', indicate if the first index need to do trading
    #PlotHolding if 'True' will plot Hoding,Intersection,price against index
    def __init__(self,s0,s1,df,Collection,flogic,ListInitialState,IsFirstGroup,PlotHolding,TradeOnIntersection):
        self.fuzzylogic = flogic
        self.DfFitness = pd.DataFrame(np.array(ListInitialState*20).reshape(20,7),columns=['capital','profit','holding','cost','riskfree','deposit','lastTradeValue'])
        #used to keep track of last status
        self.StartIndex = s0
        self.EndIndex = s1
        self.DailyFirstIndex = s0
        self.LastMA=np.zeros(20)
        self.IsFirstGroup = IsFirstGroup
        self.PlotHolding = PlotHolding
        self.TradeOnIntersection = TradeOnIntersection
        self.ForPlot=[]
        self.TradeLog=[]
        for index in range(self.StartIndex, self.EndIndex):
            #prepare data for plotting
            self.tmpPlot=[]
            self.tmpPlot.append(index)
            self.tmpPlot.append(df.High[index])
            
            self.profitflag=np.zeros(20)
            self.tmpLog=[]
            self.tmpLog.append(index)
            #if df.Flag[index] == 1:
            #    self.DailyFirstIndex = index
            #calculate rlevel for each individual,20 in total
            rlevelList=[]
            MA_List=[]
            for ruleSet in Collection:
                tmpList=[]
                tmpMA=[]
                for rule in ruleSet:#rule:{a,b,c,d,e} a:MA [m type,n type] ,b:m {10,20,50100,150,200}, c:n {1,3,5,10,15,20} ,d:membership 0-6, e:recommand [-1, 1]
                    MAd = self.MA_Diff(rule[0],rule[1][0],rule[1][1],index,df)
                    recommandValue = self.fuzzylogic.ComputeMembership(MAd,int(rule[1][0]),int(rule[1][1]),int(rule[0][0]),int(rule[2]),int(rule[0][1]))
                    if recommandValue >= 0:#result will not be taken into account if recommandValue below 0
                        tmpList.append(recommandValue* rule[3])
                    tmpMA.append(MAd)
                rlevelList.append(self.Average(tmpList))
                if len(tmpMA) == 0:
                    tmpMA.append(0)
                MA_List.append(self.Average(tmpMA))
            self.DfRlevel = pd.DataFrame(rlevelList)#Dataframe that stores rlevel values for all 20 individuals
            #CrossFlag is used to determin if intersection happens.Possitive means no and Negative means intersection happens.
            self.CrossFlag = (np.multiply(np.asarray(MA_List),self.LastMA)).tolist()
            self.LastMA = np.asarray(MA_List)
            #if the ruleset only contain 1 rule then need to pad CrossFlag to 20 elements. then use sign to remove values just keep sign
            self.CrossFlag = np.sign(np.pad(self.CrossFlag, (0,(20 - len(self.CrossFlag))), 'constant', constant_values=(0, 0)))

            TmpDfFitness = pd.DataFrame(np.array([ListInitialState[0],0,0,0,0,0,0]*20).reshape(20,7),columns=['capital','profit','holding','cost','riskfree','deposit','lastTradeValue'])
            #Dataframe stores valeus to calculate fitness function at current moment.

            #Check if get close out
            for IndividualCount in range(0,20):    
                closeProfit=0
                CostModifier=0
                if self.DfFitness.holding[IndividualCount] > 0:
                    CostModifier = -200
                    closeProfit = 25 *self.DfFitness.iloc[IndividualCount]['holding'] * (df.Low[index]  - self.DfFitness.iloc[IndividualCount]['lastTradeValue'])
                else:
                    CostModifier = 200
                    closeProfit = 25 *self.DfFitness.iloc[IndividualCount]['holding'] * (df.High[index]  - self.DfFitness.iloc[IndividualCount]['lastTradeValue'])
                    
                if closeProfit + self.DfFitness.iloc[IndividualCount]['deposit'] < 0:# check out!! 
                    self.DfFitness.iloc[IndividualCount]['capital'] -= self.DfFitness.iloc[IndividualCount]['deposit']
                    self.DfFitness.iloc[IndividualCount]['deposit'] = 0
                    self.DfFitness.iloc[IndividualCount]['cost'] += max((abs(self.DfFitness.iloc[IndividualCount]['holding']) * (self.DfFitness.iloc[IndividualCount]['lastTradeValue']+CostModifier) * 0.002),self.minTradeCost)
                    
                    if IndividualCount == 0:
                        self.tmpLog.append('Yes')
                        #Log and plot part
                        self.tmpLog.append(self.DfFitness.iloc[IndividualCount]['profit'])
                        self.tmpLog.append(0)
                        self.tmpLog.append(self.DfFitness.iloc[IndividualCount]['deposit'])
                        self.tmpLog.append(self.DfFitness.iloc[IndividualCount]['riskfree'])
                        self.tmpLog.append(self.DfFitness.iloc[IndividualCount]['cost'])
                        closeProfit=0
                        if self.DfFitness.iloc[IndividualCount]['holding'] > 0:
                            closeProfit = 25 *self.DfFitness.iloc[0]['holding'] * (df.Low[index]  - self.DfFitness.iloc[0]['lastTradeValue'])
                        else:
                            closeProfit = 25 *self.DfFitness.iloc[0]['holding'] * (df.High[index]  - self.DfFitness.iloc[0]['lastTradeValue'])
                        totalAsset= self.DfFitness.iloc[IndividualCount]['capital'] + self.DfFitness.iloc[IndividualCount]['profit'] + self.DfFitness.iloc[IndividualCount]['riskfree'] - self.DfFitness.iloc[IndividualCount]['cost']+closeProfit
                        self.tmpLog.append(0)
                        self.tmpLog.append(totalAsset)
                        self.tmpLog.append(self.DfFitness.iloc[IndividualCount]['capital'] + self.DfFitness.iloc[IndividualCount]['profit'] + self.DfFitness.iloc[IndividualCount]['riskfree'] - self.DfFitness.iloc[IndividualCount]['cost'] - self.DfFitness.iloc[IndividualCount]['deposit'])
                        self.tmpLog.append(self.DfFitness.iloc[IndividualCount]['lastTradeValue'])
                        self.TradeLog.append(self.tmpLog) 
                        self.tmpLog=[]
                        self.tmpLog.append(index)
                        self.tmpLog.append('Yes')
                    self.DfFitness.iloc[IndividualCount]['holding'] = 0
                else:
                    if IndividualCount == 0:
                        self.tmpLog.append('No')

            #Calculate holding
            TmpDfFitness['holding'] = (((self.DfFitness['capital'] + self.DfFitness['profit'] - self.DfFitness['deposit']- self.DfFitness['cost']) /5000)* self.DfRlevel).round()#Easier way#(df.High[index] * self.Deposit))* self.DfRlevel).round()
            #Calculate Profit and cost since it is affected by buy or sell option.
            flag =np.zeros(20)
            for IndividualCount in range(0,20):           
                HoldingDiff = self.DfFitness.iloc[IndividualCount]['holding'] - TmpDfFitness.iloc[IndividualCount]['holding']
                currentTradePrice=0
                if HoldingDiff < 0:#this means buy,HoldingDiff is negative.
                    currentTradePrice = df.High[index]
                else:
                    currentTradePrice = df.Low[index]
               
                TmpDfFitness.iloc[IndividualCount]['cost'] =  max((abs(HoldingDiff) * currentTradePrice * 0.002),self.minTradeCost)
                #if suggest holding change sign from previous, it is same as close position first then acuire holding for opposite position.
                if self.DfFitness.iloc[IndividualCount]['holding'] != 0:
                    if (TmpDfFitness.iloc[IndividualCount]['holding'] == 0) or ((TmpDfFitness.iloc[IndividualCount]['holding'] * self.DfFitness.iloc[IndividualCount]['holding']) < 0):
                        #close previous position
                        TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.iloc[IndividualCount]['profit'] + self.DfFitness.iloc[IndividualCount]['holding'] * (currentTradePrice  - self.DfFitness.iloc[IndividualCount]['lastTradeValue'])
                        TmpDfFitness.iloc[IndividualCount]['lastTradeValue'] =  currentTradePrice
                        flag[IndividualCount]=1
                    else:
                        #calculate profit if holding has same sign
                        if abs(TmpDfFitness.iloc[IndividualCount]['holding']) < abs(self.DfFitness.iloc[IndividualCount]['holding']):
                            TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.iloc[IndividualCount]['profit'] + HoldingDiff *(currentTradePrice  - self.DfFitness.iloc[IndividualCount]['lastTradeValue'] )
                            TmpDfFitness.iloc[IndividualCount]['lastTradeValue'] = self.DfFitness.iloc[IndividualCount]['lastTradeValue']
                            flag[IndividualCount]=2
                        else:
                            TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.iloc[IndividualCount]['profit']
                            TmpDfFitness.iloc[IndividualCount]['lastTradeValue'] =  (abs(self.DfFitness.iloc[IndividualCount]['holding']) * self.DfFitness.iloc[IndividualCount]['lastTradeValue'] + abs(HoldingDiff) * currentTradePrice) / abs(TmpDfFitness.iloc[IndividualCount]['holding'])
                            flag[IndividualCount] =3
                else:
                    TmpDfFitness.iloc[IndividualCount]['lastTradeValue'] =  currentTradePrice
                    TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.iloc[IndividualCount]['profit']
                    flag[IndividualCount]=4
                #calculate deposit
                TmpDfFitness.iloc[IndividualCount]['deposit'] = abs(TmpDfFitness.iloc[IndividualCount]['holding']) * 5000#Use easier way#TmpDfFitness.iloc[IndividualCount]['lastTradeValue'] * self.Deposit
            #calculate risk-free
            TmpDfFitness['riskfree'] = self.DfFitness.riskfree
            #accumulate costs
            TmpDfFitness['cost'] = self.DfFitness.cost + TmpDfFitness.cost 
            for IndividualCount in range(0,20):#Check through criteria and see if no need to trade at this index
                if ((not self.IsFirstGroup) or index != self.StartIndex):
                    if self.TradeOnIntersection:
                        if (self.CrossFlag[IndividualCount] >= 0) or(self.DfFitness.capital[IndividualCount] + TmpDfFitness.profit[IndividualCount] - TmpDfFitness.deposit[IndividualCount] - TmpDfFitness.cost[IndividualCount]< 0):
                            TmpDfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','deposit','lastTradeValue']]=self.DfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','deposit','lastTradeValue']]
                    else:
                        if (self.DfFitness.capital[IndividualCount] + TmpDfFitness.profit[IndividualCount] - TmpDfFitness.deposit[IndividualCount] - TmpDfFitness.cost[IndividualCount]< 0):
                            TmpDfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','deposit','lastTradeValue']]=self.DfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','deposit','lastTradeValue']]    
                else:
                    if (self.DfFitness.capital[IndividualCount] + TmpDfFitness.profit[IndividualCount] - TmpDfFitness.deposit[IndividualCount] - TmpDfFitness.cost[IndividualCount] < 0):
                        TmpDfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','deposit','lastTradeValue']]=self.DfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','deposit','lastTradeValue']]
            self.DfFitness = TmpDfFitness[['capital','profit','holding','cost','riskfree','deposit','lastTradeValue']]
            self.tmpLog.append(self.DfFitness.profit[0])
            #calculate riskFree
            self.DfFitness.riskfree += self.rfrate * (self.DfFitness.capital - self.DfFitness.deposit + self.DfFitness.profit + self.DfFitness.riskfree - self.DfFitness.cost ) / 365
            
            #Log and plot part
            self.tmpLog.append(self.DfFitness.holding[0])
            self.tmpLog.append(self.DfFitness.deposit[0])
            self.tmpLog.append(self.DfFitness.riskfree[0])
            self.tmpLog.append(self.DfFitness.cost[0])
            closeProfit=0
            if self.DfFitness.holding[0] > 0:
                closeProfit = 25 *self.DfFitness.iloc[0]['holding'] * (df.Low[index]  - self.DfFitness.iloc[0]['lastTradeValue'])
            else:
                closeProfit = 25 *self.DfFitness.iloc[0]['holding'] * (df.High[index]  - self.DfFitness.iloc[0]['lastTradeValue'])
            totalAsset= self.DfFitness.capital[0] + self.DfFitness.profit[0] + self.DfFitness.riskfree[0] - self.DfFitness.cost[0]+closeProfit
            self.tmpLog.append(closeProfit)
            self.tmpLog.append(totalAsset)
            self.tmpLog.append(self.DfFitness.capital[0] + self.DfFitness.profit[0] + self.DfFitness.riskfree[0] - self.DfFitness.cost[0] - self.DfFitness.deposit[0])
            self.tmpLog.append(self.DfFitness.lastTradeValue[0])
            self.TradeLog.append(self.tmpLog)
            
            self.tmpPlot.append(self.CrossFlag[0]*100)
            self.tmpPlot.append(self.DfFitness.holding[0])
            self.tmpPlot.append(df.Date[index])
            self.ForPlot.append(self.tmpPlot)
            
        self.HoldingPlot = pd.DataFrame(self.ForPlot,columns=['index','prince','intersect','holding','date'])
        self.TRlog = pd.DataFrame(self.TradeLog,columns=['index','Close out','Profit','Holding','Deposit','riskfree','cost','closeProfit','totalAsset','Cash','price on hand'])
        if PlotHolding:
            self.HoldingPlot.set_index('index').plot(y=['intersect','holding'],figsize=(10,5), grid=True)
            savefile = "HoldingPlot" + str(index)   # file might need to be replaced by a string
            plt.savefig(savefile+ '.png' )       
            plt.show()

            writer = pd.ExcelWriter(os.path.join('',savefile+'.xlsx'), engine='xlsxwriter')
            self.TRlog.to_excel(writer)
            writer.save()
            
            
    def getRreturn(self,df):
        tmpProfit = self.DfFitness.loc[:, ['profit']]
        for IndividualCount in range(0,20):  
            if self.DfFitness.holding[IndividualCount] > 0:
                tmpProfit.iloc[IndividualCount]['profit'] += 25 * self.DfFitness.iloc[IndividualCount]['holding'] * (df.Low[self.EndIndex]  - self.DfFitness.iloc[IndividualCount]['lastTradeValue'])
            else:
                tmpProfit.iloc[IndividualCount]['profit'] += 25 *self.DfFitness.iloc[IndividualCount]['holding'] * (df.High[self.EndIndex]  - self.DfFitness.iloc[IndividualCount]['lastTradeValue'])
        return ((self.DfFitness.profit + self.DfFitness.riskfree - self.DfFitness.cost  )/self.DfFitness.capital)
    
    def getTotalAsset(self,df):
        closeProfit=0
        if self.DfFitness.holding[0] > 0:
            closeProfit = 25 *self.DfFitness.iloc[0]['holding'] * (df.Low[self.EndIndex]  - self.DfFitness.iloc[0]['lastTradeValue'])
        else:
            closeProfit = 25 *self.DfFitness.iloc[0]['holding'] * (df.High[self.EndIndex]  - self.DfFitness.iloc[0]['lastTradeValue'])
        totalAsset= self.DfFitness.capital + self.DfFitness.profit + self.DfFitness.riskfree - self.DfFitness.cost 
        print("Total asset is :",totalAsset[0]+closeProfit)
        return totalAsset[0]+closeProfit

    def getAccountStatus(self):
        return self.DfFitness.loc[0, :].values.tolist()
    