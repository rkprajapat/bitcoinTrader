# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 12:42:20 2017

@author: rkprajap
"""

def with_percent_change(basevalue, pct_change, increase=True):
    if increase:
        new_value = basevalue + (basevalue * pct_change)/100.0
    else:
        new_value = basevalue - (basevalue * pct_change)/100.0
    return new_value