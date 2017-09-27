# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 21:29:49 2017

@author: rkprajap
"""
import pandas as pd
import numpy as np
import os
import time, datetime
import blockchain


from Wallet import wallet
from History import filepath as historyfile, history_writer
from TradeBook import buy, sell, filepath as tradebook, tbwriter
from PollAgent import RepeatedTimer, poll_price



#Trade Constancts
loss_tolerance_pct = .5
xchange_brokerage_pct = .2
polling_frequency_seconds = 15
min_buy_amount = 2000
margin_pct = .1

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



def backtesting(count):
    ltq = blockchain.exchangerates.to_btc('INR', 1000)
    print('BTC Qty Per INR 1000:', ltq)
#    Provide uptime every five minutes
    if count%((5*50)/polling_frequency_seconds) == 0:
        print('Uptime %d minutes' % (count/((5*50)/polling_frequency_seconds)))
    
    utcnow = datetime.datetime.utcnow()
    dtm = utcnow.strftime(history_writer.format)
    history_writer.write_row(dtm, ltq)
    btc_price_df.loc[len(btc_price_df)] = [dtm, ltq]
    
#    Dont trade until enough data is available
    max_rows_for_60_min = int((60*60)/polling_frequency_seconds)
    max_rows_for_1_min = int((1*60)/polling_frequency_seconds)
#    if len(btc_price_df) < max_rows: 
#        return
        
        
#    for index, row in btc_price_df.iterrows():
#        ltq = row['INR1000_Rate']
    #    print('Price as on %s:%n', dtm, ltp)
    
    m1_MA = moving_average_calc(polling_frequency_seconds, 1, btc_price_df[len(btc_price_df)-max_rows_for_1_min:], 'INR1000_Rate')
    m60_MA = moving_average_calc(polling_frequency_seconds, 60, btc_price_df[len(btc_price_df)-max_rows_for_60_min:], 'INR1000_Rate')
    
    #    Stage 1
#    Identify 60 min lowest price and also look for surges by checking 1 min average
    if ltq > m60_MA and ltq > m1_MA and wallet.fiat_balance > min_buy_amount:
        buy_score = 1        
        buy_amount = 0
        if buy_amount < min_buy_amount:
            buy_amount = with_percent_change(min_buy_amount, xchange_brokerage_pct, increase=False)
        if wallet.fiat_balance < (2*min_buy_amount):
            buy_amount = with_percent_change(wallet.fiat_balance, xchange_brokerage_pct, increase=False)
            
        buy(ltq, xchange_brokerage_pct, buy_amount)
        print('Total %f BTC for INR %f' % (wallet.btc_balance, wallet.cost))
        print('Expected LTQ %f' % wallet.expected_ltq)
        
    if wallet.btc_balance > 0 and ltq < with_percent_change(wallet.expected_ltq, margin_pct, increase=False):
        sell_score = 1
        sell(ltq, xchange_brokerage_pct, wallet.btc_balance)
        print('Sold ',wallet.btc_balance, wallet.fiat_balance)
        
#    Stop loss
    if ltq > with_percent_change(ltq, 3, increase=True):
        sell(ltq, xchange_brokerage_pct, wallet.btc_balance)
        print('Sold ',wallet.btc_balance, wallet.fiat_balance)
        


#btc_price_df = pd.DataFrame(columns=['UTCDateTime','INR1000_Rate'])     
#rt = RepeatedTimer(polling_frequency_seconds, backtesting)
#try:
#    rt.start()
#    time.sleep(3800)
#finally:
#    rt.stop()

#Run it for 8 hours
run_window = (8*60*60)/polling_frequency_seconds
count = 1
while(count < run_window):
    backtesting(count)

    count += 1
    time.sleep(polling_frequency_seconds)
    
    
    

        

        
        
