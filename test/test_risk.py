import unittest
from reidrisk.dataset import Dataset
from reidrisk.attacker import Attacker
from reidrisk.risk import Risk
import pandas as pd
from reidrisk.risk import get_attacker_condition_fields_f
from reidrisk.risk import get_attacker_condition_field_values_mapping
from reidrisk.risk import set_attacker_condition_fields_values_map_f


DATAFILE = 'data/synthetic_data_small.csv'
ATTACKERFILE1 = 'script/attacker1.csv'
ATTACKERFILE2 = 'script/attacker2.csv'

class TestRisk(unittest.TestCase):
    def test_set_attacker_known_fields_map(self):
        attacker1_df = pd.read_csv(ATTACKERFILE1, header=0, index_col=None, sep=',')
        attacker1 = Attacker(attacker1_df)
        ds = Dataset(source='file', dfile=DATAFILE)
        a_known_f_m={'RACE':'race','GENDER':'gender','STATE':'state','AGE':'age'}
        a_c_f_m = {'RACE':'race','GENDER':'gender'}
        r = Risk(ds, attacker1_df, attacker1, a_known_f_m, a_c_f_m)
        self.assertEqual(r.attacker_known_fields_map,a_known_f_m)

    def test_get_attacker_known_fields(self):
        attacker1_df = pd.read_csv(ATTACKERFILE1, header=0, index_col=None, sep=',')
        attacker1 = Attacker(attacker1_df)
        ds = Dataset(source='file', dfile=DATAFILE)
        a_known_f_m={'RACE':'race','GENDER':'gender','STATE':'state','AGE':'age'}
        a_c_f_m = {'RACE':'race','GENDER':'gender'}
        r = Risk(ds, attacker1_df, attacker1, a_known_f_m, a_c_f_m)
        probmodel = attacker1.model[('white','male')]
        fields = probmodel.fields
        fields_array_row = probmodel.fields_array[0]
        attacker_known_fields = r.get_attacker_known_fields(fields, fields_array_row)
        self.assertEqual(attacker_known_fields, [])
        fields_array_row = probmodel.fields_array[1]
        attacker_known_fields = r.get_attacker_known_fields(fields, fields_array_row)
        self.assertEqual(attacker_known_fields, ['state','race','gender','age'])

    def test_get_attacker_condition_fields_f_1(self):
        a_c_fields = ['RACE','AGE']
        a_c_fields_map = {'RACE':'race','AGE':'age'}
        df_fields = ['race','age','ethnicity']
        a_c_fields_in_d = get_attacker_condition_fields_f(a_c_fields, a_c_fields_map, df_fields)
        self.assertEqual(a_c_fields_in_d, ['race','age'])
    def test_get_attacker_condition_fields_f_2(self):
        a_c_fields = [['RACE','AGE'],['AGE_RANGE']]
        a_c_fields_map = [{'RACE':'race','AGE':'age'}, {'AGE_RANGE':'age'}]
        df_fields = ['race','age','ethnicity', 'state']
        a_c_fields_in_d = get_attacker_condition_fields_f(a_c_fields, a_c_fields_map, df_fields)
        self.assertEqual(a_c_fields_in_d, [['race','age'],['age']])

    def test_get_attacker_condition_field_values_mapping_1(self):
        mapping_type = 'use_range'
        map_to_range_sep = '-'
        attacker_condition_field_values = ['1-10','10-20']
        field_values_in_d = [1,2,3,4,5,9,10,19]
        a = get_attacker_condition_field_values_mapping(mapping_type, None, map_to_range_sep, attacker_condition_field_values, field_values_in_d)
        self.assertEqual(a[1], '1-10')
        self.assertEqual(a[2], '1-10')
        self.assertEqual(a[3], '1-10')
        self.assertEqual(a[4], '1-10')
        self.assertEqual(a[5], '1-10')
        self.assertEqual(a[9], '1-10')
        self.assertEqual(a[10], '10-20')
        self.assertEqual(a[19], '10-20')
    def test_set_attacker_condition_fields_values_map_f_1(self):
        a_i = pd.read_csv(ATTACKERFILE1, header=0, index_col=None, sep=',')
        ds = Dataset(source='file', dfile=DATAFILE)
        a_c_f_m = {'RACE':'race','GENDER':'gender'}
        race_dict = {'What Race Ethnicity: Black':'black', 'What Race Ethnicity: White':'white', 'Skip':'other',
 'What Race Ethnicity: Hispanic':'other', 'What Race Ethnicity: Asian':'other', 'Other':'other',
 'More than one race/ethnicity':'other', 'Prefer Not To Answer':'other'}
        gender_dict = {'Gender Identity: Man':'male', 'Gender Identity: Woman':'female', 'Skip':'other',
 'Gender Identity: Non Binary':'other', 'Gender Identity: Transgender':'other',
 'Gender Identity: Additional Options' :'other', 'Prefer Not To Answer':'other'}
        a_c_f_v_m_i = {'RACE':['use_dict', race_dict],'GENDER':['use_dict',gender_dict]}
        a = set_attacker_condition_fields_values_map_f(a_c_f_v_m_i, a_c_f_m, a_i, ds)
        self.assertEqual(a, {'race':race_dict, 'gender':gender_dict})
    def test_set_attacker_condition_fields_values_map_f_2(self):
        a_i = pd.read_csv(ATTACKERFILE2, header=0, index_col=None, sep=',')
        ds = Dataset(source='file', dfile=DATAFILE)
        a_c_f_m = {'AGE_RANGE':'age'}
        a_c_f_v_m_i = {'AGE_RANGE':['use_range', None, '-']}
        a = set_attacker_condition_fields_values_map_f(a_c_f_v_m_i, a_c_f_m, a_i, ds)
        self.assertEqual(a['age'][18], '18-24')
        self.assertEqual(a['age'][23], '18-24')
        self.assertEqual(a['age'][24], '24-50')
        self.assertEqual(a['age'][49], '24-50')
        self.assertEqual(a['age'][50], '50-64')
        self.assertEqual(a['age'][63], '50-64')
        self.assertEqual(a['age'][64], '64-121')
        self.assertEqual(a['age'][119], '64-121')

