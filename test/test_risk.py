import unittest
from reidrisk.dataset import Dataset
from reidrisk.attacker import Attacker
from reidrisk.risk import Risk
import pandas as pd


class TestRisk(unittest.TestCase):
    def test_set_attacker_known_fields_map(self):
        attacker1_df = pd.read_csv('script/attacker1.csv', header=0, index_col=None, sep=',')
        attacker1 = Attacker(attacker1_df)
        ds = Dataset(source='file', dfile='data/syntheticdata_anonymized.csv')
        a_known_f_m={'race':'race','gender':'gender'}
        a_c_f_m = {'race':'race','gender':'gender'}
        r = Risk(ds, attacker1_df, attacker1, a_known_f_m, a_c_f_m)
        self.assertEqual(r.attacker_known_fields_map,{'race':'race','gender':'gender'})

    def test_get_attacker_known_fields(self):
        attacker1_df = pd.read_csv('script/attacker1.csv', header=0, index_col=None, sep=',')
        attacker1 = Attacker(attacker1_df)
        ds = Dataset(source='file', dfile='data/syntheticdata_anonymized.csv')
        a_known_f_m={'race':'race','gender':'gender'}
        a_c_f_m = {'race':'race','gender':'gender'}
        r = Risk(ds, attacker1_df, attacker1, a_known_f_m, a_c_f_m)
        probmodel = attacker1.model[('white','male')]
        fields = probmodel.fields
        fields_array_row = probmodel.fields_array[0]
        attacker_known_fields = r.get_attacker_known_fields(fields, fields_array_row)
        self.assertEqual(attacker_known_fields, [])
        fields_array_row = probmodel.fields_array[1]
        attacker_known_fields = r.get_attacker_known_fields(fields, fields_array_row)
        self.assertEqual(attacker_known_fields, ['race','gender'])

