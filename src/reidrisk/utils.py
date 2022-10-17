"""
author: Weiyi Xia
last modified: October 9, 2022
"""
import numpy as np
import pandas as pd
def generate_all_binary_string(n):
    """
    Given a positive integer number N. The task is to generate all the binary strings of N bits.
    These binary strings should be in ascending order.
    :param n:
    :return an array:
    """
    rows_count = 2**n
    cols_count = n
    binary_array = np.zeros((rows_count, cols_count))
    for i in range(rows_count):
        for j in range(cols_count):
            if (i//(2**j))%2 == 1:
                binary_array[i][j] = 1
    return binary_array.astype(int)

class MissingPatterns:
    def __init__(self, patterns: np.ndarray):
        self.patterns = patterns.astype(int)
        self._check_values_in_patterns() #check if the values in the patterns are 0 or 1
        self.unique_patterns = np.unique(self.patterns, axis=0)
        self.tree = self.get_pattern_tree()

    def _check_values_in_patterns(self):
        if np.max(self.patterns) > 1 or np.min(self.patterns) < 0:
            raise ValueError("The values in the patterns should be 0 or 1")
    def get_pattern_tree(self):
        u_p = self.unique_patterns
        levels = {}
        #every row in u_p is a binary vector
        #get the counts of 1s in each row in u_p
        count_list = []
        for row in u_p:
            count = np.sum(row)
            count_list.append(count)
        #get the unique counts
        unique_count = np.unique(count_list)
        #sort the unique counts in descending order
        unique_count = np.sort(unique_count)[::-1]
        #for each unique count, get the corresponding rows
        for count in unique_count:
            levels[count] = []
            for i in range(len(u_p)):
                if count_list[i] == count:
                    levels[count].append(i)
        tree = {}
        #iterate through unique_count by index
        if len(unique_count) < 1:
            #throw a value exception, pattern can not be empty
            raise ValueError("The patterns can not be empty")

        for i in range(len(unique_count)):
            #if it is the last level
            if i == len(unique_count) - 1:
                for item in levels[unique_count[i]]:
                    tree[item] = []
            else:
                #if it is not the last level
                if unique_count[i] == self.patterns.shape[1]:
                    #if it is the first level
                    for item in levels[unique_count[i]]:
                        tree[item] = levels[unique_count[i+1]]
                else:
                    #if it is not the first level
                    for item in levels[unique_count[i]]:
                        tree[item] = []
                        for next_item in levels[unique_count[i+1]]:
                            if -1 not in u_p[item] - u_p[next_item]:
                                tree[item].append(next_item)
        return tree

    def __str__(self):
        s = 'unique patterns: \n'
        for i, v in enumerate(self.unique_patterns):
            s += str(i) + ': ' + str(v) + '\n'
        for key, value in self.tree.items():
            s += 'parent node: '+str(key) + '\n children nodes: ' + str(value) + '\n'
        return s

    def get_offsprings(self, node):
        if self.tree.get(node, None) is None:
            raise ValueError("The node does not exist")
        else:
            offsrpings = []
            #breadth first search
            #offsprings is all the nodes in the subtree of node except the node itself

            queue = [node]
            while len(queue) > 0:
                curr_node = queue.pop(0)
                offsrpings.append(curr_node)
                if len(self.tree[curr_node]) > 0:
                    queue += self.tree[curr_node]
            offsrpings.remove(node)
            return offsrpings

class DataFrameWithMissingValues:
    def __init__(self, df: pd.DataFrame, null_values):
        self.missing_values = null_values
        self.df = df
        self._replace_missing_with_nan()
        self.missing_patterns = self._get_missing_patterns()

    def _replace_missing_with_nan(self):
        for i in range(self.df.shape[0]):
            for j in range(self.df.shape[1]):
                if self.df.iloc[i,j] in self.missing_values or str(self.df.iloc[i,j]).strip()== '':
                    self.df.iloc[i,j] = np.nan

    def _get_missing_patterns(self):
        return MissingPatterns(np.array(pd.notnull(self.df)).astype(int))

    def get_equivalent_group_size(self):
        pass

