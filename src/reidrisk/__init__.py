"""
author: Weiyi Xia
last modified: October 9, 2022

This module contains the functions to creating the probabilistic attacker model for re-identification attack.

"""

from attacker import Attacker

def attacker(probability_file, model, name):
    return Attacker(probability_file, model, name)


