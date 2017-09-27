# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 21:36:27 2017

@author: rkprajap
"""
import os, csv, datetime
from Wallet import wallet
from utility import with_percent_change


dir = os.path.join(os.getcwd(), 'data')
filename = 'tradebook.csv'
filepath = os.path.join(dir, filename)

class TradeBookWriter(object):
    def __init__(self):
        self.fieldnames = ['UTCDateTime', 'INR1000_Rate','Trade_Type','BTC_Qty','Fiat_Amount','Brokerage Pct','Total']
        self.format = "%m/%d/%Y %H:%M:%S"
        self.sanity_check()
        
    def sanity_check(self):
        if not os.path.exists(filepath):
            with open(filepath, 'w', newline='') as outcsv:
                writer = csv.DictWriter(outcsv, fieldnames = self.fieldnames)
                writer.writeheader() 
    
    def write_row(self, dtm, rate, trtype, btc_qty, amount, brokerage, total):
        with open(filepath, 'a', newline='') as outcsv:
            writer = csv.writer(outcsv)
            writer.writerow([dtm, rate, trtype, btc_qty, amount, brokerage, total])

def buy(ltq, xchange_brokerage_pct, buy_amount):
    btc_qty = (ltq * buy_amount)/1000.0
    paid_amount = with_percent_change(buy_amount, xchange_brokerage_pct, increase=True)
    wallet.fiat_balance = wallet.fiat_balance - paid_amount
    wallet.btc_balance = wallet.btc_balance + btc_qty
    wallet.cost = wallet.cost + paid_amount
#    wallet.cost_price = (wallet.btc_balance/wallet.cost)*1000
#    wallet.expected_ltq = wallet.cost_price * (1 + (xchange_brokerage_pct/100.0))
    wallet.expected_ltq = (wallet.btc_balance*1000)/ with_percent_change(wallet.cost, xchange_brokerage_pct, increase=True)
    wallet.update_wallet()
        
    utcnow = datetime.datetime.utcnow()
    dtm = utcnow.strftime(tbwriter.format)
    tbwriter.write_row(dtm, ltq, 'Buy', btc_qty, buy_amount, xchange_brokerage_pct, paid_amount)
    
def sell(ltq, xchange_brokerage_pct, btc_qty):
    sale_amount = (btc_qty/ltq)*1000.0    
    received_amount = with_percent_change(sale_amount, xchange_brokerage_pct, increase=False)    
    wallet.fiat_balance = wallet.fiat_balance + received_amount
    if btc_qty == wallet.btc_balance:
        wallet.btc_balance = 0
        wallet.cost = 0
        wallet.expected_ltq = 0
    else:
        wallet.btc_balance = wallet.btc_balance - btc_qty
        wallet.cost = wallet.cost - received_amount
        wallet.expected_ltq = (wallet.btc_balance*1000)/ with_percent_change(wallet.cost, xchange_brokerage_pct, increase=True)
   
    wallet.update_wallet()
    
    utcnow = datetime.datetime.utcnow()
    dtm = utcnow.strftime(tbwriter.format)
    tbwriter.write_row(dtm, ltq, 'Sell', btc_qty, sale_amount, xchange_brokerage_pct, received_amount)

tbwriter = TradeBookWriter()
 