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
        self.expected_price = 0
        
    def check_balance(self):
        line1 = 'INR Balance:' + str(self.fiat_balance)
        line2 = 'BTC Balance:' + str(self.btc_balance)
        line3 = 'Cost:' + str(self.cost)
        line4 = 'Cost Price' + str(self.cost_price)
        line5 = 'Expected Price' + str(self.expected_price)
        text_file = open("Wallet.txt", "w")
        text_file.write(line1, line2, line3, line4, line5)
        text_file.close()
        print(line1, line2, line3, line4, line5)
        
    def buy(self, inr_rate, buy_amount): #inr_rate is for per 1000 rupees
        paid_amount = (buy_amount * (1 + (self.brokerage_pct/100.0)))
        self.fiat_balance = self.fiat_balance - paid_amount
        btc_bought = (inr_rate/1000.0)*paid_amount
        self.btc_balance = self.btc_balance + btc_bought
        self.cost = self.cost + paid_amount
        self.cost_price = self.cost/self.btc_balance
        self.expected_price = self.cost_price * (1 + (self.brokerage_pct/100.0))
        self.check_balance()
        return paid_amount
        
    def sell(self, inr_rate, btc_qty): #inr_rate is for per 1000 rupees    
        self.btc_balance = self.btc_balance - btc_qty
        trade_amount = (inr_rate * btc_qty)/1000.0
        received_amount = fiat_amount * (1 - (self.brokerage_pct/100.0))
        self.fiat_balance = self.fiat_balance + received_amount
        self.check_balance()
        return trade_amount,received_amount
        
class TradeBookWriter(object):
    def __init__(self):
        self.dir = os.path.join(os.getcwd(), 'data')
        self.filename = 'tradebook.csv'
        self.filepath = os.path.join(self.dir, self.filename)
        self.fieldnames = ['UTCDateTime', 'INR1000_Rate','Trade_Type','BTC_Qty','Fiat_Amount','Brokerage','Total']
        self.format = "%m/%d/%Y %H:%M:%S"
        self.sanity_check()
        
    def sanity_check(self):
        if os.path.exists(self.filename):
            print('writing file')
            with open(self.filepath, 'w', newline='') as outcsv:
                writer = csv.DictWriter(outcsv, fieldnames = self.fieldnames)
                writer.writeheader() 
    
    def write_row(self, dtm, rate, trtype, btc_qty, amount, brokerage, total):
        with open(self.filepath, 'a', newline='') as outcsv:
            writer = csv.writer(outcsv)
            writer.writerow([dtm, rate, trtype, btc_qty, amount, brokerage, total])
        
class HistoricalDataWriter(object):
    def __init__(self):
        self.url = 'https://blockchain.info/tobtc?currency=INR&value=1000'
        self.dir = os.path.join(os.getcwd(), 'data')
        self.filename = 'bitcoin_historical_prices.csv'
        self.filepath = os.path.join(self.dir, self.filename)
        self.fieldnames = ['UTCDateTime', 'INR1000_Rate']
        self.format = "%m/%d/%Y %H:%M:%S"
        self.rate_dict = dict.fromkeys(self.fieldnames, 0)
        self.sanity_check()
        
    def sanity_check(self):
        if os.path.exists(self.filename):
            print('writing file')
            with open(self.filepath, 'w', newline='') as outcsv:
                writer = csv.DictWriter(outcsv, fieldnames = self.fieldnames)
                writer.writeheader() 
    
    def write_row(self):
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
    
def buy(ltp):
    buy_amount = wallet.fiat_balance * per_trade_fiat_radio
    btc_qty = (ltp * buy_amount)/1000.0
    total_cost = wallet.buy(ltp, buy_amount)
    
    utcnow = datetime.datetime.utcnow()
    dtm = utcnow.strftime(tbwriter.format)
    tbwriter.write_row(dtm, ltp, 'Buy', btc_qty, buy_amount, xchange_brokerage_pct, total_cost)
    
def sell(ltp):
    trade_amount, received_amount = wallet.sell(ltp, wallet.btc_balance)
    
    utcnow = datetime.datetime.utcnow()
    dtm = utcnow.strftime(tbwriter.format)
    tbwriter.write_row(dtm, ltp, 'Sell', wallet.btc_balance, trade_amount, xchange_brokerage_pct, received_amount)
    
    
def trade_decision(ltp):
    buy_score = 0
    sell_score = 0
    
    #    moving averages
    m1_MA = moving_average_calc(polling_frequency_seconds, 1, btc_price_df, 'INR1000_Rate')
    m3_MA = moving_average_calc(polling_frequency_seconds, 3, btc_price_df, 'INR1000_Rate')
    m5_MA = moving_average_calc(polling_frequency_seconds, 5, btc_price_df, 'INR1000_Rate')
    m10_MA = moving_average_calc(polling_frequency_seconds, 10, btc_price_df, 'INR1000_Rate')
    m20_MA = moving_average_calc(polling_frequency_seconds, 20, btc_price_df, 'INR1000_Rate')
    m30_MA = moving_average_calc(polling_frequency_seconds, 30, btc_price_df, 'INR1000_Rate')
    m60_MA = moving_average_calc(polling_frequency_seconds, 60, btc_price_df, 'INR1000_Rate')
    
    print(m1_MA, m3_MA, m5_MA, m10_MA, m20_MA, m30_MA, m60_MA)
#    Stage 1
    if ltp < m1_MA and ltp > m5_MA:
        buy_score = 1
        buy(ltp)
        
    if wallet.btc_balance > 0 and ltp > wallet.expected_price:
        sell_score = 1
        sell(ltp)   


def poll_price():    
    inr1000_rate = blockchain.exchangerates.to_btc('INR', 1000)
    print('BTC Price Per INR 1000:', inr1000_rate)
    
    utcnow = datetime.datetime.utcnow()
    dtm = utcnow.strftime(writer.format)
    writer.rate_dict['UTCDateTime'] = dtm
    writer.rate_dict['INR1000_Rate'] = inr1000_rate
    writer.write_row()   
    
#    Dont trade until enough data is available
    max_rows = int((60*60)/polling_frequency_seconds)
    if len(btc_price_df) > max_rows: 
        trade_decision() #    Identify the trade decision
    
    btc_price_df.loc[len(btc_price_df)] = [utcnow, inr1000_rate]
#    To keep the program memory efficient, remove unnecessary items from dataframe
    
    if len(btc_price_df) > max_rows:
        items_to_drop = len(btc_price_df) - max_rows
        btc_price_df.drop(btc_price_df.index[:items_to_drop], inplace=True)

 
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
tbwriter = TradeBookWriter()
btc_price_df = pd.DataFrame(columns=writer.fieldnames)

rt = RepeatedTimer(polling_frequency_seconds, poll_price)
try:
    rt.start()
    time.sleep(6000)
finally:
    rt.stop()






        

        
