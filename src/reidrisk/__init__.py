"""
author: Weiyi Xia
last modified: October 9, 2022

This module contains the functions to creating the probabilistic attacker model for re-identification attack.

"""

from attacker import Attacker

def attacker(name, condition_fields, fields, probability_file):
    return Attacker(name, condition_fields, fields, probability_file)


def twitter_attacker():
    return Attacker()

def voter_attacker():
    return Attacker()
