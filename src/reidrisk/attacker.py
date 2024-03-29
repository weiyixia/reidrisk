"""
author: Weiyi Xia
last modified: October 9, 2022

This module contains the functions to creating the probabilistic attacker model for re-identification attack.

"""
from typing import Dict, Hashable

import pandas as pd
import numpy as np
import csv
from .utils import generate_all_binary_string


def joined_prob(fields_list, prob_list):
    """
    :param fields_list: a list of fields, ['race', 'gender, age'], an item
    in the list can contain multiple fields
    :param prob_list: a list of probabilities
    :param all_fields: a list of all fields
    :return: a list of joined probabilities, each probability is the joined probability
    that of each combinations of the fields in fields_list
    """

    """
    create a binary matrix to represent all the combinations of the fields
    each row in the array is a combination of the fields
    if the value is 0, the corresponding field is not in the combination
    if the value is 1, the corresponding field is in the combination
    """
    cols_count = len(fields_list)
    fields_array = generate_all_binary_string(cols_count)
    fields_array_invert = 1 - fields_array
    prob_vector = np.array(prob_list)
    """
    the joined probability is the product of the probability that each in_group field is in the group
    and the probability that each out_group field is not in the group
    """
    prob_array = fields_array * prob_vector + fields_array_invert * (1 - prob_vector)
    joined_prob_list = np.prod(prob_array, axis=1)

    field_index_dict = {}
    for i in range(len(fields_list)):
        curr = list(fields_list[i].split(','))
        for item in curr:
            field_index_dict[item] = i

    all_fields = list(field_index_dict.keys())

    # map the fields_array to all_fields_array
    all_fields_array = np.zeros((fields_array.shape[0], len(all_fields))).astype(int)
    # iterate through each column in all_fields_array
    for i in range(len(all_fields)):
        # get the index of the current field in fields_list
        field_index = field_index_dict.get(all_fields[i], -1)
        # if the current field is in fields_list, get the corresponding column in fields_array
        if field_index != -1:
            all_fields_array[:, i] = fields_array[:, field_index]

    return ProbModel(all_fields, all_fields_array, joined_prob_list)


class ProbModel:
    def __init__(self, all_fields, fields_array, prob_list):
        # check if the length of all_fields is equal to the number of columsn in fields_array
        if len(all_fields) != len(fields_array[0]):
            raise Exception("The length of all_fields is not equal to the number of columns in fields_array")
        # check if the number of rows in fields_array is equal to the length of prob_list
        if len(fields_array) != len(prob_list):
            raise Exception("The number of rows in fields_array is not equal to the length of prob_list")
        self.fields = all_fields
        self.fields_array = fields_array
        self.prob_list = prob_list

    def __add__(self, other):
        return add_two_prob_model(self, other)

    def __str__(self):
        df = pd.DataFrame(self.fields_array, columns=self.fields)
        df['prob'] = self.prob_list
        return df.to_string()

    def to_string(self):
        return self.__str__()

def add_two_prob_model(model1, model2):
    """
    :param model1: a ProbModel object
    :param model2: a ProbModel object
    :return: a ProbModel object that is the sum of model1 and model2
    """
    if model1 is None:
        return model2
    if model2 is None:
        return model1
    fields = list(set(model1.fields + model2.fields))
    cols_count = len(fields)
    fields_array1 = np.zeros((model1.fields_array.shape[0], cols_count)).astype(int)
    fields_array2 = np.zeros((model2.fields_array.shape[0], cols_count)).astype(int)

    for item in fields:
        if item in model1.fields:
            fields_array1[:, fields.index(item)] = model1.fields_array[:, model1.fields.index(item)]
        if item in model2.fields:
            fields_array2[:, fields.index(item)] = model2.fields_array[:, model2.fields.index(item)]

    m1_nonzero_index = np.where(model1.prob_list > 0)[0]
    m2_nonzero_index = np.where(model2.prob_list > 0)[0]

    m1_nonzero = model1.prob_list[m1_nonzero_index]
    m2_nonzero = model2.prob_list[m2_nonzero_index]

    m1_fields_array_nonzero = fields_array1[m1_nonzero_index, :]
    m2_fields_array_nonzero = fields_array2[m2_nonzero_index, :]

    fields_array_list = []
    prob_v_list = []
    # iterate through each row in m1_fields_array_nonzero
    for i in range(m1_fields_array_nonzero.shape[0]):
        curr_row = m1_fields_array_nonzero[i, :]
        m1_curr_fields_array = np.tile(curr_row, (m2_fields_array_nonzero.shape[0], 1))
        m1_curr_prob_v = np.tile(np.array(m1_nonzero[i]), m2_fields_array_nonzero.shape[0])

        curr_fields_array = m1_curr_fields_array | m2_fields_array_nonzero
        curr_prob_v = m1_curr_prob_v * m2_nonzero

        fields_array_list.append(curr_fields_array)
        prob_v_list.append(curr_prob_v)

    total_fields_array = np.concatenate(fields_array_list)
    total_prob_v = np.concatenate(prob_v_list)

    total_array = np.concatenate([total_fields_array, total_prob_v.reshape(total_prob_v.shape[0], 1)], axis=1)

    total_df = pd.DataFrame(total_array, columns=fields + ['prob'])
    # convert the columns in fields to int
    for item in fields:
        total_df[item] = total_df[item].astype(int)

    group_sum_df = total_df.groupby(fields).sum().reset_index()

    field_array = group_sum_df[fields].values
    prob_v = group_sum_df['prob'].values
    return ProbModel(fields, field_array, prob_v)


