from math import ceil
from json import loads
from copy import deepcopy
from itertools import repeat

import numpy as np
import pandas as pd
import streamlit as st


def create_table(
    surveys: list,
    rates: list,
    survey_title: list) -> pd.DataFrame:
    '''
    Surveys are a list of tuples (c, s, e)
     - c is the total number of remaining CR
     - s is the start date of the survey
     - e is the end date of the survey
    '''
    n = len(surveys)
    m = max([e for c,s,e in surveys])
    table = np.zeros(shape=(n, m))
    data = zip(surveys, rates)
    dates = [f'Day {i}' for i in range(1, m+1)]

    for idx, ((c, s, e), r) in enumerate(data):
        d = max(1, e - s)
        agents = ceil(c / (r * d))
        table[idx][s:e] = agents

    survey_names = [*survey_title, 'Required Agents']
    table = np.vstack(
        (table, table.sum(axis=0))
    ).astype(int)

    table = pd.DataFrame(
        table,
        columns=dates
    ).astype(str)

    table.insert(
        loc=0,
        column='Surveys',
        value=survey_names
    )

    table.set_index(
        'Surveys',
        inplace=True
    )

    return table


def knapsack_solver(
    weights:list, 
    values:list, 
    max_weight:int, 
    top_n:int=1) -> list:

    if len(weights) == 0:
        return 0

    max_iteration = max_weight + 1

    last_array = [-1 for _ in range(max_iteration)]
    last_path = [[] for _ in range(max_iteration)]

    for i in range(len(weights[0])):
        if weights[0][i] < max_weight:
            weight = weights[0][i]
            if last_array[weight] < values[0][i]:
                last_array[weight] = values[0][i]
                last_path[weight] = [(0, i, weight)]

    for i in range(1, len(weights)):
        current_array = [-1 for _ in range(max_iteration)]
        current_path = [[] for _ in range(max_iteration)]

        for j in range(len(weights[i])):
            weight = weights[i][j]
            value = values[i][j]
            for k in range(weight, max_iteration):
                if last_array[k - weight] > 0:
                    if current_array[k] < last_array[k - weight] + value:
                        current_array[k] = last_array[k - weight] + value
                        current_path[k] = deepcopy(last_path[k - weight])
                        current_path[k].append((i, j, weight))

        last_array = current_array
        last_path = current_path

    solution = [
        elem 
        for elem 
        in zip(last_array, last_path) 
        if elem[0] != -1
    ]
    solution = sorted(
        solution, 
        key=lambda tup: tup[0], 
        reverse=True
    )

    return solution[:top_n]


def survey_extension_solver(
    surveys:list, 
    hard_deadlines:list,
    max_extension:int, 
    max_manpower:int, 
    top_n:int=1) -> dict:
    daily_agents = lambda c, r, d, x: ceil(c / (r * (d + x)))

    problem_dict = [dict.fromkeys([]) for _ in surveys]
    for idx, (cr, rate, day) in enumerate(surveys):
        if hard_deadlines[idx] > 0:
            largest_extension = min(max_extension, hard_deadlines[idx])
        else:
            largest_extension = max_extension

        for extension in range(largest_extension):
            agents = daily_agents(cr, rate, day, extension+1)
            if agents not in problem_dict[idx].values():
                problem_dict[idx][max_extension-extension] = agents

    values = []
    weights = []
    for survey in problem_dict:
        values.append(tuple(survey.keys()))
        weights.append(tuple(survey.values()))

    solution = knapsack_solver(weights, values, max_manpower, top_n)
    viable_days = [list(d.keys()) for d in problem_dict]
    schedule = []

    for idx, (score, path) in enumerate(solution):
        agent = [tup[2] for tup in path]
        extend = [
            max_extension-viable_days[idx][elem]+1
            for idx, elem
            in enumerate([tup[1] for tup in path])
        ]
        schedule.append((agent, extend))

    if schedule:
        return schedule
    else:
        print(
            'Solution not found. '
            'Either extend the maximum extension or increase manpower.'
        )
        return


@st.cache_data(ttl=60*60*24)
def get_const(file_path: str):
    try:
        with open(file_path, 'r') as file:
            const_dict = loads(file.read())
        return const_dict
    except FileNotFoundError as err:
        print(f'Select a valid path. {err}')


def left_align(s, props='text-align: center;'):
    return props

