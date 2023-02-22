import unittest
from reidrisk.dataset import Dataset
import pandas as pd

DATAFILE = 'data/synthetic_data_small.csv'
DATAFILE2 = 'data/AoU_DM_2000.csv'
class TestDataset(unittest.TestCase):

    def test_bigquery(self):
        ds = Dataset(
            source = 'bigquery',
            bigquery_service_account_key_file='/Users/weiyi/Documents/projects/privacydynamics/keys/prvy-synthetic-8d9e39a1462e.json',
            bigquery_dataset='aoudatabrowsersynthetic',
            bigquery_table='basicsurvey_with_id'
        )
        self.assertEqual(ds.dset.shape[0], 372380)

    def test_file(self):
        ds = Dataset(source='file', dfile=DATAFILE)
        self.assertEqual(ds.dset.shape[0], 50)

    def test_combine_multiselect(self):
        """
        this test case can be moved to a Jupyter notebook as a demonstration
        """
        null_value_list_file = 'data/null_value_list.csv'
        null_value_l = pd.read_csv(null_value_list_file, header=0, index_col=None, na_filter=False)
        null_value_l = list(null_value_l[null_value_l.columns[0]])
        multiselectvaluesf = 'data/multi_select_field_values.csv'
        unique_values_df = pd.read_csv(multiselectvaluesf)

        grouped = unique_values_df.groupby("field")['value'].apply(list)
        values_dict = dict(grouped)
        datamodel= 'OMOP'
        ds = Dataset(source='file', dfile=DATAFILE2, null_value_list=null_value_l, data_model=datamodel, multi_select_field_values = values_dict, year_bin=2)
        ds.combine_multi_select_answers()
        ds.dset.to_csv('data/AoU_DM_2000_combine_multi_select.csv', index=False)
    def test_default_pipeline(self):
        """
        this test case can be moved to a Jupyter notebook as a demonstration
        """
        null_value_list_file = 'data/null_value_list.csv'
        null_value_l = pd.read_csv(null_value_list_file, header=0, index_col=None, na_filter=False)
        null_value_l = list(null_value_l[null_value_l.columns[0]])
        multiselectvaluesf = 'data/multi_select_field_values.csv'
        unique_values_df = pd.read_csv(multiselectvaluesf)

        grouped = unique_values_df.groupby("field")['value'].apply(list)
        values_dict = dict(grouped)
        datamodel=None
        ds = Dataset(source='file', dfile=DATAFILE2, null_value_list=null_value_l, data_model=datamodel, multi_select_field_values = values_dict, year_bin=2)
        ds.pipeline()
        ds.dset_numeric.to_csv('data/AoU_DM_2000_numeric_datamodel_default.csv', index=False)
    def test_omop_pipeline(self):
        """
        this test case can be moved to a Jupyter notebook as a demonstration
        """
        null_value_list_file = 'data/null_value_list.csv'
        null_value_l = pd.read_csv(null_value_list_file, header=0, index_col=None, na_filter=False)
        null_value_l = list(null_value_l[null_value_l.columns[0]])
        multiselectvaluesf = 'data/multi_select_field_values.csv'
        unique_values_df = pd.read_csv(multiselectvaluesf)

        grouped = unique_values_df.groupby("field")['value'].apply(list)
        values_dict = dict(grouped)
        datamodel= 'OMOP'
        ds = Dataset(source='file', dfile=DATAFILE2, null_value_list=null_value_l, data_model=datamodel, multi_select_field_values = values_dict, year_bin=2)
        ds.pipeline()
        ds.dset_numeric.to_csv('data/AoU_DM_2000_numeric_datamodel_OMOP.csv', index=False)

