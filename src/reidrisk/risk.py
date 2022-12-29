"""
author: Weiyi Xia
"""
import pandas as pd
import .attacker.Attacker as Attacker
class Risk:
    def __init__(
            self,
            dset: pd.DataFrame,
            attacker: Attacker,
            attacker_known_fields_map = [],
            attacker_condition_fields_map = [],
            attacker_condition_fields_values_map = {}
    ):
        self.dset = dset
        self.attacker = attacker
        self.attacker_known_fields_map = self.set_attacker_known_fields_map(attacker_known_fields_map)
        '''
        attacker_condition_fields_map: a list of dictionary of condition fields for each attacker
            this function checks if the dictionaries are consistent
        with the attacker's condition fields
        every item in the c_f_map corresponds to an item in attacker.condition_fields
        for example, if attacker.condition_fields is [['race','gender'],['age']]
        c_f_map needs to have two items in it
        item 1 is a dictionary that contains two keys: race, gender
        item 2 is a dictionary that contains one key: age
        '''
        self.attacker_condition_fields_map = attacker_condition_fields_map
        self.attacker_condition_fields_in_ds = self.get_attacker_condition_fields()
        self.attacker_condition_field_value_mapping_type = attacker_condition_fields_values_mapping_type
        self.attacker_condition_fields_values_map = attacker_condition_fields_values_map
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


    def get_attacker_condition_fields_f(a_c_fields, a_c_fields_map, df_fields):
        '''
        recursive function to get the attacker condition fields
        '''
        if a_c_fields is None or len(a_c_fields)==0:
            return a_c_fields
        else:
            item = a_c_fields[0]
            if type(item) is str:
               curr_a_c_fields_map = a_c_fields_map[0]

               curr_ds_field = curr_a_c_fields_map.get(item,None)
                if curr_ds_field is None:
                    raise ValueError("attacker condition fields map is not consistent")
                elif curr_ds_field not in df_fields:
                    raise ValueError("attacker condition fields map is not consistent")
                else:
                    return [curr_ds_field] + get_attacker_condition_fields_f(a_c_fields[1:],a_c_fields_map,df_fields)
            else:
                curr_a_c_fields_map = a_c_fields_map[0]
                curr_a_c_fields = item
                left = get_attacker_condition_fields_f(curr_a_c_fields,curr_a_c_fields_map,df_fields)
                right = get_attacker_condition_fields_f(a_c_fields[1:],a_c_fields_map[1:],df_fields)
                return [left] + right
    def get_attacker_condition_fields(self):
        return get_attacker_condition_fields_f(self.attacker.condition_fields,self.attacker_condition_fields_map,self.dset.columns)

    def get_attacker_condition_field_values_mapping(mapping_type, map_to_range_sep = None, attacker_condition_field_values=None, lower_bound=0, upper_bound = 100):
        if mapping_type == 'use_range':
            if map_to_range_sep is None:
                raise ValueError("map to range separator is not specified")
            else:
                c_dict = {}
                for item in attacker_condition_field_values:
                    if type(item) is not str:
                        raise ValueError("attacker condition field values are not ranges")
                    elif map_to_range_sep not in item:
                        raise ValueError("attacker condition field values are not ranges")
                    elif item[0] == map_to_range_sep:
                        lower = lower_bound
                        upper = int(item[1:])
                    elif item[-1] == map_to_range_sep:
                        lower = int(item[:-1])
                        upper = upper_bound
                    else:
                        lower = int(item.split(map_to_range_sep)[0])
                        upper = int(item.split(map_to_range_sep)[1])
                    for value in range(lower,upper):
                        c_dict[value] = item
                return c_dict




    def get_matching_prob_model(self, df_row, attacker_condition,attacker_condition_fields) :
        '''
    def risk_metric(groupsize):

        this function compute different risk metric based on group size
        :return:
        implement this function using pattern matching
        '''
        pass
