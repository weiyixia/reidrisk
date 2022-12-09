import unittest
import numpy as np
from reidrisk.utils import generate_all_binary_string
from reidrisk.utils import MissingPatterns
from reidrisk.utils import DataFrameWithMissingValues
import pandas as pd

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
        self.assertEqual(mp._tree, expected_tree)
    def test_DataFrameWithMissingValues(self):
        patterns = np.array([[0,0,0],[8,100,90],[0,0,65],[32,0,26],[22,11,0],[0,0,13],[7,0,0],[6,0,0],[0,0,3],[0,70,0],[0,0,0]])
        mp = DataFrameWithMissingValues(pd.DataFrame(patterns), [0]).missing_patterns
        expected_u_p = np.array([[0, 0, 0],[0, 0, 1],[0, 1,0],[1, 0, 0],[1, 0, 1],[1, 1, 0],[1,1,1]])
        expected_tree = {0:[], 1: [0], 2: [0], 3: [0], 4: [1,3],5:[2,3],6:[4,5]}
        self.assertEqual(_convert_2d_array_to_set(mp.unique_patterns), _convert_2d_array_to_set(expected_u_p))
        self.assertEqual(mp._tree, expected_tree)

    def test_MissingPatterns_get_offsprings(self):
        patterns = np.array([[0,0,0],[1,1,1],[0,0,1],[1,0,1],[1,1,0],[0,0,1],[1,0,0],[1,0,0],[0,0,1],[0,1,0],[0,0,0]])
        mp = MissingPatterns(patterns)
        self.assertEqual(mp._get_offsprings(0), [])
        self.assertEqual(mp._get_offsprings(1), [0])
        self.assertEqual(mp._get_offsprings(2), [0])
        self.assertEqual(mp._get_offsprings(3), [0])
        self.assertEqual(set(mp._get_offsprings(4)), set([0,1,3]))
        self.assertEqual(set(mp._get_offsprings(5)), set([0,2,3]))
        self.assertEqual(set(mp._get_offsprings(6)), set([0,1,2,3,4,5]))
        self.assertEqual(set(mp.pattern_groups[0]), set([0, 10]))
        self.assertEqual(set(mp.pattern_groups[1]), set([2,5,8]))
        self.assertEqual(set(mp.pattern_groups[2]), set([9]))
        self.assertEqual(set(mp.pattern_groups[3]), set([6,7]))
        self.assertEqual(set(mp.pattern_groups[4]), set([3]))
        self.assertEqual(set(mp.pattern_groups[5]), set([4]))
        self.assertEqual(set(mp.pattern_groups[6]), set([1]))

    def test_equivalent_group_size_1(self):
        patterns = np.array([
            [0,0,0],
            [8,100,90],
            [0,0,65],
            [32,0,26],
            [22,11,0],
            [0,0,13],
            [7,0,0],
            [6,0,0],
            [0,0,3],
            [0,70,0],
            [0,0,0]])
        mp = DataFrameWithMissingValues(pd.DataFrame(patterns), [0])
        counts = mp.get_equivalent_group_size()
        self.assertEqual(counts, [2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 2])
    def test_equivalent_group_size_2(self):
        patterns = np.array([
            [0,0,0],
            [8,100,90],
            [0,0,90],
            [8,0,90],
            [0,100,0],
            [0,0,13],
            [8,0,0],
            [0,100,65],
            [0,0,0]])
        mp = DataFrameWithMissingValues(pd.DataFrame(patterns), [0])
        counts = mp.get_equivalent_group_size()
        self.assertEqual(counts, [2, 7, 3, 5, 3, 3, 3, 4, 2])
