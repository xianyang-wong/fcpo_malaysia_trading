Collection = [[[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.3],[1,20,5,3,0.3]],
              [[0,10,3,2,-0.4],[1,20,5,3,0.4]]]
#pd.set_option('display.float_format', lambda x: '%.3f' % x)
class FitnessFunction:
    DfFitness = pd.DataFrame(np.array([1000000.0,0,0,0,0,0]*20).reshape(20,6),columns=['capital','profit','holding','cost','riskfree','rreturn'])
    
    #rule:{a,b,c,d,e} a:MA 0-3 ,b:m {10,20,50100,150,200}, c:n {1,3,5,10,15,20} ,d:membership 0-6, e:recommand [-1, 1]
    InitialCapital=1000000
    #initial capital
    StartIndex = 20
    #starting index of calculation
    EndIndex=21
    #end index
   
    Deposit = 0.15
    #Holding   Deposit
    rfrate = 0.02
    #risk free return

    #caculate moving average at give index, will call SeeTing function ,here use SMA instead.
    def MA_Diff(m,n,index):#SMA as demo
        mRange = df.iloc[index-m:index]
        nRange = df.iloc[index-n:index]
        return nRange['Open'].mean() - mRange['Open'].mean()

    def Average(list):
        return sum(list)/len(list)

    def __init__(self):
        floglic = FuzzyLogic(2014)
        #initialize FuzzyLogic module
       
        #calculate rlevel for each individual,20 in total
        rlevelList=[]
        for ruleSet in Collection:
            tmpList=[]
            for rule in ruleSet:
                MAd = MA_Diff(rule[1],rule[2],Index)
                recommandValue = floglic.ComputeMembership(MAd,rule[1],rule[2],rule[0],rule[3]) 
                if(recommandValue >= 0):
                    tmpList.append(recommandValue* rule[4])
                    rlevelList.append(Average(tmpList))
        self.DfRlevel = pd.DataFrame(rlevelList)

        for index in range(self.StartIndex, self.EndIndex):
            TmpDfFitness = pd.DataFrame(np.array([0.0,0,0,0,0,0,30]*20).reshape(20,7),columns=['capital','profit','holding','cost','riskfree','rreturn','MinCost'])
            #store buffer

            #Calculate Holding
            TmpDfFitness['holding'] = (self.DfFitness.capital /(df.iloc[index]['High'] * Deposit))* self.DfRlevel
            #Calculate Profit and cost since it is affected by buy or sell option.
            for IndividualCount in range(0,20):
                HoldingDiff = self.DfFitness.iloc[IndividualCount]['holding'] - TmpDfFitness.iloc[IndividualCount]['holding']
                if HoldingDiff < 0:#this means buy
                    TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.profit[IndividualCount]+ df.iloc[index]['High'] * HoldingDiff
                    #calculate Cost
                    TmpDfFitness.iloc[IndividualCount]['cost'] = abs(HoldingDiff) * df.iloc[index]['High'] * 0.002
                else:
                    TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.profit[IndividualCount]+ df.iloc[index]['Low'] * HoldingDiff
                    #calculate Cost
                    TmpDfFitness.iloc[IndividualCount]['cost'] =  abs(HoldingDiff) * df.iloc[index]['Low'] * 0.002
            TmpDfFitness['cost'] = TmpDfFitness[['cost', 'MinCost']].max(axis=1)
            #calculate riskFree
            TmpDfFitness['riskfree'] = self.DfFitness.riskfree + self.rfrate * (self.InitialCapital - df.iloc[index]['Open'] * self.Deposit * TmpDfFitness['holding'].abs() )
            #calculate current capital
            print(TmpDfFitness['capital'])
            TmpDfFitness['capital'] = self.DfFitness.capital + TmpDfFitness.riskfree - TmpDfFitness.cost + TmpDfFitness.profit
            print(TmpDfFitness['capital'])
            #accumulate costs
            TmpDfFitness['cost'] = self.DfFitness.cost + TmpDfFitness.cost 
            for IndividualCount in range(0,20):#do not trade if no capital
                if TmpDfFitness.iloc[IndividualCount]['capital'] < 0:
                    TmpDfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','rreturn']]=self.DfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','rreturn']]
            self.DfFitness = TmpDfFitness[['capital','profit','holding','cost','riskfree','rreturn']]
            print(TmpDfFitness['capital'])

        
    def getRreturn(self):
        return (self.DfFitness.profit + self.DfFitness.riskfree -self.DfFitness.cost)/self.InitialCapital
    
    def getTotalAsset(self):
        return self.DfFitness.capital + self.DfFitness.holding * df.iloc[EndIndex]['Low']
        
#FF =FitnessFunction()
#FF.getRreturn()
#FF.getTotalAsset()
