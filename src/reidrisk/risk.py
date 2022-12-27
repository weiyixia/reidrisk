"""
author: Weiyi Xia
"""
import pandas as pd
import .attacker.Attacker as Attacker
class Risk:
    def __init__(self, dset: pd.DataFrame, attacker: Attacker):
        self.dset = dset
        self.attacker = attacker
    def risk_metric(groupsize):
        '''

        this function compute different risk metric based on group size
        :return:
        implement this function using pattern matching
        '''
