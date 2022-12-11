import unittest
from reidrisk.attacker import Attacker
from reidrisk.attacker import joined_prob
import numpy as np

class TestAttacker(unittest.TestCase):
    def test_joined_prob(self):
        field_list = ['age', 'race,gender']
        prob_list = [0.5, 0.2]
        prob_model = joined_prob(field_list, prob_list)
        fields = prob_model.fields
        fields_array = prob_model.fields_array
        prob_list = prob_model.prob_list
        self.assertEqual(fields, ['age','race','gender'])
        self.assertEqual(np.array_equal(fields_array, np.array([[0,0,0],[1,0,0],[0,1,1],[1,1,1]])), True)
        self.assertEqual(np.array_equal(prob_list, np.array([0.4,0.4,0.1,0.1])), True)
