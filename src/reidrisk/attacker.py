"""
author: Weiyi Xia
last modified: October 9, 2022

This module contains the functions to creating the probabilistic attacker model for re-identification attack.

"""
import pandas as pd
import numpy as np
import csv

class Attacker:
    def __init__(self, name, condition_fields, fields, probability_file):
        """
        :param name: the name of the attacker
        :param condition_fields: the list of field names that the probabilities are conditioned on
        :param fields: the list of fields that there is a probability that the attacker knows
        :param probability_file: the file that contains the conditional probabliities
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
        self.condition_fields = condition_fields
        self.fields = fields
        self.probability_file = probability_file
        """
        self.probability_model contains the dictionary of the conditional probabilities
        the key is the tuple of the values of the condition_fields
        the value is the list of probabilities of all the different combinations of the fields
        """
        self.probability_model = None


    def _check_probability_file(self):
         """
        self.probability_file: the file that contains the conditional probabliities
        each condition_fields corresponds to a column in the file
        in addition to that, there are two columns: known_fields and probability
        the values in the known_fields are comma separated, e.g. 'age, race', 'gender';
        the field in known_fields should be in the self.fields
        if a field is not in self.fields, the probability file is invalid
        the values in the known_fields in all the rows with the same values in the condition_fields
        should not overlap.
        For example, if row one and row two have the same values in all the columns corresponding to
        the condition_fields, and row one's known_fields is '
        the values in the known_fields in all the rows with the same values in the condition_fields
        should not overlap.
        For example, if row one and row two have the same values in all the columns corresponding to
        the condition_fields, and row one's known_fields is 'age, race', and row two's known_fields is 'age, gender'
        then the probability file is invalid.
        """
        #check if the column names are valid
        with open(self.probability_file, 'r') as f:
            reader = csv.reader(f)
            column_names = next(reader)
            if set(column_names) != set(self.condition_fields + ['known_fields', 'probability']):
                raise ValueError('The column names in the probability file are invalid.')

        #check if the comma seperated field in each row in the known_fields are in the self.fields
        df = pd.read_csv(self.probability_file)
        for row in df.iterrows():
            known_fields = row[1]['known_fields'].split(',')
            if set(known_fields) - set(self.fields):
                raise ValueError('ERROR in row' + str(row) + ': The field in known_fields should be in the self.fields.')

        df = pd.read_csv(self.probability_file)
        #group df by the condition_fields and check each group
        for name, group in df.groupby(self.condition_fields):
            known_fields_list = group['known_fields'].tolist()
            known_fields_set = set()
            #check if the values in the known_fields are valid
            for i in known_fields_list:
                known_fields = set(i.split(','))
                #check if known_fields is in the known_fields_set
                if known_fields in known_fields_set:
                    raise ValueError('ERROR in group' + str(name) + ': The values in the known_fields in all the rows with the same values in the condition_fields should not overlap.')

""" 
private functions
"""
"""
The function __get_each_field_prob_list() is used to get the probability of each field in the field map table.
param: field_prob_filename: the file name of the csv file that contains the probability of each field
param: fields: the list of columns from the field map table
return: prob_list: the list of probabilities of each field in the field map table
"""
def __get_each_field_prob_list(field_prob_filename, fields):
    prob_df = pd.read_csv(field_prob_filename, sep=',', header=0, index_col=None)
    if ATTR_TO_STANDARD_ATTR_MAP != None:
        prob_df = prob_df.replace(ATTR_TO_STANDARD_ATTR_MAP)
    prob_list = []
    #iterate through each column of the field map table
    for col_name in fields:
        #find the row in the prob_df that corresponds to the current field if exists
        prob_row = prob_df[prob_df['field']==col_name]
        #by default, if the row does not exist, the probability is 0
        prob_value = 0
        #if the row exists, get the probability value from the row
        if prob_row.shape[0]>0:
            prob_value = list(prob_row['probability'])[0]
        #add the probability value to the list
        prob_list.append(prob_value)
    return prob_list
"""
a private function for creating the list of fields in the group for each row offunction needed
params: fields_df: a dataframe of the field map table
return: fields_df with a new column "field_group" added 
"""
def __add_field_group_list_col_to_field_map(field_map_df):
    col_names = field_map_df.columns.tolist()
    field_map_df['field_group'] = field_map_df[col_names].apply(lambda x: set(x[x==1].index.tolist()), axis=1)
    return field_map_df



"""
Function get_joined_prob() is used to compute the joined probability of each group of fields the attacker knows
params: field_map_table: the file name of the field map table, each column is a field, each row contains "0" and "1" values,
"1" means the field is in the group, "0" means the field is not in the group
the first row is the header, the first column is the index
params: single_field_prob_list: a list of probabilities of each field 
return: a list of joined probabilities of each group of fields the attacker knows
"""
def __get_joined_prob(field_map_table, single_field_prob_list):
    #read the field map table to a dataframe
    fields_df = pd.read_csv(field_map_table, index_col=0, header=0, sep=',')

    #convert the dataframe to numpy array
    fields_array = np.array(fields_df)

    fields_array_reverse =np.full(fields_df.shape, 1) - fields_array


    field_in_group_prob_list_vector = np.array(single_field_prob_list)
    field_not_in_group_prob_list_vector = np.full(len(single_field_prob_list), 1) - field_in_group_prob_list_vector
   """
   the joined probability is the product of the probability that each in_group field is in the group
   and the probability that each out_group field is not in the group
   """
    single_field_prob_array =  fields_array*field_in_group_prob_list_vector + fields_array_reverse* field_not_in_group_prob_list_vector
    joined_prob_list = np.prod(single_field_prob_array, axis = 1)
    return joined_prob_list


"""
Function field_group_prob_to_joined_prob_list() is used convert an input of the probability that the attacker knows
certain group of fields to a list of probabilities corresponding to each group of fields. 
params: field_map_table: the file name of the field map table, each column is a field, each row contains "0" and "1" values,
"1" means the field is in the group, "0" means the field is not in the group
the first row is the header, the first column is the index
params: joined_fields_prob_df: a dataframe of the joined probability of each group of fields the attacker knows instead of each field,
this applies to resources such as Voter Registration Data, where the attacker knows the joined probability of each group of fields 
return: a list of joined probabilities of each group of fields the attacker knows
"""
def __field_group_prob_to_joined_prob_list(field_map_table, joined_fields_prob_df):
    fields_df = pd.read_csv(field_map_table, index_col=0, header=0, sep=',')
    fields_df = __add_field_group_list_col_to_field_map(fields_df)
    fields_df['combined_prob'] = 0

    total_non_empty_prob = 0
    #iterate through each row of the joined_fields_prob_df
    #each row is a group of fields
    #in the voter registration data, there is only one row
    for row_index in joined_fields_prob_df.index.tolist():
        curr_field_group = joined_fields_prob_df.loc[row_index, 'field_group']
        curr_prob = joined_fields_prob_df.loc[row_index, 'prob']
        fields_df.loc[fields_df['field_group']==curr_field_group, 'combined_prob'] = curr_prob
        total_non_empty_prob = total_non_empty_prob + curr_prob
    """
    other than the fields groups specified in joined_fields_prob_df, 
    there is only one more possible situation, that is, the attacker does not know anything, i.e., empty set
    """
    fields_df.loc[fields_df['field_group']==set([]), 'combined_prob'] = 1- total_non_empty_prob
    return np.array(list(fields_df['combined_prob']))

#function needed
def _combine_two_attacker_models(m1, m2, field_map_table):
    fields_df = pd.read_csv(field_map_table, index_col=0, header=0, sep=',')
    fields_array = np.array(fields_df)
    m1_nonzero_index = np.where(m1>0)[0]
    fields_array_list = []
    prob_v_list = []

    for i in m1_nonzero_index:
        m1_prob_v = np.tile(np.array(m1[i]), fields_array.shape[0])
        #print (m1_prob_v)
        m1_fields_array = np.tile(fields_array[i,:], (fields_array.shape[0],1))
        #print (m1_fields_array)

        combined_prob_v = m1_prob_v*m2

        #print (combined_prob_v)

        combined_fields_df = fields_array | m1_fields_array

        prob_v_list.append(combined_prob_v)
        fields_array_list.append(combined_fields_df)


    total_fields_array = np.concatenate(fields_array_list)
    total_prob_v = np.concatenate(prob_v_list)
    #print (total_fields_array)
    #print (total_prob_v)

    total_array = np.concatenate([total_fields_array,total_prob_v.reshape(total_prob_v.shape[0],1)], axis=1)


    total_df = pd.DataFrame(total_array, columns = list(fields_df.columns) + ['prob'])
    group_sum_df = total_df.groupby(list(fields_df.columns)).sum().reset_index()

    #print (group_sum_df)

    merged_df = fields_df.merge(group_sum_df, how='left', on = list(fields_df.columns))
    merged_df['prob'].fillna(0, inplace=True)
    #print (merged_df)
    return np.array(merged_df['prob'])

"""
public functions
"""

"""
function get_twitter_attacker_model() gets the probability values for the Twitter attacker model
params: field_map_table: the file name of the field map table, each column is a field, each row contains "0" and "1" values,
"1" means the field is in the group, "0" means the field is not in the group
the first row is the header, the first column is the index
return: a dictionary, the key is the age group, the value is a list of probabilities of each group of fields the attacker knows
"""
def get_twitter_attacker_model(field_map_table):
    fields = pd.read_csv(field_map_table, index_col=0, header=0, sep=',')
    prob_file_list = TWITTER_PROB_FILES
    #prob_dict = compute_joined_prob(field_map_table, prob_file_list, 'twitter')
    prob_dict = {}
    for file_name in prob_file_list:
        file_name_list = file_name.replace('.csv','').split('_')
        age_lower = file_name_list[3]
        age_upper= file_name_list[4]
        prob_list = __get_each_field_prob_list(file_name, fields)
        prob_combined = __get_joined_prob(field_map_table, prob_list)
        prob_dict[(age_lower, age_upper)] = prob_combined
    return prob_dict

"""
function get_regular_attacker_model() gets the probability values for an attacker model in which the probability that each field
is known is specified in the file with name EACH_FIELD_KNOWN_PROB_FILE
params: field_map_table: the file name of the field map table, each column is a field, each row contains "0" and "1" values,
"1" means the field is in the group, "0" means the field is not in the group
the first row is the header, the first column is the index
each_field_known_prob_file: the file name of the file that specifies the probability that each field is known, two columns:
field name and probability, no index column
return: a list of probabilities of each group of fields the attacker knows
"""
def get_regular_attacker_model(field_map_table,each_field_known_prob_file):
    fields_df = pd.read_csv(field_map_table, index_col=0, header=0, sep=',')
    prob_list =[]
    #if EACH_FIELD_KNOWN_PROB_FILE is not specified, by default, the attacker knows everything, worst case scenario
    if each_field_known_prob_file==None:
        for col_name in list(fields_df.columns):
            prob_value = 1
            prob_list.append(prob_value)
    else:
        prob_df = pd.read_csv(each_field_known_prob_file, sep=',', header=0, index_col=None)
        if ATTR_TO_STANDARD_ATTR_MAP!= None:
            prob_df = prob_df.replace(ATTR_TO_STANDARD_ATTR_MAP)

        for col_name in list(fields_df.columns):
            prob_row = prob_df[prob_df['field']==col_name]
            prob_value = 0
            if prob_row.shape[0]>0:
                prob_value = list(prob_row['probability'])[0]
            prob_list.append(prob_value)
    prob_combined = __get_joined_prob(field_map_table, prob_list)
    return prob_combined


"""
function get_voter_attacker_model() gets the probability values for voter registration table attack
params: field_map_table: the file name of the field map table, each column is a field, each row contains "0" and "1" values,
"1" means the field is in the group, "0" means the field is not in the group
the first row is the header, the first column is the index
return: a dictionary, the key is the the combination of residential state and race, the value is a list of probabilities of each group of fields the attacker knows
"""
def get_voter_attacker_model(field_map_table):
    df = pd.read_csv(VOTER_FIELDS_IN_EACH_STATE_FILE, sep=',', header=0, index_col=None)
    df = df.rename (columns = ATTR_TO_STANDARD_ATTR_MAP)

    if 'year_of_birth' in df.columns:
        for col_name in [x for x in df.columns if x!='year_of_birth']:
            if col_name.lower().contains('year') and col_name.lower().contains('birth'):
                df['year_of_birth'] = df['year_of_birth'] + df[col_name]


    state_fields_dict = {}
    for row_index, row_value in df.iterrows():
        curr_state = row_value['state']
        curr_set = ['StreetAddress_PIIState']
        for column_name in ['Gender_GenderIdentity', 'Race_WhatRaceEthnicity', 'year_of_birth']:
            if row_value[column_name]>0:
                curr_set.append(column_name)
        state_fields_dict[curr_state] = curr_set

    prob_dict_raw = {}
    df_prob = pd.read_csv(VOTER_PROBABILITY_BY_STATE_RACE , sep=',', header=0, index_col=None)
    for r_index, race_state_prob in df_prob.iterrows():
        curr_state = race_state_prob['state']
        curr_race = race_state_prob['race']
        curr_prob = race_state_prob['probability']
        curr_set = state_fields_dict[curr_state]
        if curr_state == 'AoUDRC_GeneralizedState':
            prob_dict_raw[(curr_state, curr_race)]=pd.DataFrame({'field_group':[set(curr_set)], 'prob':[ curr_prob]}, index=[0])
        else:
            prob_dict_raw[('PIIState_'+curr_state, curr_race)]=pd.DataFrame({'field_group':[set(curr_set)], 'prob':[ curr_prob]}, index=[0])


    prob_dict = {}
    for raw_key, raw_value in prob_dict_raw.items():
        curr_prob_list = field_group_prob_to_joined_prob_list(field_map_table,raw_value )
        prob_dict[raw_key] = curr_prob_list
    return prob_dict

#function needed
def get_voter_twitter_combined_model(field_map_table):
    voter_model = get_voter_attacker_model(field_map_table)
    twitter_model = get_twitter_attacker_model(field_map_table)
    combined_prob_dict = {}
    for voter_key, voter_value in voter_model.items():
        for twitter_key, twitter_value in twitter_model.items():
            combined_key =tuple( [voter_key, twitter_key])
            combined_prob_array = _combine_two_attacker_models(voter_value, twitter_value, field_map_table)
            combined_prob_dict[combined_key] = combined_prob_array
    return combined_prob_dict


def generate_prob_model_key(key_value, key_type, key_list=None):
    if key_type == 'age':
        age = key_value
        if age<24:

            return ('18','24')
        elif age<30:
            return ('25','30')
        elif age<49:
            return ('30','49')
        elif age<64:
            return ('50','64')
        else:
            return ('65','120')
    elif key_type == 'state':
        state = key_value
        if state in ['','No matching concept']:
            state = 'AoUDRC_GeneralizedState'
        #prob_list = prob_dict[state]
        if state not in key_list:
            state = 'AoUDRC_GeneralizedState'
        return state
    elif key_type == 'race':
        if key_value == '':
            return 'Skip'
        else:
            return key_value

def model_name_to_prob_model_mapping(field_map_table, attacker_model, prob_file_name=None):
    if attacker_model == 'twitter':
        #prob_file_list = ['twitter_field_prob_18_24.csv','twitter_field_prob_25_30.csv','twitter_field_prob_30_49.csv','twitter_field_prob_50_64.csv','twitter_field_prob_65_120.csv']
        #prob_dict = compute_joined_prob(field_map_table, prob_file_list, 'twitter')
        prob_model = get_twitter_attacker_model(field_map_table)
    elif attacker_model == 'worst case':
        prob_model = get_regular_attacker_model(field_map_table)
    elif attacker_model == 'voter':
        #prob_file_list = ['/home/weiyi/datasets/voter_list_stats/voter_list_attacker_prob.csv']
        #prob_dict = compute_joined_prob(field_map_table, prob_file_list, 'voter')
        prob_model = get_voter_attacker_model(field_map_table)

    elif attacker_model == 'voter twitter':
        prob_model = get_voter_twitter_combined_model(field_map_table)
    else:
        #prob_file_list = [attacker_model+'.csv']
        prob_model = get_regular_attacker_model(field_map_table, prob_file_name)
    return prob_model
