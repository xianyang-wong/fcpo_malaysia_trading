import pandas as pd
import numpy as np

parsedByDay = pd.read_excel(os.path.join(directory,'data/FCPO_6_years_NUS_ParsedByDay.xlsx'))

holdingplot936 = pd.read_excel(os.path.join(directory,'HoldingPlot936.xlsx'))
parsedByDay936 = parsedByDay.iloc[holdingplot936['index'],:]

writer = pd.ExcelWriter(os.path.join(directory,'check_files/parsedByDay936.xlsx'), engine='xlsxwriter')
parsedByDay936.to_excel(writer)
writer.save()

check = pd.concat([parsedByDay936.reset_index(drop=True), holdingplot936.reset_index(drop=True)], axis=1)

writer = pd.ExcelWriter(os.path.join(directory,'data/check_file.xlsx'), engine='xlsxwriter')
check.to_excel(writer)
writer.save()




