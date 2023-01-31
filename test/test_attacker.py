import unittest
from reidrisk.attacker import Attacker
from reidrisk.attacker import joined_prob
from reidrisk.attacker import ProbModel
import numpy as np
import pandas as pd

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

    def test_joined_prob_single_field(self):
        field_list = ['age']
        prob_list = [0.5]
        prob_model = joined_prob(field_list, prob_list)
        fields = prob_model.fields
        fields_array = prob_model.fields_array
        prob_list = prob_model.prob_list
        self.assertEqual(fields, ['age'])
        self.assertEqual(np.array_equal(fields_array, np.array([[0],[1]])), True)
        self.assertEqual(np.array_equal(prob_list, np.array([0.5,0.5])), True)

    def test_add_two_prob_model_1(self):
        model1 = ProbModel(['age'],np.array([[0],[1]]),np.array([0.5,0.5]))
        model2 = None
        model3 = model1 + model2
        self.assertEqual(model3.fields, ['age'])
    def test_add_two_prob_model_2(self):
        model1 = ProbModel(['age'],np.array([[0],[1]]),np.array([0.5,0.5]))
        model2 = ProbModel(['gender'],np.array([[0],[1]]),np.array([0.2,0.8]))
        model3 = model1 + model2
        self.assertEqual(model3.fields, ['age', 'gender'])
        self.assertEqual(np.array_equal(model3.fields_array, np.array([[0,0],[0,1],[1,0],[1,1]])), True)

    def test_create_attacker_model1(self):
        attack1_df = pd.read_csv('script/attacker1.csv', header=0, index_col=None, sep=',')
        attack1 = Attacker(attack1_df)
        keys = attack1.model.keys()
        self.assertIn(('black', 'male'), keys)
        self.assertIn(('white', 'male'), keys)
        self.assertIn(('other', 'male'), keys)
        self.assertEqual(attack1.model[('black', 'male')].fields, ['STATE', 'RACE', 'GENDER', 'AGE'])
        self.assertEqual(np.array_equal(attack1.model[('black', 'male')].fields_array, np.array([[0,0,0,0],[1,1,1,1]])), True)
        self.assertEqual(np.array_equal(attack1.model[('black', 'male')].prob_list, np.array([0.5,0.5])), True)
        #    print (value.fields)
        #    print (value.fields_array)
        #    print (value.prob_list)
