from copy import deepcopy
from math import ceil
from itertools import repeat, combinations

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


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


def calculate_alternative(
    df: pd.DataFrame,
    ManPower: int,
    current_date: np.datetime64) -> None:

    cr = df['Remaining CR']
    rates = df['Avg Daily CR/agent']
    days = df['Remaining Working Days'].clip(1, None)
    title = df['Survey Title'].tolist()

    daily_agents = lambda c, r, d, x: np.ceil(c / (r * (d + x)))
    future_busday = lambda date, skip: str(np.busday_offset(date, skip, 'forward'))

    complete_dates = [
        st.session_state.get(f'{i}_complete_date')
        for i 
        in range(len(title))
    ]

    surveys = list(zip(cr, repeat(0), days))
    schedule = create_table(
        surveys=surveys,
        rates=rates,
        survey_title=title
    )
    schedule = schedule.replace('0', '-')
    schedule.columns = [
        future_busday(current_date, i)
        for i 
        in range(max(days))
    ]

    st.write('#### Minimum Agent Requirements')
    st.write(
        'The table shows the minimum number of agents '
        'allocated to each survey for each working day '
        'over the duration of the survey.'
    )
    st.write(f'##### Number of Available Call Agents: {ManPower}')
    st.dataframe(schedule)

    understaffed_days = schedule.columns[
        schedule.loc['Required Agents'].astype(int) > ManPower
    ]

    understaffed_message = 'Manpower requirements are not met for '
    if len(understaffed_days) == 1:
        understaffed_message += f'the day {understaffed_days[0]}.'
    elif len(understaffed_days) > 1:
        understaffed_message += f'days {understaffed_days[0]} to {understaffed_days[-1]}.'
    else:
        understaffed_message = 'Manpower requirements met for all days.'

    st.write(understaffed_message)
    st.write('##### Extension')

    st.write(
        'The table shows the reduction in the number of '
        'call agents required to reduce the minimum number '
        'of call agents for a survey.'
    )
    extension = st.number_input(
        'Maximum extension',
        min_value=0,
        max_value=180,
        value=10
    )

    # Need to prettify this ugly dict comprehension further
    extension_dates = dict()
    for j in range(len(title)):
        survey_dict = dict()

        for i in range(extension):
            num_agents = daily_agents(cr, rates, days, i+1)[j]
            past_num_agents = daily_agents(cr, rates, days, i)[j]

            if (num_agents <= ManPower - len(title) + 1
                and num_agents != past_num_agents):

                date = future_busday(complete_dates[j], i+1)
                survey_dict[date] = num_agents

        extension_dates[title[j]] = survey_dict

    for k,v in extension_dates.items():
        if bool(v):
            extension_df = pd.DataFrame(v, index=[k])
            extension_df = extension_df \
                .astype(int) \
                .T \
                .drop_duplicates(keep='first')
            st.dataframe(extension_df.T, use_container_width=False)

        else:
            st.write(f'Survey {k} needs a larger extension.')


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
        if weights[0][i] != max_weight:
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
        extend = [max_extension-viable_days[idx][elem]
                  for idx, elem
                  in enumerate([tup[1] for tup in path])]
        schedule.append((agent, extend))

    if schedule:
        for i in range(top_n):
            print(", ".join([f"Assign {agents} call agents to survey {idx} for {days} days" 
                             for idx, (agents, days) 
                             in enumerate(zip(*schedule[i]))]).capitalize())
        return schedule
    else:
        print("Solution not found. Either extend the maximum extension or increase manpower.")
        return


def left_align(s, props='text-align: center;'):
    return props