"""
author: Weiyi Xia
"""
import pandas as pd
import .attacker.Attacker as Attacker
class Risk:
    def __init__(
            self,
            dset: pd.DataFrame,
            attacker_input,
            attacker: Attacker,
            attacker_known_fields_map = [],
            attacker_condition_fields_map = [],
            attacker_condition_fields_values_mapping_input = []
    ):
        self.dset = dset
        self.attacker_input = attacker_input
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
        '''
        if the attacker is a single attacker, attacker_condition_fields_values_mapping_input is a dictionary 
        for example {'age':['exact_match',None]}, each key, value pairs corresponds to a attacker condition fields
        each value is a list
        the first item in the list corresponds to the mapping type, the second item is a dictionary if the first item is 'use_dictionary'
        else, the second item is None 
        
        if the attacker is a combination of two attackers, the attacker_condition_fields_values_mapping_input is 
        a list of dictionaries 
        each list corresponds to an attacker
        for example [{'age':['exact_match',None]},{'race':['exact_match',None]}] 
       
        we will use a recursive function to get the mapping and store it in self.attacker_condition_fields_values_mapping 
        : a list of dictionary of condition fields values mapping for each attacker
        '''
        self.attacker_condition_fields_values_mapping_input = attacker_condition_fields_values_mapping_input
        self.attacker_condition_fields_values_map = self.set_attacker_condition_fields_values_map()
        self.attacker_condition_fields_in_ds = self.get_attacker_condition_fields()
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


    def set_attacker_condition_fields_values_map_f(a_c_f_v_m_i, a_c_f_m, a_i):
        '''
        a is attacker
        a_c_f_v_m_i is attacker_condition_fields_mapping_input
        a_c_f_m is attacker_condition_fields_mapping
        a_i is the attacker input
        the attacker_input can be dataframe or a list of dataframes
        if the attacker only uses one resource, then the attacker_input is a dataframe
        if the attacker uses multiple resources, then the attacker_input is a list of dataframes
        '''
        if a_c_f_v_m_i is None or (type(a_c_f_v_m_i) is list and len(a_c_f_v_m_i)==0) or (type(a_c_f_v_m_i) is dict and len(a_c_f_v_m_i)==0):
            return a_c_f_v_m_i
        else:
            if type(a_c_f_v_m_i) is dict:
                a_c_f_m = {}
                for a_c_k,v in a_c_f_v_m_i.items():
                    k = a_c_f_m[a_c_k]
                    m_type = v[0]
                    m_map = v[1]
                    range_sep = None
                    l_bound = 0
                    u_bound = 100
                    if len(v) == 3:
                        range_sep = v[2]
                    if len(v) == 4:
                        l_bound = v[3]
                    if len(v) == 5:
                        u_bound = v[4]
                    if m_type == 'exact':
                        a_c_f_m[k] = None
                    elif m_type == 'use_dict':
                        a_c_f_m[k] = m_map
                    elif m_type == 'use_range':
                        a_f_values = list(a_i[k].unique())
                        a_c_f_m[k] = get_attacker_condition_field_values_mapping(m_type, range_sep, a_f_values, l_bound, u_bound)
                else:
                    return [set_attacker_condition_fields_values_map_f(a_c_f_v_m_i[0],a_c_f_m[0], a_i[0])] + set_attacker_condition_fields_values_map_f(a_c_f_v_m_i[1:],a_c_f_m[1:],a_i[1:])

    def set_attacker_condition_fields_values_map(self):
        set_attacker_condition_fields_values_map_f(self.attacker_condition_fields_mapping_input,self.attacker_input)


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

    def get_prob_model_condition_key_f(a_c_f_i_d, a_c_f_v_m, df_row):
        '''
        recursive function to get the probability model condition key
        a_c_f_i_d is attacker_condition_fields_in_ds
        a_c_f_v_m is attacker_condition_fields_values_map
        df_row is the row of the dataframe
        '''
        if a_c_f_i_d is None or len(a_c_f_i_d)==0:
            return a_c_f_i_d
        else:
            curr_filed = a_c_f_i_d[0]
            if curr_field is str:
                c_v_in_ds = df_row[curr_field]
                c_v_map = a_c_f_v_m[curr_field]
                c_v_in_a_c = c_v_map[c_v_in_ds]
                return [c_v_in_a_c] + get_prob_model_condition_key_f(a_c_f_i_d[1:],a_c_f_v_m,df_row)
            else:
                curr_a_c_f_i_d = curr_field
                curr_a_c_f_v_m = a_c_f_v_m[0]
                left = get_prob_model_condition_key_f(curr_a_c_f_i_d,curr_a_c_f_v_m,df_row)
                right = get_prob_model_condition_key_f(a_c_f_i_d[1:],a_c_f_v_m[1:],df_row)
                return [left] + right

    def get_prob_model_condition_key(self, df_row):
        '''
        df_row is the row of the dataset
        '''
        a_c_f_i_d = self.attacker_condition_fields_in_ds
        a_c_f_v_m = self.attacker_condition_fields_values_map
        return get_prob_model_condition_key_f(a_c_f_i_d,a_c_f_v_m,df_row)

    def risk_metric(groupsize):
        '''
        this function compute different risk metric based on group size
        implement this function using pattern matching
        '''
        pass
