# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 21:32:44 2017

@author: rkprajap
"""
import os,csv, sys, datetime

dir = os.path.join(os.getcwd(), 'data')
filename = 'wallet.csv'
filepath = os.path.join(dir, filename)
format = "%a %m/%d/%Y %H:%M:%S"

class Wallet(object):
    def __init__(self):
        self.fiat_balance = 0
        self.btc_balance = 0
        self.expected_ltq = 0
        self.cost = 0
        self.cost_price = 0
        self.fieldnames = ['UTCDateTime','Fiat Balance', 'BTC Balance', 'Cost', 'Cost Price', 'Expected LTQ']
        self.sanity_check()        
        
    def sanity_check(self):
        if not os.path.exists(filepath):
            with open(filepath, 'w', newline='') as outcsv:
                writer = csv.DictWriter(outcsv, fieldnames = self.fieldnames)
                writer.writeheader() 
            print('No wallet balance. Update Wallet.csv in data folder')
            sys.exit()
        else:
            self.check_balance()
                
    def update_wallet(self):
        with open(filepath, 'a', newline='') as outcsv:
            writer = csv.writer(outcsv)
            utcnow = datetime.datetime.utcnow()
            dtm = utcnow.strftime(format)
            writer.writerow([dtm,self.fiat_balance, self.btc_balance, self.cost, self.cost_price, self.expected_ltq]) 
        
    def check_balance(self):
        print('Checking Balance')
        with open(filepath) as incsv:
            reader = csv.DictReader(incsv)
            for row in enumerate(reader):
                self.fiat_balance = float(row[1]['Fiat Balance'])
                self.btc_balance = float(row[1]['BTC Balance'])
                self.cost = float(row[1]['Cost'])
                self.cost_price = float(row[1]['Cost Price'])
                self.expected_ltq = float(row[1]['Expected LTQ'])
                
    def fill_wallet_for_backtest(self):
        os.remove(filepath)
        with open(filepath, 'w', newline='') as outcsv:
            writer = csv.DictWriter(outcsv, fieldnames = self.fieldnames)
            writer.writeheader() 
        self.fiat_balance = 20000
        self.btc_balance = 0
        self.expected_ltq = 0
        self.cost = 0
        self.cost_price = 0
        self.update_wallet()
        

wallet = Wallet()

