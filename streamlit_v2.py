import numpy as np
import pandas as pd
import streamlit as st

from math import ceil
from utils.utils import calculate_alternative, survey_extension_solver

st.write(
    '### CALL ANALYST OPTIMIZATION MODEL (CAP MODEL)\n'
    '\n'
    '#### Description\n'
    'An optimization model that will guide our call analyst '
    'allocation for survey works in order to complete all '
    'survey projects in a timely manner.\n'
    '***'
)
col1, col2 = st.columns(2)

def survey_input_details() -> pd.DataFrame:
    survey_names = []
    cr_rates = []
    remaining_cr = []
    remaining_working_days = []
    target_cr_day = []
    allocated_agents = []

    with col1:
        extension = st.number_input(
            'Maximum extension',
            min_value=0,
            max_value=180,
            value=10,
            key='max_extension'
        )

    with st.sidebar:
        st.write('## STEP 1: Input parameters')
        survey_count = st.number_input(
            'How many surveys will be conducted today? (Max: 10)',
            1,
            10,
            key='survey_count'
        )
        manpower = st.number_input(
            'How many call agents we have? (Max: 100)',
            1,
            100,
            key='manpower'
        )
        today = st.date_input(
            'Today\'s date',
            key='current_date'
        )
        st.write(
        '''
        ***
        ## STEP 2: Survey input details
        '''
        )

        for i in range(survey_count):
            st.write('#### Please enter survey details as below:')

            name = st.text_input(f'{i}. Survey name ')
            survey_cr_rate = st.slider(
                f'{i}. Avg Daily CR/agent ',
                1,
                50,
                10
            )
            survey_cr = st.number_input(
                f'{i}. Remaining CR ',
                1,
                10000
            )
            due_date = st.date_input(
                f'{i}. Target Completion Date', 
                value=np.busday_offset(today, 1, 'forward').tolist(), 
                min_value=today, 
                key=f'{i}_complete_date'
            )

            survey_planned_cr = int()
            survey_agents = int()
            survey_names.append(name)
            cr_rates.append(survey_cr_rate) 
            remaining_cr.append(int(survey_cr))
            survey_day_count = np.busday_count(today, due_date)
            remaining_working_days.append(survey_day_count)

            if survey_day_count != 0:
                survey_target_cr = ceil(survey_cr / survey_day_count)
                target_cr_day.append(int(survey_target_cr))
            else:
                survey_target_cr = survey_cr / survey_day_count
                target_cr_day.append(survey_target_cr)

            allocated_agents.append(survey_agents)
            st.write('***')

    data = {
        'Survey Title': survey_names,
        'Avg Daily CR/agent': cr_rates,
        'Remaining CR': remaining_cr,
        'Remaining Working Days': remaining_working_days,
        'Call Agents Allocation': allocated_agents,
        'Target CR/day': target_cr_day,
        'Plan CR/day': survey_planned_cr
    }

    dataframe = pd.DataFrame.from_dict(data)
    return dataframe


def display_solution(df: pd.DataFrame):
    remaining_cr = df['Remaining CR'].tolist()
    cr_rates = df['Avg Daily CR/agent'].tolist()
    starting_day = [0 for _ in range(df.shape[0])]

    surveys = list(zip(remaining_cr, cr_rates, starting_day))
    max_extension = st.session_state.get('max_extension', 10)
    max_manpower = st.session_state.get('manpower', 1)

    solutions = survey_extension_solver(
        surveys=surveys,
        max_extension=max_extension,
        max_manpower=max_manpower,
        top_n=5
    )

    solution_options = [f'Top {i+1}' for i in range(min(5, len(solutions)))]

    with col2:
        st.selectbox(
            'Select top 5 solution',
            options=solution_options,
            index=0,
            key='top_n'
        )

    if solutions:
        top_n = solution_options.index(st.session_state.get('top_n', 'Top 1'))
        agents, days = solutions[top_n]
        today = st.session_state.get('current_date', None)
        due_dates = np.busday_offset(
            dates=today,
            offsets=days,
            roll='forward'
        )

        solutions_df = pd.DataFrame.from_dict(
            {
                'Survey Title': df['Survey Title'],
                'Avg Daily CR/agent': df['Avg Daily CR/agent'],
                'Remaining CR': df['Remaining CR'],
                'Remaining Working Days': pd.Series(days),
                'Due Date': due_dates,
                'Call Agents Allocation': agents,
                'Target CR/day': np.ceil(df['Remaining CR'] / pd.Series(days)),
                'Plan CR/day': df['Avg Daily CR/agent'] * pd.Series(agents)
            }
        )

        solutions_df = solutions_df.astype(
            {
                'Survey Title':'string',
                'Avg Daily CR/agent': 'int',
                'Remaining CR': 'int',
                'Remaining Working Days': 'int',
                'Due Date': 'string',
                'Call Agents Allocation': 'int',
                'Target CR/day': 'int',
                'Plan CR/day': 'int',
            },
        )
        st.table(solutions_df)
    else:
        st.write(
            'Solution not found.'
            ' Either extend the maximum extension or increase manpower.'
        )

df = survey_input_details()
display_solution(df)