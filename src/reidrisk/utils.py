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
        self._tree = self._get_pattern_tree()
        self.linked_patterns = {}
        #iterate through the each row in unique_patterns by index
        #for each row, get the offsprings
        #use the row index as key, offsprings as value
        for i in range(self.unique_patterns.shape[0]):
            self.linked_patterns[i] = self._get_offsprings(i)
        self.pattern_groups = self._get_pattern_groups()

    def _check_values_in_patterns(self):
        if np.max(self.patterns) > 1 or np.min(self.patterns) < 0:
            raise ValueError("The values in the patterns should be 0 or 1")
    def _get_pattern_tree(self):
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
        for key, value in self._tree.items():
            s += 'parent node: '+str(key) + '\n children nodes: ' + str(value) + '\n'
        return s

    def _get_offsprings(self, node):
        if self._tree.get(node, None) is None:
            raise ValueError("The node does not exist")
        else:
            offsrpings = []
            #breadth first search
            #offsprings is all the nodes in the subtree of node except the node itself

            queue = [node]
            while len(queue) > 0:
                curr_node = queue.pop(0)
                offsrpings.append(curr_node)
                if len(self._tree[curr_node]) > 0:
                    queue += self._tree[curr_node]
            offsrpings.remove(node)
            return list(set(offsrpings))

    def _get_index_of_unique_pattern(self):
        unique_pattern_dict = {}
        for i in range(self.unique_patterns.shape[0]):
            unique_pattern_dict[tuple(self.unique_patterns[i])] = i
        return unique_pattern_dict
    def _get_pattern_groups(self):
        #iterate through each row in self.patterns by index
        #for each row, convert it to a tuple, use the tuple as key to get the value from the dictionary
        #append the row index to the value
        #return the dictionary
        unique_pattern_dict = self._get_index_of_unique_pattern()
        pattern_groups = {}
        for i in range(self.patterns.shape[0]):
            pattern = tuple(self.patterns[i])
            pattern_index = unique_pattern_dict[pattern]
            if pattern_groups.get(pattern_index, None) is None:
                pattern_groups[pattern_index] = [i]
            else:
                pattern_groups[pattern_index].append(i)
        return pattern_groups


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
        groups_by_missing = self.missing_patterns.pattern_groups
        u_p = self.missing_patterns.unique_patterns
        group_size = [0]*self.df.shape[0]
        #iterate through pattern_groups by key and value
        groupby_dict = {}
        for pattern_key, row_indexes in groups_by_missing.items():
            #check if u_p[pattern_key] is all 0s
            if np.sum(u_p[pattern_key]) == 0:
                groupby_dict[pattern_key] = len(row_indexes)
            #get the columns that are 1 in u_p[pattern_key]
            else:
                c_df = self.df.iloc[row_indexes, u_p[pattern_key] == 1]
                #group by all the columns in c_df and get the size of each group
                c_count = c_df.groupby(c_df.columns.tolist()).size()
                #convert c_count to a dictionary
                c_count = c_count.to_dict()
                if np.sum(u_p[pattern_key])==1:
                    c_count_tuple = {}
                    for key, value in c_count.items():
                        c_count_tuple[(key,)] = value
                    groupby_dict[pattern_key] = c_count_tuple
                else:
                    groupby_dict[pattern_key] = c_count

        for pattern_key, row_indexes in groups_by_missing.items():
            if np.sum(u_p[pattern_key]) == 0:
                for i in row_indexes:
                    group_size[i] = groupby_dict[pattern_key]
            else:
                c_count = groupby_dict[pattern_key]
                for offspring in self.missing_patterns.linked_patterns[pattern_key]:
                    #get the columns that are 1 in u_p[item]
                    o_count = groupby_dict[offspring]
                    #iterate through c_count by key and value
                    if np.sum(u_p[offspring]) == 0:
                        for key, value in c_count.items():
                            c_count[key] += o_count
                    else:
                        c_cols = np.where(u_p[pattern_key] == 1)[0]
                        o_cols = np.where(u_p[offspring] == 1)[0]
                        o_key_indexes = []
                        for col_index in range(len(c_cols)):
                            if c_cols[col_index] in o_cols:
                                o_key_indexes.append(col_index)
                        for key, value in c_count.items():
                            #if key is in o_count
                            o_key = tuple([key[i_o_key] for i_o_key in o_key_indexes])
                            if o_key in o_count:
                                #add the value of c_count[key] to o_count[key]
                                c_count[key] += o_count[o_key]
                for i in row_indexes:
                    group_size[i] = c_count[tuple(self.df.iloc[i, u_p[pattern_key] == 1])]
        return group_size

