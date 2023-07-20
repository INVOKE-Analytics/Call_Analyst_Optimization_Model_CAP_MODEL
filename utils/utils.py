from copy import deepcopy
from math import ceil
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

    solution = [elem for elem in zip(last_array, last_path) if elem[0] != -1]
    solution = sorted(solution, key=lambda tup: tup[0], reverse=True)

    return solution[:top_n]


def survey_extension_solver(
    surveys:list, 
    max_extension:int, 
    max_manpower:int, 
    top_n:int=1) -> dict:
    daily_agents = lambda c, r, d, x: ceil(c / (r * (d + x)))

    problem_dict = [dict.fromkeys([]) for _ in surveys]
    for idx, (cr, rate, day) in enumerate(surveys):
        for extension in range(max_extension):
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
        extend = [max_extension-viable_days[idx][elem]+1
                  for idx, elem
                  in enumerate([tup[1] for tup in path])]
        schedule.append((agent, extend))

    if schedule:
        return schedule
    else:
        print("Solution not found. Either extend the maximum extension or increase manpower.")
        return


def left_align(s, props='text-align: center;'):
    return props