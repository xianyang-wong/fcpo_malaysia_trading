##---------------- Memo Table ----------------------------##

memo={'sma':{},
      'tma':{},
      'tpma':{},
      'ama':{}}

##----------------- Helper Functions-----------------------##

def smafunc(period, lst):
    
    count = 0
    memo['sma'][period] = []
    
    while count + period <= len(lst):
        start = count
        end = count + period
        memo['sma'][period] += [sum(lst[start:end])/period,]
        count += 1

        
def tmafunc(period):

    lst = memo['sma'][period]
    count = 0
    memo['tma'][period] = []
    
    while count + period <= len(lst):
        start = count
        end = count + period
        memo['tma'][period] += [sum(lst[start:end])/period,]
        count += 1

def tpmafunc(period, lst):
    
    memo['tpma'][period] = []
    count = 0

    while count + period <= len(lst):
        start = count
        end = count + period
        temp_lst = list(lst[start:end])
        max_price = max(temp_lst)
        min_price = min(temp_lst)
        close_price = temp_lst[0]
        memo['tpma'][period] += [(max_price + min_price + close_price)/3,]
        count += 1

def amafunc(period, lst):
    
    ini_ama = sum(lst[:period])/period
        
    memo['ama'][period] = [ini_ama,]
    fastSC = 2/(1 + 2)
    slowSC = 2/(1 + 30)

    k_1 = period 
    k_n = 1
    k = 1

    while k_1 < len(lst):
        signal = abs(lst[k_1] - lst[k_n])
        i = k_n
        noise = 0

        while i <= k_1:
            noise += abs(lst[i]-lst[i-1])
            i += 1

        if noise == 0:
            ER_k = 0
        else:
            ER_k = signal / noise
            
        SSC_k = ER_k * (fastSC - slowSC) + slowSC
        ama_k_1 = memo['ama'][period][k - 1] 
        memo['ama'][period] += [ama_k_1 + (SSC_k**2)*(lst[k - 1]-ama_k_1),]
        k_1 += 1
        k_n += 1
        k += 1


##-------------------------------------------------------------##

# Main Function

def computeMA(typeMA, startindex, endindex, period, df):

    if memo['sma']== {}:
        initialisation(list(df['Close']))


    if startindex <= period:
        start = startindex
        end = endindex + 1
    else:
        start = startindex - period
        end = endindex + 1 - period

    if typeMA == 0:
        return memo['sma'][period][start:end]
    elif typeMA == 1:
        return memo['tma'][period][start:end]
    elif typeMA == 2:
        return memo['tpma'][period][start:end]
    elif typeMA == 3:
        return memo['ama'][period][start:end]
    else:
        return []
    
# initialised the computation for memo table
def initialisation(lst):
    mn = [1,3,5,10,15,20,50,100,150,200]
    
    for ele in mn:
        smafunc(ele,lst)
        tmafunc(ele)
        tpmafunc(ele,lst)
        amafunc(ele,lst)
        

## Test Cases
#print(smafunc(0, 10, 5))
#print(tmafunc(0, 10, 5))
#print(tpmafunc(0, 10, 5))
#print(amafunc(0, 10, 5))
#print(computeMA('sma',0, 10, 5))
