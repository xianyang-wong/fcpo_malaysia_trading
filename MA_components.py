
##----------------- Helper Functions-----------------------##

def smafunc(startindex, endindex, period, df):
    
    lst = df[startindex:endindex]
    sma = []
    count = startindex
    
    while count + period < endindex:
        start = count
        end = count + period
        sma += [sum(lst[start:end])/period,]
        count += 1
        
    return sma        
        
def tmafunc(startindex, endindex, period, df):

    lst = smafunc(startindex, endindex, period, df)
    tma= []
    count = startindex

    while count + period < len(lst):
        start = count
        end = count + period
        tma += [sum(lst[start:end])/period,]
        count += 1
        
    return tma

def tpmafunc(startindex, endindex, period, df):

    lst = df[startindex:endindex]
    tpma = []
    count = startindex

    while count + period < endindex:
        start = count
        end = count + period
        _lst = lst[start:end]
        max_price = max(_lst)
        min_price = min(_lst)
        close_price = _lst[count]
        tpma += [(max_price + min_price + close_price)/3,]
        count += 1
        
    return tpma

def amafunc(startindex, endindex, period, df):
    
    lst = df[startindex:endindex]
    ini_ama = sum(lst[:period])/period
    ama = [ini_ama,]
    count = startindex
    fastSC = 2/(1 + 2)
    slowSC = 2/(1 + 30)

    while count + period < endindex:

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

    if typeMA == 'sma':
        return smafunc(startindex, endindex, period, df)
    elif typeMA == 'tma':
        return tmafunc(startindex, endindex, period, df)
    elif typeMA == 'tpma':
        return tpmafunc(startindex, endindex, period, df)
    elif typeMA == 'ama':
        return amafunc(startindex, endindex, period, df)
    else:
        return []

## Test Cases
#print(smafunc(0, 10, 5))
#print(tmafunc(0, 10, 5))
#print(tpmafunc(0, 10, 5))
#print(amafunc(0, 10, 5))
#print(computeMA('sma',0, 10, 5))
