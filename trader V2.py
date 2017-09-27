# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 21:29:49 2017

@author: rkprajap
"""
import pandas as pd
import numpy as np
import os
import time


from Wallet import wallet
from History import filepath as historyfile
from TradeBook import buy, sell, filepath as tradebook, tbwriter
from PollAgent import RepeatedTimer, poll_price



#Trade Constancts
loss_tolerance_pct = .5
per_trade_fiat_radio = .2
xchange_brokerage_pct = .2
polling_frequency_seconds = 15

def moving_average_calc(freq_in_sec, ma_minutes, df, column):    
    cnt = int((ma_minutes*60)/freq_in_sec)
    if (len(df) < cnt):
        return 0
    else:
        rates = df[column].tail(cnt)
        return np.mean(rates)
    
def with_percent_change(basevalue, pct_change, increase=True):
    if increase:
        new_value = basevalue + (basevalue * pct_change)/100.0
    else:
        new_value = basevalue - (basevalue * pct_change)/100.0
    return new_value

        
#load historical data file
btc_price_df = pd.read_csv(historyfile)
os.remove(tradebook)
tbwriter.sanity_check()
wallet.fill_wallet_for_backtest()

def backtesting():
    for index, row in btc_price_df.iterrows():
        ltq = row['INR1000_Rate']
    #    print('Price as on %s:%n', dtm, ltp)
#        m1_MA = moving_average_calc(polling_frequency_seconds, 1, btc_price_df[:index-1], 'INR1000_Rate')
        m60_MA = moving_average_calc(polling_frequency_seconds, 60, btc_price_df[:index-1], 'INR1000_Rate')
        
        #    Stage 1
        if ltq > m60_MA and wallet.fiat_balance > 500:
            buy_score = 1        
            buy_amount = wallet.fiat_balance * per_trade_fiat_radio
            if buy_amount < 1000:
                buy_amount = with_percent_change(wallet.fiat_balance, xchange_brokerage_pct, increase=False)
            buy(ltq, xchange_brokerage_pct, buy_amount)
            print('Bought ',wallet.btc_balance, wallet.fiat_balance)
            
        if wallet.btc_balance > 0 and ltq < wallet.expected_ltq:
            sell_score = 1
            sell(ltq, xchange_brokerage_pct, wallet.btc_balance)
            print('Sold ',wallet.btc_balance, wallet.fiat_balance)
            
def livetesting():
    pollagent = RepeatedTimer(15, poll_price)
    try:
        pollagent.start()
        time.sleep(3800)
    finally:
        pollagent.stop()
    

        

        
        
