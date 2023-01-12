from reidrisk.utils import DataFrameWithMissingValues
import numpy as np
from reidrisk.utils import MissingPatterns
from reidrisk.attacker import ProbModel
from reidrisk.attacker import Attacker
from reidrisk.dataset import Dataset
import pandas as pd
import random

ds = Dataset(source='file', dfile='../data/syntheticdata_anonymized.csv')
print (pd.unique(ds.dset['race']))

df = pd.read_csv('../data/syntheticdata_anonymized.csv', header=0, index_col=None, sep=',')
df['age'] = [random.randint(18, 120) for i in range(df.shape[0])]
df['ethnicity'] = df['race'].apply(lambda x: 'hispanic' if x == 'What Race Ethnicity: Hispanic' else 'non-hispanic')
states = pd.read_csv('../data/us_state_list.csv', header=0, index_col=None, sep=',')['State']
df['state'] = [random.choice(states) for i in range(df.shape[0])]
small_df = df.sample(n=50, axis=0)
df.to_csv('../data/syntheticdata_anonymized_with_age_ethnicity_state.csv', index=False, header=True, sep=',')
small_df.to_csv('../data/syntheticdata_anonymized_with_age_ethnicity_state_1000rows.csv', index=False, header=True, sep=',')
#def test_add_two_prob_model_2():
#    model1 = ProbModel(['age'],np.array([[0],[1]]),np.array([0.5,0.5]))
#    model2 = ProbModel(['gender','race,education'],np.array([[0],[1]]),np.array([0.2,0.8]))
#    model3 = model1 + model2
#    print (model3.fields)
#    print (model3.fields_array)
#    print (model3.prob_list)
#
#test_add_two_prob_model_2()
'''
attack1_df = pd.read_csv('attacker1.csv', header=0, index_col=None, sep=',')
print (attack1_df)

attack1 = Attacker(attack1_df)
print (attack1)

attack2_df = pd.read_csv('attacker2.csv', header=0, index_col=None, sep=',')
print (attack2_df)
attack2 = Attacker(attack2_df)
print (attack2)
'''


#combined_attacker = attack1 + attack2
#print (combined_attacker)