class Attacker:
    def __init__(self, probability_df, model = None, name='',condition_fields=[]):
        """
        :param name: the name of the attacker
        :param condition_fields: the list of field names that the probabilities are conditioned on
        :param fields: the list of fields that there is a probability that the attacker knows
        :param probability_df: the dataframe that contains the conditional probabliities
        each condition_fields corresponds to a column in the file
        in addition to that, there are two columns: known_fields and probability
        the values in the known_fields are comma separated, e.g. 'age, race', 'gender';
        the values in the known_fields in all the rows with the same values in the condition_fields
        should not overlap.
        For example, if row one and row two have the same values in all the columns corresponding to
        the condition_fields, and row one's known_fields is 'age, race', and row two's known_fields is 'age, gender'
        then the probability file is invalid.
        """
        self.name = name
        self.probability_df = probability_df
        self._check_columns()
        if condition_fields!=[]:
            self.condition_fields=condition_fields
        else:
            self.condition_fields = self._get_condition_fields()
        self._check_known_fields()
        self.model = model
        if self.model is None:
            self._set_attacker_model()

    def _check_columns(self):
        if self.probability_df is None:
            pass
        else:
            header = list(self.probability_df.columns)
            if 'known_fields' not in header:
                raise Exception("The column known_fields is not in the probability file")
            if 'probability' not in header:
                raise Exception("The column probability is not in the probability file")

    def _check_known_fields(self):
        if self.probability_df is not None:
            df = self.probability_df
            # group df by the condition_fields and check each group
            if len(self.condition_fields) > 0:
                for name, group in df.groupby(self.condition_fields):
                    known_fields_list = group['known_fields'].tolist()
                    known_fields_set = set()
                    # check if the values in the known_fields are valid
                    for i in known_fields_list:
                        known_fields = set(i.split(','))
                        # check if known_fields is in the known_fields_set
                        if known_fields in known_fields_set:
                            raise ValueError('ERROR in group' + str(
                                name) + ': The values in the known_fields in all the rows with the same values in the condition_fields should not overlap.')
            else:
                known_fields_list = df['known_fields'].tolist()
                known_fields_set = set()
                # check if the values in the known_fields are valid
                for i in known_fields_list:
                    known_fields = set(i.split(','))
                    # check if known_fields is in the known_fields_set
                    if known_fields in known_fields_set:
                        raise ValueError('ERROR in group' + str(
                            name) + ': The values in the known_fields in all the rows with the same values in the condition_fields should not overlap.')

    def _get_condition_fields(self):
        if self.probability_df is not None:
            column_names = list(self.probability_df.columns)
            column_names.remove('known_fields')
            column_names.remove('probability')
            return list(column_names)
        else:
            return []

    def _set_attacker_model(self):
        """
        return a dictionary, the keys are tuples of values of the condition_fields
        and the values are ProbModel objects
        """
        if self.probability_df is not None:
            df = self.probability_df
            # group df by the condition_fields and check each group
            attacker_model: dict[Hashable, ProbModel] = {}
            if len(self.condition_fields) == 0:
                known_fields_list = df['known_fields'].tolist()
                prob_list = df['probability'].tolist()
                attacker_model = joined_prob(known_fields_list, prob_list)
            else:
                for name, group in df.groupby(self.condition_fields):
                    known_fields_list = group['known_fields'].tolist()
                    prob_list = group['probability'].tolist()
                    if type(name) is tuple:
                        attacker_model[name] = joined_prob(known_fields_list, prob_list)
                    else:
                        attacker_model[tuple([name])] = joined_prob(known_fields_list, prob_list)
            self.model = attacker_model

    def __add__(self, other):
        return add_two_attacker_model(self, other)

    def __str__(self):
        l1 = "Attacjer name: " + self.name + "\n"
        l2 = ''
        for k, v in self.model.items():
            for index, item in enumerate(self.condition_fields):
                l2 += str(item) + ": " + str(k[index]) + ", "
            l2 += "\n"
            l2 += str(v)
            l2 += "\n"
        return l1 + l2


def add_two_attacker_model(model1, model2):
    '''
    :param model1: Attacker
    :param model2: Attacker
    :return:
    '''
    m1 = model1.model
    m2 = model2.model

    if m1 is None:
        return model2

    if m2 is None:
        return model1

    name = model1.name + ' plus ' + model2.name
    condition_fields = model1.condition_fields + model2.condition_fields

    model_sum = {}
    if len(model1.condition_fields) == 0:
        if len(model2.condition_fields) == 0:
            model_sum = m1 + m2
        else:
            for name2, group2 in m2.items():
                model_sum[name2] = m1 + group2
    else:
        if len(model2.condition_fields) == 0:
            for name1, group1 in m1.items():
                model_sum[name1] = group1 + m2
        else:
            for name1, group1 in m1.items():
                for name2, group2 in m2.items():
                    model_sum[tuple([name1, name2])] = group1 + group2
    return Attacker(None, model_sum,'',[model1.condition_fields, model2.condition_fields])
