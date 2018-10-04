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
import Fuzzy_Logic as fuzzy
import MA_components as maComp
class FitnessFunction:
    DfFitness = pd.DataFrame(np.array([1000000.0,0,0,0,0,0]*20).reshape(20,6),columns=['capital','profit','holding','cost','riskfree','deposit'])
    
    #rule:{a,b,c,d,e} a:MA 0-3 ,b:m {10,20,50100,150,200}, c:n {1,3,5,10,15,20} ,d:membership 0-6, e:recommand [-1, 1]
    InitialCapital=1000000
    #initial capital
    StartIndex = 20
    #starting index of calculation
    EndIndex= 22
    #end index
   
    Deposit = 0.15
    #Holding   Deposit
    rfrate = 0.02
    #risk free return

    #caculate moving average at give index, will call SeeTing function ,here use SMA instead.
    def MA_Diff(self,MAType,m,n,index):#SMA as demo
        mValues = maComp.computeMA(MAType, int(index), int(index), m, self.df)
        nValues = maComp.computeMA(MAType, int(index), int(index), n, self.df)
        v =  np.subtract(mValues, nValues)
        return v[0]

    def Average(self,list):
        return sum(list)/len(list)

    def __init__(self,s0,s1,s2,s3,df):
        self.StartIndex = s0
        self.EndIndex = s1
        self.df = df
        floglic = fuzzy.FuzzyLogic(self.StartIndex, self.EndIndex,df)
        
        for index in range(self.StartIndex, self.EndIndex):
             #calculate rlevel for each individual,20 in total
            rlevelList=[]
            for ruleSet in Collection:
                tmpList=[]
                for rule in ruleSet:
                    MAd = self.MA_Diff(0,rule[1],rule[2],index)
                    print(MAd)
                    recommandValue = floglic.ComputeMembership(MAd,int(rule[1]),int(rule[2]),int(rule[0]),int(rule[3]))
                    print(rule)
                    print(recommandValue)
                    if recommandValue >= 0:
                        tmpList.append(recommandValue* rule[4])
                print(tmpList)
                rlevelList.append(self.Average(tmpList))
            self.DfRlevel = pd.DataFrame(rlevelList)
            TmpDfFitness = pd.DataFrame(np.array([0.0,0,0,0,0,0,30]*20).reshape(20,7),columns=['capital','profit','holding','cost','riskfree','deposit','MinCost'])
            #store buffer

            #Calculate Holding,if reaching the end of session, sell all holdings to cash out.
            if index != self.EndIndex-1:
                TmpDfFitness['holding'] = (self.DfFitness.capital /(df.iloc[index]['High'] * self.Deposit))* self.DfRlevel
            #Calculate Profit and cost since it is affected by buy or sell option.
            for IndividualCount in range(0,20):
                HoldingDiff = self.DfFitness.iloc[IndividualCount]['holding'] - TmpDfFitness.iloc[IndividualCount]['holding']
                if HoldingDiff < 0:#this means buy
                    if IndividualCount == self.StartIndex:# if this is the first transation, calculate profit differently(subtract from the rest)
                        TmpDfFitness.iloc[IndividualCount]['profit'] = df.iloc[index]['High'] * TmpDfFitness.iloc[IndividualCount]['holding'] * -1
                    else:
                        TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.profit[IndividualCount]+ df.iloc[index]['High'] * HoldingDiff
                    #calculate Cost
                    TmpDfFitness.iloc[IndividualCount]['cost'] = abs(HoldingDiff) * df.iloc[index]['High'] * 0.002
                    #calculate deposit
                    TmpDfFitness.deposit[IndividualCount] = self.DfFitness.deposit[IndividualCount] + HoldingDiff * df.iloc[index]['High'] * self.Deposit * -1
                    #calculate Capital
                    TmpDfFitness.capital[IndividualCount] = self.DfFitness.capital[IndividualCount] + HoldingDiff * df.iloc[index]['High'] * self.Deposit
                else:
                    if IndividualCount == self.StartIndex:
                        TmpDfFitness.iloc[IndividualCount]['profit'] = df.iloc[index]['Low'] * TmpDfFitness.iloc[IndividualCount]['holding'] * -1
                    else:
                        TmpDfFitness.iloc[IndividualCount]['profit'] = self.DfFitness.profit[IndividualCount]+ df.iloc[index]['Low'] * HoldingDiff
                    #calculate Cost
                    TmpDfFitness.iloc[IndividualCount]['cost'] =  abs(HoldingDiff) * df.iloc[index]['Low'] * 0.002
                     #calculate deposit
                    TmpDfFitness.deposit[IndividualCount] = self.DfFitness.deposit[IndividualCount] + HoldingDiff * df.iloc[index]['Low'] * self.Deposit * -1
                    #calculate Capital
                    TmpDfFitness.capital[IndividualCount] = self.DfFitness.capital[IndividualCount] + HoldingDiff * df.iloc[index]['Low'] * self.Deposit + HoldingDiff * (df.iloc[index]['Low']- df.iloc[index-1]['Low'])
            TmpDfFitness['cost'] = TmpDfFitness[['cost', 'MinCost']].max(axis=1)
            #calculate riskFree
            TmpDfFitness['riskfree'] = self.DfFitness.riskfree + self.rfrate * (self.InitialCapital - df.iloc[index]['High'] * self.Deposit * TmpDfFitness['holding'].abs() )
            #calculate current capital
            TmpDfFitness['capital'] = TmpDfFitness.capital + TmpDfFitness.riskfree - TmpDfFitness.cost
            #accumulate costs
            TmpDfFitness['cost'] = self.DfFitness.cost + TmpDfFitness.cost 
            for IndividualCount in range(0,20):#do not trade if no capital
                if TmpDfFitness.iloc[IndividualCount]['capital'] < 0:
                    TmpDfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','deposit']]=self.DfFitness.loc[IndividualCount:IndividualCount,['capital','profit','holding','cost','riskfree','rreturn']]
            self.DfFitness = TmpDfFitness[['capital','profit','holding','cost','riskfree','deposit']]


        
    def getRreturn(self):
        print(self.DfFitness)
        print((self.DfFitness.profit + self.DfFitness.riskfree - self.DfFitness.cost)/self.InitialCapital)
    
    def getTotalAsset(self):
        print(self.DfFitness.capital + self.DfFitness.deposit)
        
FF =FitnessFunction(200,5200,34,43,df)
FF.getRreturn()
FF.getTotalAsset()
