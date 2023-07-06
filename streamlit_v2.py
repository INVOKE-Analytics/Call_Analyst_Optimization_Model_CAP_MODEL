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
st.sidebar.write('## STEP 1: Input parameters')
Number_running_survey = st.sidebar.number_input(
    'How many surveys will be conducted today? (Max: 10)',
    1,
    10
)
ManPower = st.sidebar.number_input(
    'How many call agents we have? (Max: 100)',
    1,
    100
)
today = st.sidebar.date_input(
    'Today\'s date',
    key='current_date'
)
st.sidebar.write(
'''
***
## STEP 2: Survey input details
'''
)

def Survey_input_details():
    survey_names = []
    cr_rates = []
    remaining_cr = []
    remaining_working_days = []
    target_cr_day = []
    allocated_agents = []

    for i in range(Number_running_survey):
        st.sidebar.write('#### Please enter survey details as below:')

        Name = st.sidebar.text_input(f'{i}. Survey name ')
        survey_cr_rate = st.sidebar.slider(
            f'{i}. Avg Daily CR/agent ',
            1,
            50,
            10
        )
        survey_cr = st.sidebar.number_input(
            f'{i}. Remaining CR ',
            1,
            10000
        )
        due_date = st.sidebar.date_input(
            f'{i}. Target Completion Date', 
            value=np.busday_offset(today, 1, 'forward').tolist(), 
            min_value=today, 
            key=f'{i}_complete_date'
        )

        survey_planned_cr = int()
        survey_agents = int()
        survey_names.append(Name)
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
        st.sidebar.write('***')

    data = {
        'Survey Title': survey_names,
        'Avg Daily CR/agent': cr_rates,
        'Remaining CR': remaining_cr,
        'Remaining Working Days': remaining_working_days,
        'Target CR/day': target_cr_day,
        'Call Agents Allocation': allocated_agents,
        'Plan CR/day': survey_planned_cr
    }

    dataframe = pd.DataFrame.from_dict(data)
    return dataframe