
##----------------- Helper Functions-----------------------##

def smafunc(startindex, endindex, period, df):
    
    lst = list(df[startindex:endindex])
    sma = []
    count = 0

    while count + period <= endindex-startindex:
        start = count
        end = count + period
        sma += [sum(lst[start:end])/period,]
        count += 1
        
    return sma       
        
def tmafunc(startindex, endindex, period, df):
    
    if startindex < period:
        new_startindex = 0
    else:
        new_startindex = startindex - period + 1

    lst = smafunc(startindex, endindex, period, df)
    tma= []
    count = 0

    while count + period <= len(lst):
        start = count
        end = count + period
        tma += [sum(lst[start:end])/period,]
        count += 1
        
    return tma

def tpmafunc(startindex, endindex, period, df):

    lst = list(df[startindex:endindex])
    tpma = []
    count = 0

    while count + period <= endindex - startindex:
        start = count
        end = count + period
        temp_lst = list(lst[start:end])
        max_price = max(temp_lst)
        min_price = min(temp_lst)
        close_price = temp_lst[0]
        tpma += [(max_price + min_price + close_price)/3,]
        count += 1
        
    return tpma

def amafunc(startindex, endindex, period, df):
    
    lst = list(df[startindex:endindex])
    ini_ama = sum(lst[:period])/period
    ama = [ini_ama,]
    count = 0
    fastSC = 2/(1 + 2)
    slowSC = 2/(1 + 30)

    while count + period < endindex - startindex:

        start = count
        end = count + period
        signal = abs(lst[end] - lst[start+1])
        i = start
        noise = 0

        while i < end:
            noise += abs(lst[i+1]-lst[i])
            i += 1

        ER_k = signal / noise
        SSC_k = ER_k * (fastSC - slowSC) + slowSC
        ama += [ama[count] + (SSC_k**2)*(lst[end]-ama[count]),]
        count += 1

    return ama

##-------------------------------------------------------------##

# Main Function

def computeMA(typeMA, startindex, endindex, period, df):

    if startindex <= period:
        new_startindex = 0
    else:
        new_startindex = startindex - period

    if typeMA == 0:
        return smafunc(new_startindex, endindex, period, df)
    elif typeMA == 1:
        return tmafunc(new_startindex, endindex, period, df)
    elif typeMA == 2:
        return tpmafunc(new_startindex, endindex, period, df)
    elif typeMA == 3:
        return amafunc(new_startindex, endindex, period, df)
    else:
        return []

## Test Cases
#print(smafunc(0, 10, 5))
#print(tmafunc(0, 10, 5))
#print(tpmafunc(0, 10, 5))
#print(amafunc(0, 10, 5))
#print(computeMA('sma',0, 10, 5))
