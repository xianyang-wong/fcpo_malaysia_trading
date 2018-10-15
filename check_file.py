import pandas as pd
import numpy as np
import os
import datetime as dt

trade_signals = pd.read_excel('C:/Users/XY/Desktop/fcpo_malaysia_trading/HoldingPlot936.xlsx')
trade_signals['trade_flag'] = 1

daily = pd.read_excel('C:/Users/XY/Desktop/fcpo_malaysia_trading/data/FCPO_6_years_NUS_ParsedByDay.xlsx')
daily1415 = daily[daily['Date'].dt.year.isin([2014])].reset_index()

daily1415 = daily1415.merge(trade_signals[['Date','trade_flag']],
                            how='left',
                            left_on='Date',
                            right_on='Date').reset_index().fillna(0)

for day in range(0,daily1415.shape[0]):
    if day == 0:
        current_status = [0, 0, 0, 10000000]  # [holding, initial holding price,deposit, cash]
    """"""
    # NEED TO ADD
    # everyday check if got short position
    # if there is pay interest on short position
    # adjust short holdings such that total marked to market value is maximum of RM 5million
    """"""

    if daily1415['trade_flag'][day]==1:
        trade_signal_holding = trade_signals['Holding'][trade_signals['Date'] == daily1415['Date'][day]]

        """"""
        # NEED TO ADD
        # check that directions of holdings are the same
        # if not need to close out current holdings position
        # then carry out trade
        if :

        else:
            change_in_position = np.abs(trade_signal_holding - current_status[0])
        """"""
        """"""
        # NEED TO ADD
        # cost of trade if long
        # deposit if long
        """"""
        """"""
        # NEED TO ADD
        # cost of trade if short
        # deposit if short
        """"""

        """"""
        # NEED TO ADD
        # update cash position
        """"""
        """"""
        # NEED TO ADD
        # Append current_status to current_records with Daily Date
        """"""
      """"""
      # NEED TO ADD
      # Append current_status to current_records with Daily Date
      """"""
    """"""
    # NEED TO ADD
    # Merge on daily Open, Close, High, Low to current_records
    # Calculate Marked to Market Value for each day
    # Calculate Profit / Loss for each day
    # Calculate % Returns for Each day
    """"""
    """"""
    # NEED TO ADD
    # Calculate Cumulative Returns
    # Calculate Annualized Returns
    # Calculate Annualized Sharpe Ratio
    """"""
    return (current_records, cumulative returns, annualized returns, annualized sharpe ratio)
