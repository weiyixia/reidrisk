"""
author: Weiyi Xia
created on 12/8/2022
last modified: 12/8/2022
"""
import pandas as pd
from google.cloud import bigquery
import os

class Dataset:
    def __init__(
            self,
            source,
            dset: pd.DataFrame=None,
            dfile: str=None,
            colnames = None,
            header=0,
            index_col=False,
            sep=",",
            bigquery_service_account_key_file=None,
            bigquery_dataset=None,
            bigquery_table=None,
            attacker_known_fields_map = [],
            attacker_condition_fields_map = [],
            attacker_condition_fields_values_map = {}
    ):
        self.dset = dset
        self.source = source
        self.dfile = dfile
        self.colnames = colnames
        self.header = header
        self.index_col = index_col
        self.sep = sep
        self.bigquery_service_account_key_file = bigquery_service_account_key_file
        self.bigquery_dataset = bigquery_dataset
        self.bigquery_table = bigquery_table
        self.attacker_known_fields_map = self.set_attacker_known_fields_map(attacker_known_fields_map)
        self.attacker_condition_fields_map = attacker_condition_fields_map
        self.attacker_condition_fields_values_map = attacker_condition_fields_values_map

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

    def set_attacker_known_fields_map(self,a_k_f_map):
        '''
        a_k_f_map: a list of dictionary of known fields for each attacker
        this function checks if the dictionaries are consistent
        i.e., the same fields in different dictionaries are mapped to the same field in the dataset
        for example, if attacker 1 knows race, and attacker 2 also knows race,
        the two race needs to to mapped to the same field in the dataset
        the function returns the combined dictionary of the known fields from all the attackers
        '''
        a_k_f_map_combined = {}
        if a_k_f_map is None or len(a_k_f_map)==0:
            raise ValueError("attacker known fields map is not specified")
        else:
            for item in a_k_f_map:
                for k,v in item.items():
                    if k in a_k_f_map_combined:
                        if a_k_f_map_combined[k] != v:
                            raise ValueError("attacker known fields map is not consistent")
                    else:
                        a_k_f_map_combined[k] = v
        return a_k_f_map_combined

    def get_attacker_known_fields(self, all_fields_from_attacker_model, fields_array_row_from_attacker_model):
        '''
        all_fields_from_attacker_model corresponds to Attacker.ProbModel.fields
        fields_array_row_from_attacker_model corresponds to a row in Attacker.ProbModel.fields_array
        '''

        # get the fields that are known to the attacker in the dataset
        attacker_known_fields = []
        for i in range(len(fields_array_row_from_attacker_model)):
            if fields_array_row_from_attacker_model[i] == 1:
                field_in_attacker_model = all_fields_from_attacker_model[i]
                #convert the field in the attacker model to the field in the dataset
                field_in_dataset = self.attacker_known_fields_map.get(field_in_attacker_model,None)
                if field_in_dataset is not None:
                    attacker_known_fields.append(field_in_dataset)
        return attacker_known_fields

    def get_attacker_condition_fields(self, attacker_condition_fields: []):
        '''
        this function first check if the condition_fields are in the dataset
        all the condition fields need to be mapped to a field in the dataset
        if there is only one attacker model, the attacker condition fields is
        a list of strings
        if the attacker is a combination of two attackers
        the attacker condition fields is a list of two lists of strings
        :param attacker_condition_fields_map: 
        :return: 
        '''
        if len(attacker_condition_fields_map)==0:
            return []
        else:
            attacker_condition_fields_in_dataset = []
            for item in attacker_condition_fields:
                if type(item) is str:
                    curr_field = self.attacker_condition_fields_map.get(item,None)
                    if curr_field is None:
                        raise ValueError("attacker condition field {} is not in the attacker_condition_fields_map".format(item))
                    elif curr_field not in self.dset.columns:
                        raise ValueError("attacker condition field {} is not in the dataset".format(item))
                    else:
                        attacker_condition_fields_in_dataset.append(curr_field)
                else:
                    curr_field_list = []
                    for item_in_item in item:
                        curr_field = self.attacker_condition_fields_map.get(item_in_item,None)
                        if curr_field is None:
                            raise ValueError("attacker condition field {} is not in the attacker_condition_fields_map".format(item_in_item))
                        elif curr_field not in self.dset.columns:
                            raise ValueError("attacker condition field {} is not in the dataset".format(item_in_item))
                        else:
                            curr_field_list.append(curr_field)
                    attacker_condition_fields_in_dataset.append(curr_field_list)
            return attacker_condition_fields_in_dataset

    def get_matching_prob_model(self, df_row, attacker_condition,attacker_condition_fields) :
        '''
        df_row is a row in the dataset
        attacker_condition is a row in the attacker model
        attacker_condition_fields is a row in the attacker model
        :param df_row:
        :param attacker_condition:
        :param attacker_condition_fields:
        :return:
        '''
        for i in range(len(attacker_condition)):
            if attacker_condition[i] == 1:
                field = attacker_condition_fields[i]
                if df_row[field] != self.attacker_condition_fields_values_map.get(field,None):
                    return False
        return True





