System Requirement
1) Python 3.7

Package Included
1) Numpy
2) sklearn
3) pandas
4) matplotlib
5) itertools

Files.
1) controller_rearrange.py
2) FitnessFunction.py
3) Fuzzy_Logic.py
4) genetic_alog.py
5) MA_components.py

To start the simulator, 
Run controller_rearrange.py

Options.
1)Trade by day or intersection.
In controller_rearrange.py, line 28.
Set TradeWhenIntersection = True or False

2) Clustering
To turn on clustering,in controller_rearrange.py, line 96
Change to setting to 
flogic = fuzzy.FuzzyLogic(y1, y3, parsed.loc[:, :], True, False)

To turn off clustering,in controller_rearrange.py, line 96
Change to setting to 
flogic = fuzzy.FuzzyLogic(y1, y3, parsed.loc[:, :], False, False)

3) Different Moving Average for long and short period
To use different MA, 
in controller_rearrange.py, line 67, set parameter to "different"
in controller_rearrange.py, line 96 set parameter to flogic = fuzzy.FuzzyLogic(y1, y3, parsed.loc[:, :], False, True)

To use same MA, 
in controller_rearrange.py, line 67, set parameter to "same"
in controller_rearrange.py, line 96 set parameter to flogic = fuzzy.FuzzyLogic(y1, y3, parsed.loc[:, :], False, False

