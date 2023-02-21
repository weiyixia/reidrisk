"""
author: Weiyi Xia
created on 12/8/2022
last modified: 12/8/2022
"""
import pandas as pd
import numpy as np
from google.cloud import bigquery
import os


def combine(col_to_combine):
    v_str = ''
    for col in col_to_combine:
        if col != None and col != '' and not pd.isnull(col):
            if v_str == '':
                v_str = col
            else:
                v_str = v_str + ' and ' + col
    return v_str


def generalize_birth_year(x, birthyear_group_size):
    if len(str(x)) < 4:
        return ''
    else:
        return str(int(str(x)[:4]) - (int(str(x)[:4]) % (birthyear_group_size)))


class Dataset:
    def __init__(
            self,
            source,
            dset: pd.DataFrame = None,
            dfile: str = None,
            colnames=None,
            header=0,
            index_col=False,
            sep=",",
            null_value_list=[],
            bigquery_service_account_key_file=None,
            bigquery_dataset=None,
            bigquery_table=None,
            # missing_set is the set of values that are considered missing, for example, ['NA', 'N/A', 'Skip','prefer not to answer']
            missing_set=None,
            year_bin=1
    ):
        self.dset = dset
        self.source = source
        self.dfile = dfile
        self.colnames = colnames
        self.header = header
        self.index_col = index_col
        self.sep = sep
        self.null_value_list = null_value_list
        self.bigquery_service_account_key_file = bigquery_service_account_key_file
        self.bigquery_dataset = bigquery_dataset
        self.bigquery_table = bigquery_table
        self.load()
        self.columns = self.dset.columns
        self.selected_columns = self.columns
        self.missing_set = missing_set
        self.year_bin = year_bin
        self.dset_numeric = None
        self.null_df = None
        self.categories_dict = {}

    def load(self):
        if self.source == "dataframe":
            pass
        elif self.source == 'file':
            if self.dfile is None:
                raise ValueError("dataset file is not specified")
            else:
                self.dset = pd.read_csv(self.dfile, sep=self.sep, header=self.header, index_col=self.index_col)

        elif self.source == "bigquery":
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.bigquery_service_account_key_file
            client = bigquery.Client()
            query = "SELECT * FROM {}.{}".format(self.bigquery_dataset, self.bigquery_table)
            self.dset = client.query(query).to_dataframe()
        elif self.source == "bigquery_omop":
            '''
            this is for the AoU OMOP data
            it needs to be implemented
            '''
            pass
        else:
            raise ValueError("dataset source is not specified")

    def combine_multi_select_answers(self, multi_select_field_values_dict):
        """
        this function does these:
        first, combine the columns associated with a multi-select questions, and do this for all the multi-select questions
        second, remove all the columns related to single answers of the multi-select questions
        """

        for field, value_list in multi_select_field_values_dict.items():
            col_to_combine = []
            for name_value in value_list:
                if name_value not in self.null_value_list:
                    curr_col_name = str(field) + '_' + str(name_value)
                    col_to_combine.append(curr_col_name)

            self.dset[field] = self.dset.apply(lambda x: combine([x[col_name] for col_name in col_to_combine]), axis=1)

        col_to_remove = []
        for field, value_list in multi_select_field_values_dict.items():
            for name_value in value_list:
                col_to_remove.append(str(field) + '_' + str(name_value))
        print(col_to_remove)
        all_cols = self.dset.columns
        self.dset[[i for i in all_cols if i not in col_to_remove]]

    def replace_all_unknown_to_empty_string(self, null_value_list):
        self.dset.replace({i: '' for i in null_value_list}, inplace=True)

    def create_year_of_death_column(self):
        if 'death_date' in self.columns:
            self.dset['year_of_death'] = self.dset['death_date'].apply(lambda x: str(x)[:4])

    def generalize_year(self):
        """
        this function is for the AoU OMOP data, corresponding to the function in the original code base file: generate_dataset.py
        generate_dataset_numeric_df_for_new_aou(self, file_prefix, null_value_list_file, year_bin, filters_for_all_fields_in_analysis, convert_to_numeric=True):
        """
        if 'YEAR_OF_BIRTH' in self.columns:
            self.dset['YEAR_OF_BIRTH'] = self.dset['YEAR_OF_BIRTH']. \
                apply(lambda x: generalize_birth_year(x, self.year_bin))

        if 'birth_year' in self.columns:
            self.dset['birth_year'] = self.dset['birth_year']. \
                apply(lambda x: generalize_birth_year(x, self.year_bin))

        if 'year_of_birth' in self.columns:
            self.dset['year_of_birth'] = self.dset['year_of_birth']. \
                apply(lambda x: generalize_birth_year(x, self.year_bin))

        if 'year_of_death' in self.columns:
            self.dset['year_of_death'] = self.dset['year_of_death']. \
                apply(lambda x: generalize_birth_year(x, self.year_bin))

    def convert_cate_to_numeric(self):
        """
        this function corresponds to the function in the original code base file: targeted_attack_risk_from_local_file_for_new_aou.py
        convert_cate_to_numeric
        """
        self.dset_numeric = self.dset.replace('', np.nan)
        self.null_df = self.dset_numeric.isnull()
        for field_i in self.columns:
            self.categories_dict[field_i] = dict(
                enumerate(self.dset_numeric[field_i].astype('category').cat.categories))
            self.dset_numeric[field_i] = self.dset_numeric[field_i].astype('category').cat.codes
