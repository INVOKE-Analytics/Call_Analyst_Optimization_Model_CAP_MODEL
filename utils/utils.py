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

def view_alternative(
    df: pd.DataFrame,
    manpower: int,
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
    st.dataframe(schedule)

    understaffed_days = schedule.columns[
        schedule.loc['Required Agents'].astype(int) > manpower
    ]

    st.write(
        'Manpower requirements are not met for days'
        f'{understaffed_days[0]} to {understaffed_days[1]}'
    )
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

            if num_agents <= manpower - len(title) + 1:
                date = future_busday(complete_dates[j], i+1)
                survey_dict[date] = num_agents

        extension_dates[title[j]] = survey_dict

    for k,v in extension_dates.items():
        if bool(v):
            extension_df = pd.DataFrame(v, index=[k])
            extension_df = (
                extension_df
                .astype(int)
                .T
                .drop_duplicates(keep='first')
            )
            st.dataframe(extension_df.T, use_container_width=False)
        else:
            st.write(f'Survey {k} needs a larger extension.')


def left_align(s, props='text-align: center;'):
    return props