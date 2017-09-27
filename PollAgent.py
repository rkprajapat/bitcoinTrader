# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 21:41:55 2017

@author: rkprajap
"""
import blockchain, datetime
import pandas as pd
from threading import Timer

from History import HistoricalDataWriter

writer = HistoricalDataWriter()



##################################################33
#Instantiate Classes
##################################################33
btc_price_df = pd.DataFrame(columns=writer.fieldnames)
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

def poll_price():    
    inr1000_rate = blockchain.exchangerates.to_btc('INR', 1000)
    print('BTC Price Per INR 1000:', inr1000_rate)
    
    utcnow = datetime.datetime.utcnow()
    dtm = utcnow.strftime(writer.format)
    writer.rate_dict['UTCDateTime'] = dtm
    writer.rate_dict['INR1000_Rate'] = inr1000_rate
    writer.write_row()
    
    return dtm, inr1000_rate



        
        
        