# Explanation 
"""
import copy

# SOMEHOW NEED TO ENSURE EXACTLY ONE ITEM FROM EACH GROUP IS SELECTED
def knapsack_multichoice_onepick(weights, values, max_weight):
    if len(weights) == 0:
        return 0

    # stores the `best` items within their `weight classes`
    # the `weight class` is the collection of all items that share the same weight
    # the `best` item within their `weight class` is the item with the largest value
    last_array = [-1 for _ in range(max_weight + 1)]
    # stores the location of the `best` items within the group
    last_path = [[] for _ in range(max_weight + 1)]

    # Runs through all weights in `group_0`
    print(f"\n{'='*10}\ngroup_0\n{'='*10}")
    for i in range(len(weights[0])):

        print(f"\nweights[0][{i}]", weights[0][i], f"< {max_weight} max_weight")
        if weights[0][i] < max_weight:
            # `item i` is first sorted into it's `weight class` (by placing it into the weights[0][i]-th index of the `last array``)
            # then compare the value of `item i` to the current value stored in the weights[0][i]-th position of the `last array`
            # and discard the least valuable `item`
            # store the position of `item i` in the last_path using the `weight class` index (weights[0][i]-th index)

            print(f"\tlast_array[weights[0][{i}]]:", last_array[weights[0][i]], f"< value[0][{i}]", values[0][i])
            if last_array[weights[0][i]] < values[0][i]:
                last_array[weights[0][i]] = values[0][i]
                last_path[weights[0][i]] = [(0, i)]

                print("\t\tlast_array:", last_array, "last_path:", last_path)

    # Iterate through all other groups and repeat the same process as before for the other groups
    for i in range(1, len(weights)):
        current_array = [-1 for _ in range(max_weight + 1)]
        current_path = [[] for _ in range(max_weight + 1)]
        print(f"\n{'='*10}\ngroup_{i}\n{'='*10}")

        # Runs through all weights in `group_i`
        for j in range(len(weights[i])):
            # iterates through the `weight classes` from weights[i][j] to max_weight
            for k in range(weights[i][j], max_weight + 1):

                print(f"\nlast_array[{k - weights[i][j]}]:", last_array[k - weights[i][j]], "> 0")
                # check the last_weight for any `items` with weights less than or equal to `max_weight` - weight[i][j]
                # this is so that the sum of `j` (the weight of the item we are looking for) and the `weight` of the item
                # that was previously selected will be less than the `max_weight`
                if last_array[k - weights[i][j]] > 0:

                    print(f"\tcurrent_array[{k}]", current_array[k], "<", f"last_array[{k - weights[i][j]}] + values[{i}][{j}]", last_array[k - weights[i][j]], values[i][j])
                    # if the total `value` of the items can be improved by including the currently selected `item`
                    # add the `item`, update the `current_path` and value in the `current_array`
                    if current_array[k] < last_array[k - weights[i][j]] + values[i][j]:
                        current_array[k] = last_array[k - weights[i][j]] + values[i][j]

                        # append the old path from `last_path` to the `current_path`
                        current_path[k] = copy.deepcopy(last_path[k - weights[i][j]])
                        current_path[k].append((i, j))

                        print("\t\tcurrent_array", current_array, "current_path", current_path)

        last_array = current_array
        last_path = current_path
        print("\nlast_array", last_array, "last_path", last_path)


    solution, index_path = get_onepick_solution(last_array, last_path)

    return solution, index_path


def get_onepick_solution(scores, paths):
    scores_paths = list(zip(scores, paths))
    scores_paths_by_score = sorted(scores_paths, key=lambda tup: tup[0],
                                    reverse=True)

    return scores_paths_by_score[0][0], scores_paths_by_score[0][1]
"""

# Worked example
"""
'''
value = total number of days
weight = number of call agents
'''
lst = [(300, 15, 0), (1100, 12, 0), (700, 14, 0), (900, 9, 0), (400, 20, 0), (600, 18, 0), (700, 17, 0)]
max_extension = 10
daily_agents = lambda c, r, d, x: ceil(c / (r * (d + x)))

problem_dict = [dict.fromkeys([]) for _ in lst]
for idx, (cr, rate, day) in enumerate(lst):
    for extension in range(max_extension):
        agents = daily_agents(cr, rate, day, extension+1)
        if agents not in problem_dict[idx]:
            problem_dict[idx][max_extension-extension] = agents
# values, weights = list(zip(*[list(zip(*category.items())) for category in problem_dict]))

print(problem_dict)
print([category.items() for category in problem_dict])
print([list(zip(*category.items())) for category in problem_dict])
print(list(zip(*[list(zip(*category.items())) for category in problem_dict])))

values = []
weights = []
for survey in problem_dict:
    values.append(list(survey.keys()))
    weights.append(list(survey.values()))
print(values, weights)
# manpower = 40

# problem_dict
# W = 40
# k = [list(d.keys()) for d in problem_dict]

# sols = knapsack_multichoice_onepick(weights, values, W)
# agent_ext_lst = []
# for idx, (score, path) in enumerate(sols):
#     ext = [max_extension-k[idx][elem] for idx, elem in enumerate([tup[1] for tup in path])]
#     ags = [tup[2] for tup in path]
#     agent_ext_lst.append((ags, ext))

# # if agent_ext_lst:
# #     print(agent_ext_lst[0])
# #     print([(cr - rate*agents*(days+1)) for (cr, rate, _), agents, days in zip(lst, *agent_ext_lst[0])])
"""