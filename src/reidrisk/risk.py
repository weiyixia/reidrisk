"""
author: Weiyi Xia
"""
from .attacker import Attacker
from .dataset import Dataset

def get_attacker_condition_fields_f(a_c_fields, a_c_fields_map, df_fields):
    '''
    recursive function to get the attacker condition fields in the dataset
    a_c_fields is a list of fields if the attacker only uses one resource
    a_c_fields is a list of lists of fields if the attacker uses multiple resources
    a_c_fields_map is a dictionary of fields if the attacker only uses one resource
    a_c_fields_map is a list of dictionaries of fields if the attacker uses multiple resources
    df_fields is a list of fields in the dataset
    '''
    if a_c_fields is None or len(a_c_fields)==0:
        return a_c_fields
    else:
        item = a_c_fields[0]
        if type(item) is str:
            curr_a_c_fields_map = a_c_fields_map

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

def get_attacker_condition_field_values_mapping(mapping_type, map_to_range_sep = None, attacker_condition_field_values=None, values_in_ds = None):
    if mapping_type == 'use_range':
        if map_to_range_sep is None:
            raise ValueError("map to range separator is not specified")
        else:
            c_dict = {}
            for item in attacker_condition_field_values:
                if type(item) is not str:
                    raise ValueError("attacker condition field value is not a properly represented range")
                elif item.count(map_to_range_sep) != 1:
                    raise ValueError("attacker condition field value is not a properly represented ranges")
                else:
                    lower = int(item.split(map_to_range_sep)[0])
                    upper = int(item.split(map_to_range_sep)[1])
                    for value in range(lower, upper):
                        c_dict[value] = item
            for value in values_in_ds:
                if value not in c_dict:
                    raise ValueError("value in ds are not attacker condition field values")
            return c_dict
def set_attacker_condition_fields_values_map_f(a_c_f_v_m_i, a_c_f_m, a_i, ds):
    '''
    this is a recursive function to set the attacker condition fields values map
    if the attacker only uses one resource, then a_c_f_v_m_i is a dictionary
    each key is a condition field of the dataset, each value is a list,
    the first value in the list is the type of the mapping,
    the second value is the dictionary
    the third value is the separator of the range is the values are mapped to ranges
    the fourth value is a lower bound of the range if the values are mapped to ranges
    the fifth value is a upper bound of the range if the values are mapped to range
    if the attacker uses multiple resources, then a_c_f_v_m_i is a list


    a_c_f_m is attacker_condition_fields_mapping
    if the attacker only uses one resource, then a_c_f_m is a dictionary
    if the attacker uses multiple resources, then a_c_f_m is a list

    a_i is the attacker input
    the attacker_input can be dataframe or a list of dataframes
    if the attacker only uses one resource, then the attacker_input is a dataframe
    if the attacker uses multiple resources, then the attacker_input is a list of dataframes
    '''
    if a_c_f_v_m_i is None or len(a_c_f_v_m_i)==0:
        return a_c_f_v_m_i
    else:
        if type(a_c_f_v_m_i) is dict:
            '''
            this means the attacker only uses one resource
            '''
            a_c_f_v_m_in_ds = {}
            for a_c_k,v in a_c_f_v_m_i.items():
                k = a_c_f_m[a_c_k]
                m_type = v[0]
                m_map = v[1]
                range_sep = None
                if len(v) == 3:
                    range_sep = v[2]
                if m_type == 'exact':
                    a_c_f_v_m_in_ds[k] = None
                elif m_type == 'use_dict':
                    a_c_f_v_m_in_ds[k] = m_map
                elif m_type == 'use_range':
                    a_f_values = list(a_i[a_c_k].unique())
                    f_values_in_ds = ds.dset[k].unique()
                    a_c_f_v_m_in_ds[k] = get_attacker_condition_field_values_mapping(m_type, range_sep, a_f_values, f_values_in_ds)
            return a_c_f_v_m_in_ds
        else:
            return [set_attacker_condition_fields_values_map_f(a_c_f_v_m_i[0],a_c_f_m[0], a_i[0]), ds] + set_attacker_condition_fields_values_map_f(a_c_f_v_m_i[1:],a_c_f_m[1:],a_i[1:], ds)
def get_prob_model_condition_key_f(a_c_f_i_d, a_c_f_v_m, df_row):
    '''
    recursive function to get the attacker model condition key
    a_c_f_i_d is attacker_condition_fields_in_ds
    a_c_f_v_m is attacker_condition_fields_values_map
    df_row is the row of the dataframe
    '''
    if a_c_f_i_d is None or len(a_c_f_i_d)==0:
        return a_c_f_i_d
    else:
        curr_field = a_c_f_i_d[0]
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
class Risk:
    def __init__(
            self,
            dset: Dataset ,
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
        if type(a_k_f_map) is dict:
            return a_k_f_map
        else:
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






    def set_attacker_condition_fields_values_map(self):
        set_attacker_condition_fields_values_map_f(self.attacker_condition_fields_values_mapping_input,self.attacker_condition_fields_map, self.attacker_input, self.dset)


    def get_attacker_condition_fields(self):
        return get_attacker_condition_fields_f(self.attacker.condition_fields,self.attacker_condition_fields_map,self.dset.columns)


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
