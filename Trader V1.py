# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from threading import Timer
import os, csv, datetime, time
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
        self.fieldnames = ['DateTime', 'INR1000_Rate','1m_MA','2m_MA','3m_MA','5m_MA','10m_MA','15m_MA','20m_MA','30m_MA','1hr_MA']
        self.rate_dict = dict.fromkeys(self.fieldnames, 0)
        self.last_inr1000_rate = 0
        self.sanity_check()
        
    def sanity_check(self):
        if not os.path.isfile(self.filename):
            with open(self.filepath, 'w', newline='') as outcsv:
                writer = csv.DictWriter(outcsv, fieldnames = self.fieldnames)
                writer.writeheader() 
    
    def write_row(self):
        self.last_inr1000_rate = self.rate_dict['INR1000_Rate']
        with open(self.filepath, 'a', newline='') as outcsv:
            writer = csv.writer(outcsv)
            writer.writerow(self.rate_dict.values())
        
        
#Trade Constancts
loss_tolerance_pct = .5
per_trade_fiat_radio = .2
xchange_brokerage_pct = .2

wallet = Wallet(5000, 0, xchange_brokerage_pct)
writer = HistoricalDataWriter()

def poll_price():    
    inr1000_rate = blockchain.exchangerates.to_btc('INR', 1000)    
    utcnow = datetime.datetime.utcnow()        
    format = "%m/%d/%Y %H:%M:%S"
    dtm = utcnow.strftime(format)
    writer.rate_dict['DateTime'] = dtm
    writer.rate_dict['INR1000_Rate'] = inr1000_rate
    print('BTC Price Per INR 1000:', inr1000_rate)
    writer.write_row()

rt = RepeatedTimer(10, poll_price)    
try:
    rt.start()
    time.sleep(60)
finally:
    rt.stop()






        

        
