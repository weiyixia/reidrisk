import pandas as pd
import random
import numpy as np
def get_df_for_multi_select(n, all_columns, key_word):
    columns = []
    for field in all_columns:
        if key_word == 'Race_WhatRaceEthnicity':
            if key_word in field and "Hispanic" not in field:
                columns.append(field)
        else:
            if key_word in field:
                columns.append(field)
    sd_rows = []
    for i in range(n):
        curr_value = random.choice(columns)
        curr_row = []
        for v in columns:
            if v == curr_value:
                curr_row.append(curr_value[len(key_word+'_'):])
            else:
                curr_row.append('')
        sd_rows.append(curr_row)
    return pd.DataFrame(columns=columns, data=sd_rows)
fname = '../data/unique_values_in_each_field_registered_tier.csv'
unique_values_df = pd.read_csv(fname)

grouped = unique_values_df.groupby("Column Name")['Unique Values'].apply(list)
values_dict = dict(grouped)
sd = pd.DataFrame()
n = 2000

#get fields that does not contain the following strings: 'Employment_EmploymentStatus', 'Race_WhatRaceEthnicity', 'Gender_GenderIdentity', 'TheBasics_SexualOrientation'
multi_selection_columns_keywords =[ 'Employment_EmploymentStatus', 'Race_WhatRaceEthnicity', 'Gender_GenderIdentity', 'TheBasics_SexualOrientation']

single_selection_columns = []
multi_selection_columns = []
for field in values_dict.keys():
    multi_or_not = False
    for keyword in multi_selection_columns_keywords:
        #check if keyword is a substring of field

        if keyword in field:
            multi_or_not = True
            break
    if not multi_or_not:
        single_selection_columns.append(field)
    else:
        multi_selection_columns.append(field)
print(single_selection_columns)
print(multi_selection_columns)

for field in single_selection_columns:
    value_list = values_dict[field]
    sd[field] = [random.choice(value_list) for i in range(n)]
hispanic_value_list = values_dict['Race_WhatRaceEthnicity_WhatRaceEthnicity_Hispanic']
sd['Race_WhatRaceEthnicity_WhatRaceEthnicity_Hispanic'] = [random.choice(hispanic_value_list) for i in range(n)]

multi_df_list = []
for keyword in multi_selection_columns_keywords:
    multi_df_list.append(get_df_for_multi_select(n, multi_selection_columns, keyword))

# race_columns = []
# for field in multi_selection_columns:
#     if 'Race_WhatRaceEthnicity' in field and 'Hispanic' not in field:
#         race_columns.append(field)
#
# sd_race = get_df_for_multi_select(n, race_columns, 'Race_WhatRaceEthnicity')
#
# gender_columns = []
# for field in multi_selection_columns:
#     if 'Gender_GenderIdentity' in field :
#         gender_columns.append(field)
# sd_gender = get_df_for_multi_select(n, gender_columns, 'Gender_GenderIdentity')
#
#merge all the columns in sd_race to sd
combined_sd = pd.concat([sd]+multi_df_list, axis=1)
combined_sd.to_csv('../data/AoU_DM_2000.csv', sep = ',', header=True, index=False)
