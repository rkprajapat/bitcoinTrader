# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from threading import Timer
import os, csv, datetime, time
import pandas as pd
import numpy as np
import blockchain
blockchain.util.TIMEOUT = 5 #time out after 5 seconds

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
#        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
        

class Wallet(object):
    def __init__(self, fiat_balance, btc_balance, brokerage_pct):
        self.fiat_balance = fiat_balance
        self.btc_balance = btc_balance
        self.brokerage_pct = brokerage_pct
        
    def check_balance(self):
        print('INR Balance:%s', self.fiat_balance)
        print('BTC Balance:%s', self.btc_balance)
        
    def buy(self, inr_rate, btc_amount): #inr_rate is for per 1000 rupees
        paid_amount = (inr_rate * btc_amount * (1 + (self.brokerage_pct/100.0)))/1000.0
        self.fiat_balance = self.fiat_balance - paid_amount
        self.btc_balance = self.btc_balance + btc_amount        
        
    def sell(self, inr_rate, btc_amount): #inr_rate is for per 1000 rupees
        self.btc_balance = self.btc_balance - btc_amount
        self.fiat_balance = (inr_rate * btc_amount * (1 - (self.brokerage_pct/100.0)))/1000.0
        
class HistoricalDataWriter(object):
    def __init__(self):
        self.url = 'https://blockchain.info/tobtc?currency=INR&value=1000'
        self.dir = os.path.join(os.getcwd(), 'data')
        self.filename = 'bitcoin_historical_prices.csv'
        self.filepath = os.path.join(self.dir, self.filename)
        self.fieldnames = ['UTCDateTime', 'INR1000_Rate']
        self.format = "%m/%d/%Y %H:%M:%S"
        self.rate_dict = dict.fromkeys(self.fieldnames, 0)
        self.last_inr1000_rate = 0
        self.sanity_check()
        
    def sanity_check(self):
        if os.path.exists(self.filename):
            print('writing file')
            with open(self.filepath, 'w', newline='') as outcsv:
                writer = csv.DictWriter(outcsv, fieldnames = self.fieldnames)
                writer.writeheader() 
    
    def write_row(self):
        self.last_inr1000_rate = self.rate_dict['INR1000_Rate']
        with open(self.filepath, 'a', newline='') as outcsv:
            writer = csv.writer(outcsv)
            writer.writerow(self.rate_dict.values())
            
def moving_average_calc(freq_in_sec, ma_minutes, df, column):    
    cnt = int((ma_minutes*60)/freq_in_sec)
    if (len(df) < cnt):
        return 0
    else:
        rates = df[column].tail(cnt)
        return np.mean(rates)       


def poll_price():    
    inr1000_rate = blockchain.exchangerates.to_btc('INR', 1000)
    print('BTC Price Per INR 1000:', inr1000_rate)
    
    utcnow = datetime.datetime.utcnow()
    dtm = utcnow.strftime(writer.format)
    writer.rate_dict['UTCDateTime'] = dtm
    writer.rate_dict['INR1000_Rate'] = inr1000_rate
    writer.write_row()    
    
    btc_price_df.loc[len(btc_price_df)] = [utcnow, inr1000_rate]
    
#    moving averages
    m1_MA = moving_average_calc(polling_frequency_seconds, 1, btc_price_df, 'INR1000_Rate')
    m3_MA = moving_average_calc(polling_frequency_seconds, 3, btc_price_df, 'INR1000_Rate')
    m5_MA = moving_average_calc(polling_frequency_seconds, 5, btc_price_df, 'INR1000_Rate')
    m10_MA = moving_average_calc(polling_frequency_seconds, 10, btc_price_df, 'INR1000_Rate')
    m20_MA = moving_average_calc(polling_frequency_seconds, 20, btc_price_df, 'INR1000_Rate')
    m30_MA = moving_average_calc(polling_frequency_seconds, 30, btc_price_df, 'INR1000_Rate')
    m60_MA = moving_average_calc(polling_frequency_seconds, 60, btc_price_df, 'INR1000_Rate')
    
    print(m1_MA, m3_MA, m5_MA, m10_MA, m20_MA, m30_MA, m60_MA)

 
#Trade Constancts
loss_tolerance_pct = .5
per_trade_fiat_radio = .2
xchange_brokerage_pct = .2
polling_frequency_seconds = 15

##################################################33
#Instantiate Classes
##################################################33
wallet = Wallet(5000, 0, xchange_brokerage_pct)
writer = HistoricalDataWriter()
btc_price_df = pd.DataFrame(columns=writer.fieldnames)

rt = RepeatedTimer(polling_frequency_seconds, poll_price)
try:
    rt.start()
    time.sleep(6000)
finally:
    rt.stop()






        

        
