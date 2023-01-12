import unittest
import numpy as np
from reidrisk.utils import generate_all_binary_string
from reidrisk.utils import convert_2d_array_to_set
import pandas as pd

class TestUtils(unittest.TestCase):
    def test_binary_array_generation(self):
        n = 4
        binary_array = generate_all_binary_string(n)
        expected_array = np.array([[0, 0, 0, 0],[0, 0, 0, 1],[0, 0, 1, 0],[0, 0, 1, 1],[0, 1, 0, 0],[0, 1, 0, 1],[0, 1, 1, 0],[0, 1, 1, 1],[1, 0, 0, 0],[1, 0, 0, 1],[1, 0, 1, 0],[1, 0, 1, 1],[1, 1, 0, 0],[1, 1, 0, 1],[1, 1, 1, 0],[1, 1, 1, 1]])
        self.assertEqual(convert_2d_array_to_set(binary_array), convert_2d_array_to_set(expected_array))

