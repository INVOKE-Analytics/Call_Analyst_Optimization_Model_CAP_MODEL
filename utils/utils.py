from math import ceil

import numpy as np
import pandas as pd

def create_table(surveys: list, rates: list, survey_title: list, to_df=False):
    # using the c,s,e formulation for surveys with d = e - s + 1
    n = len(surveys)
    m = max([e for c,s,e in surveys])
    table = np.zeros(shape=(n, m))
    data = zip(surveys, rates)

    for idx, ((c, s, e), r) in enumerate(data):
        d = max(1, e - s)
        agents = ceil(c / (r * d))
        table[idx][s:e] = agents

    if to_df:
        survey_names = [*survey_title, 'Required Agents']
        table = np.vstack((table, table.sum(axis=0)))
        table = pd.DataFrame(table, columns=[f'Day {i}' for i in range(1, m+1)]).astype(int)
        table.insert(loc=0, column='Surveys', value=survey_names)
        table.set_index('Surveys', inplace=True)
        return table
    else:
        return table

def left_align(s, props='text-align: center;'):
    return props