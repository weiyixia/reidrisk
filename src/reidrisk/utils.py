"""
author: Weiyi Xia
last modified:  12/8/2022
"""
import numpy as np
import pandas as pd
def generate_all_binary_string(n):
    """
    Given a positive integer number N. The task is to generate all the binary strings of N bits.
    These binary strings should be in ascending order.
    :param n:
    :return an array:
    """
    rows_count = 2**n
    cols_count = n
    binary_array = np.zeros((rows_count, cols_count))
    for i in range(rows_count):
        for j in range(cols_count):
            if (i//(2**j))%2 == 1:
                binary_array[i][j] = 1
    return binary_array.astype(int)
def convert_2d_array_to_set(a):
    return set([tuple(i) for i in a])

