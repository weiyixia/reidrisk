import unittest
import numpy as np
from reidrisk.utils import MissingPatterns
from reidrisk.utils import generate_all_binary_string

def _convert_2d_array_to_set(a):
    return set([tuple(i) for i in a])
class TestUtils(unittest.TestCase):
    def test_binary_array_generation(self):
        n = 4
        binary_array = generate_all_binary_string(n)
        expected_array = np.array([[0, 0, 0, 0],[0, 0, 0, 1],[0, 0, 1, 0],[0, 0, 1, 1],[0, 1, 0, 0],[0, 1, 0, 1],[0, 1, 1, 0],[0, 1, 1, 1],[1, 0, 0, 0],[1, 0, 0, 1],[1, 0, 1, 0],[1, 0, 1, 1],[1, 1, 0, 0],[1, 1, 0, 1],[1, 1, 1, 0],[1, 1, 1, 1]])
        self.assertEqual(_convert_2d_array_to_set(binary_array), _convert_2d_array_to_set(expected_array))

    def test_missing_pattern_tree(self):
        patterns = np.array([[0,0,0],[1,1,1],[0,0,1],[1,0,1],[1,1,0],[0,0,1],[1,0,0],[1,0,0],[0,0,1],[0,1,0],[0,0,0]])
        mp = MissingPatterns(patterns)
        expected_u_p = np.array([[0, 0, 0],[0, 0, 1],[0, 1,0],[1, 0, 0],[1, 0, 1],[1, 1, 0],[1,1,1]])
        expected_tree = {0:[], 1: [0], 2: [0], 3: [0], 4: [1,3],5:[2,3],6:[4,5]}
        self.assertEqual(_convert_2d_array_to_set(mp.unique_patterns), _convert_2d_array_to_set(expected_u_p))
        self.assertEqual(mp.tree, expected_tree)
