# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 21:34:22 2017

@author: rkprajap
"""
import csv, os

url = 'https://blockchain.info/tobtc?currency=INR&value=1000'
dir = os.path.join(os.getcwd(), 'data')
filename = 'bitcoin_historical_prices.csv'
filepath = os.path.join(dir, filename)

class HistoricalDataWriter(object):
    def __init__(self):
        self.fieldnames = ['UTCDateTime', 'INR1000_Rate']
        self.format = "%m/%d/%Y %H:%M:%S"
        self.sanity_check()
        
    def sanity_check(self):
        if not os.path.exists(filepath):
            with open(filepath, 'w', newline='') as outcsv:
                writer = csv.DictWriter(outcsv, fieldnames = self.fieldnames)
                writer.writeheader() 
    
    def write_row(self, dtm, ltq):        
        with open(filepath, 'a', newline='') as outcsv:
            writer = csv.writer(outcsv)
            writer.writerow([dtm, ltq])
            
history_writer = HistoricalDataWriter()
            
    