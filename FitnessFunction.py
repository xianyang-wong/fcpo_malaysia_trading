import pandas as pd
import MA_components as maComp
import numpy as np
import matplotlib.pyplot as plt

pd.set_option('display.float_format', lambda x: '%.3f' % x)

class FitnessFunction:
    InitialCapital=10000000
    #initial capital
   
    Deposit = 0.15
    #Holding   Deposit
    rfrate = 0.02
    #risk free return,year rate

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
    #ClosePosition takes 'True','False', indicate if the program close the position at the end.
    #PlotHolding if 'True' will plot Hoding,Intersection,price against index
    def __init__(self,s0,s1,df,Collection,flogic,ListInitialState,ClosePosition,PlotHolding):
        self.fuzzylogic = flogic
        self.DfFitness = pd.DataFrame(np.array(ListInitialState*20).reshape(20,6),columns=['capital','profit','holding','cost','riskfree','deposit'])
        self.StartIndex = s0
        self.EndIndex = s1
        self.DailyFirstIndex = s0
        self.LastMA=np.zeros(20)
        self.ClosePosition = ClosePosition
        self.PlotHolding = PlotHolding
        self.ForPlot=[]
        for index in range(self.StartIndex, self.EndIndex):
            #prepare data for plotting
            self.tmpPlot=[]
            self.tmpPlot.append(index)
            self.tmpPlot.append(df.High[index])
            
            if df.Flag[index] == 1:
                self.DailyFirstIndex = index
             #calculate rlevel for each individual,20 in total
            rlevelList=[]
            MA_List=[]
            for ruleSet in Collection:
                tmpList=[]
                tmpMA=[]
                for rule in ruleSet:#rule:{a,b,c,d,e} a:MA [m type,n type] ,b:m {10,20,50100,150,200}, c:n {1,3,5,10,15,20} ,d:membership 0-6, e:recommand [-1, 1]
                    MAd = self.MA_Diff(rule[0],rule[1][1],rule[1][0],index,df)
                    recommandValue = self.fuzzylogic.ComputeMembership(MAd,int(rule[1][1]),int(rule[1][0]),int(rule[0][0]),int(rule[2]),int(rule[0][1]))
                    if recommandValue >= 0:#result will not be taken into account if recommandValue below 0
                        tmpList.append(recommandValue* rule[3])
                    tmpMA.append(MAd)
                rlevelList.append(self.Average(tmpList))
                MA_List.append(self.Average(tmpMA))
            self.DfRlevel = pd.DataFrame(rlevelList)#Dataframe that stores rlevel values for all 20 individuals
            #CrossFlag is used to determin if intersection happens.Possitive means no and Negative means intersection happens.
            self.CrossFlag = (np.multiply(np.asarray(MA_List),self.LastMA)).tolist()
            self.LastMA = np.asarray(MA_List)
            #if the ruleset only contain 1 rule then need to pad CrossFlag to 20 elements. then use sign to remove values just keep sign
            self.CrossFlag = np.sign(np.pad(self.CrossFlag, (0,(20 - len(self.CrossFlag))), 'constant', constant_values=(0, 0)))

            TmpDfFitness = pd.DataFrame(np.array([0.0,0,0,0,0,0,30]*20).reshape(20,7),columns=['capital','profit','holding','cost','riskfree','deposit','MinCost'])
            #Dataframe stores valeus to calculate fitness function at current moment.

            #Calculate Holding,if reaching the end of session and required to close position,clear holdings to cash out.
            if index == (self.EndIndex-1) and self.ClosePosition:
                TmpDfFitness['holding'] = 0
            else:
                TmpDfFitness['holding'] = ((self.InitialCapital - self.DfFitness['deposit']) /(df.High[index] * self.Deposit))* self.DfRlevel
            
            #Calculate Profit and cost since it is affected by buy or sell option.
            for IndividualCount in range(0,20):
                # to save time ,if this timing is not intersection, skip
                if (self.CrossFlag[IndividualCount] >= 0):
                    continue
                HoldingDiff = self.DfFitness.iloc[IndividualCount]['holding'] - TmpDfFitness.iloc[IndividualCount]['holding']
                if HoldingDiff < 0:#this means buy,HoldingDiff is negative.
                    if IndividualCount == self.StartIndex:# if this is the first transation, calculate profit differently(subtract from the rest)
                        TmpDfFitness.iloc[IndividualCount]['profit'] = df.High[index] * TmpDfFitness.iloc[IndividualCount]['holding'] * -1
                    else:
                        TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.profit[IndividualCount]+ df.High[index] * HoldingDiff
                    #calculate Cost
                    TmpDfFitness.iloc[IndividualCount]['cost'] = abs(HoldingDiff) * df.High[index] * 0.002
                    #calculate Capital
                    #TmpDfFitness.capital[IndividualCount] = self.DfFitness.capital[IndividualCount] + HoldingDiff * df.iloc[index]['High'] * self.Deposit
                else:
                    if IndividualCount == self.StartIndex:
                        TmpDfFitness.iloc[IndividualCount]['profit'] = df.Low[index] * TmpDfFitness.iloc[IndividualCount]['holding'] * -1
                    else:
                        TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.profit[IndividualCount]+ df.Low[index] * HoldingDiff
                    #calculate Cost
                    TmpDfFitness.iloc[IndividualCount]['cost'] =  abs(HoldingDiff) * df.Low[index] * 0.002  
            TmpDfFitness['deposit'] = abs(TmpDfFitness['holding']) * df.High[index] * self.Deposit
            #calculate deposit
            TmpDfFitness['cost'] = TmpDfFitness[['cost', 'MinCost']].max(axis=1)
            #calculate risk-free
            TmpDfFitness['riskfree'] = self.DfFitness.riskfree
            #accumulate costs
            TmpDfFitness['cost'] = self.DfFitness.cost + TmpDfFitness.cost 
            for IndividualCount in range(0,20):#do not trade if no capital or no intersection
                if ((self.InitialCapital + TmpDfFitness.profit[IndividualCount] - TmpDfFitness.deposit[IndividualCount] < 0) or (self.CrossFlag[IndividualCount] >= 0)) and ((index != self.EndIndex-1) or not self.ClosePosition):
                    #print("No money on individual ",IndividualCount)
                    TmpDfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','deposit']]=self.DfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','deposit']]
            self.DfFitness = TmpDfFitness[['capital','profit','holding','cost','riskfree','deposit']]
            if df.Flag[index] == 2:# clear daily holding profit
                self.DfFitness.profit += self.DfFitness.holding * (df.Open[index] - df.Open[self.DailyFirstIndex])
                #calculate riskFree
                self.DfFitness.riskfree += self.rfrate * (self.InitialCapital - self.DfFitness.deposit + self.DfFitness.profit  ) / 365
            self.tmpPlot.append(self.CrossFlag[0]*100)
            self.tmpPlot.append(self.DfFitness.holding[0])
            self.ForPlot.append(self.tmpPlot)
        self.HoldingPlot = pd.DataFrame(self.ForPlot,columns=['index','prince','intersect','holding'])
        if PlotHolding:
            self.HoldingPlot.set_index('index').plot(y=['intersect','holding'],figsize=(10,5), grid=True)
            savefile = "HoldingPlot" + str(index) + '.png'   # file might need to be replaced by a string
            plt.savefig(savefile)       
            plt.show()
            #print(self.HoldingPlot)
            #print("here comes plot")
    def getRreturn(self,df):
        return ((self.DfFitness.profit + self.DfFitness.riskfree - self.DfFitness.cost  + (self.DfFitness.holding * df.High[self.EndIndex]) )/self.InitialCapital)
    
    def getTotalAsset(self,df):
        totalAsset= self.InitialCapital + self.DfFitness.profit + self.DfFitness.riskfree - self.DfFitness.cost + (self.DfFitness.holding * df.High[self.EndIndex])
        print(self.DfFitness)
        print("Total asset is :",totalAsset[0])
        return totalAsset[0]

    def getAccountStatus(self):
        return self.DfFitness.loc[0, :].values.tolist()