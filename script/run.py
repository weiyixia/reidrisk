from reidrisk.utils import DataFrameWithMissingValues
import numpy as np
from reidrisk.utils import MissingPatterns
from reidrisk.attacker import ProbModel
from reidrisk.attacker import Attacker
import pandas as pd

#def test_add_two_prob_model_2():
#    model1 = ProbModel(['age'],np.array([[0],[1]]),np.array([0.5,0.5]))
#    model2 = ProbModel(['gender','race,education'],np.array([[0],[1]]),np.array([0.2,0.8]))
#    model3 = model1 + model2
#    print (model3.fields)
#    print (model3.fields_array)
#    print (model3.prob_list)
#
#test_add_two_prob_model_2()

attack1_df = pd.read_csv('attacker1.csv', header=0, index_col=None, sep=',')
print (attack1_df)

attack1 = Attacker(attack1_df)
print (attack1)

attack2_df = pd.read_csv('attacker2.csv', header=0, index_col=None, sep=',')
print (attack2_df)
attack2 = Attacker(attack2_df)
print (attack2)


combined_attacker = attack1 + attack2
print (combined_attacker)
