import unittest
from reidrisk.dataset import Dataset
from reidrisk.attacker import Attacker
import pandas as pd

class TestDataset(unittest.TestCase):
    def test_bigquery(self):
        ds = Dataset(
            source = 'bigquery',
            bigquery_service_account_key_file='/Users/weiyi/Documents/projects/privacydynamics/keys/prvy-synthetic-8d9e39a1462e.json',
            bigquery_dataset='aoudatabrowsersynthetic',
            bigquery_table='basicsurvey_with_id'
        )
        ds.load()
        self.assertEqual(ds.dset.shape[0], 372380)

    def test_file(self):
        ds = Dataset(source='file', dfile='data/syntheticdata_anonymized.csv')
        ds.load()
        self.assertEqual(ds.dset.shape[0], 372380)

    def test_set_attacker_known_fields_map(self):
        ds = Dataset(source='file',
                     dfile='data/syntheticdata_anonymized.csv',
                     attacker_known_fields_map=[{'race':'race','gender':'gender'},{'race':'race','income':'income'}]
                     )
        self.assertEqual(ds.attacker_known_fields_map,{'race':'race','gender':'gender','income':'income'})
    def test_get_attacker_known_fields(self):
        ds = Dataset(source='file',
                     dfile='data/syntheticdata_anonymized.csv',
                     attacker_known_fields_map=[{'race':'race','gender':'gender'}])
        ds.load()
        attack1_df = pd.read_csv('script/attacker1.csv', header=0, index_col=None, sep=',')
        attacker1 = Attacker(attack1_df)
        probmodel = attacker1.model[('white','hispanic','NC')]
        fields = probmodel.fields
        fields_array_row = probmodel.fields_array[0]
        attacker_known_fields = ds.get_attacker_known_fields(fields, fields_array_row)
        self.assertEqual(attacker_known_fields, [])
        fields_array_row = probmodel.fields_array[1]
        attacker_known_fields = ds.get_attacker_known_fields(fields, fields_array_row)
        self.assertEqual(attacker_known_fields, ['race','gender'])

