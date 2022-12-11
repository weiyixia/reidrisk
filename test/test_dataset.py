import unittest
from reidrisk.dataset import Dataset

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
        ds = Dataset(source='file', dfile='data/syntheticdata.csv')
        ds.load()
        self.assertEqual(ds.dset.shape[0], 372380)
