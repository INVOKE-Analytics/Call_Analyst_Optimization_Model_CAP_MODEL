import numpy as np
import pandas as pd
import streamlit as st

from math import ceil
from utils.utils import survey_extension_solver, get_const

const_dict = get_const("utils/constants.json")
MAX_CALL_AGENTS = const_dict["MAX_CALL_AGENTS"]
DEFAULT_CR_RATE = const_dict["DEFAULT_CR_RATE"]
MAX_REMAINING_CR = const_dict["MAX_REMAINING_CR"]
MAX_SURVEY_COUNT = const_dict["MAX_SURVEY_COUNT"]
DEFAULT_EXTENSION = const_dict["DEFAULT_EXTENSION"]
MAX_SURVEY_DURATION = const_dict["MAX_SURVEY_DURATION"]
MAX_CR_PER_AGENT_PER_DAY = const_dict["MAX_CR_PER_AGENT_PER_DAY"]

st.write(
    '### CALL ANALYST ALLOCATION OPTMIZATION\n'
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
    hard_deadlines = []


    with col1:
        extension = st.number_input(
            'Maximum Survey Duration',
            min_value=0,
            max_value=MAX_SURVEY_DURATION,
            value=DEFAULT_EXTENSION,
            key='max_extension'
        )

    with st.sidebar:
        st.write('## STEP 1: Input parameters')
        input_type = st.selectbox(
            label='CSV Upload or Manual Input',
            options=['CSV', 'Manual'],
            index=1,
            key='input_type'
        )

        if input_type == 'CSV':
            survey_csv = st.file_uploader(
                label='Upload survey CSV file',
                type='csv',
                key='csv_file'
            )
            manpower = st.number_input(
                label='How many call agents we have? (Max: 100)',
                min_value=1,
                max_value=MAX_CALL_AGENTS,
                value=10,
                key='manpower'
            )

        if st.session_state.get('csv_file', False):
            survey_df = pd.read_csv(
                survey_csv, 
                parse_dates=[4], 
                nrows=10
            )
            survey_df.set_index(
                'index', 
                inplace=True
            )
            survey_df.dropna(inplace=True)

            today = st.date_input(
                label='Today\'s date',
                key='current_date'
            )

            survey_names = survey_df['survey_title'].tolist()
            cr_rates = survey_df['cr_rate_per_agent'].tolist()
            remaining_cr = survey_df['remaining_cr'].astype(int).tolist()
            survey_day_count = np.busday_count(
                today,
                survey_df['deadline'].values.astype('<M8[D]')
            )
            remaining_working_days = survey_day_count.tolist()

            survey_target_cr = np.ceil(survey_df['remaining_cr'] / survey_day_count)
            target_cr_day = survey_target_cr.values.astype(int).tolist()
            allocated_agents = [int() for _ in survey_names]
            survey_planned_cr = int()

        if input_type == 'Manual':
            survey_count = st.number_input(
                'How many surveys will be conducted today? (Max: 10)',
                min_value=1,
                max_value=MAX_SURVEY_COUNT,
                key='survey_count'
            )
            manpower = st.number_input(
                'How many call agents we have? (Max: 100)',
                min_value=1,
                max_value=MAX_CALL_AGENTS,
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
                survey_cr_rate = st.number_input(
                    f'{i}. Avg Daily CR/agent ',
                    min_value=1,
                    max_value=MAX_CR_PER_AGENT_PER_DAY,
                    value=DEFAULT_CR_RATE
                )
                survey_cr = st.number_input(
                    f'{i}. Remaining CR ',
                    min_value=1,
                    max_value=MAX_REMAINING_CR
                )
                deadline = st.checkbox(
                    'Hard Deadline?',
                    value=False,
                    key=f"deadline_{i}"
                )
                due_date = st.date_input(
                    f'{i}. Target Completion Date', 
                    value=np.busday_offset(today, 1, 'forward').tolist(), 
                    min_value=today, 
                    key=f'{i}_complete_date',
                )

                survey_planned_cr = int()
                survey_agents = int()
                survey_names.append(name)
                cr_rates.append(survey_cr_rate) 
                remaining_cr.append(int(survey_cr))
                survey_day_count = np.busday_count(today, due_date)
                remaining_working_days.append(survey_day_count)
                hard_deadlines.append(deadline)

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
        'Plan CR/day': survey_planned_cr,
        'Deadline Days': survey_day_count,
        'Hard Deadlines': hard_deadlines
    }

    dataframe = pd.DataFrame.from_dict(data)
    return dataframe


def display_solution(df: pd.DataFrame):
    remaining_cr = df['Remaining CR'].tolist()
    cr_rates = df['Avg Daily CR/agent'].tolist()

    starting_day = [0 for _ in range(df.shape[0])]
    hard_deadlines = [
        MAX_SURVEY_DURATION if not hard else remainder_days
        for remainder_days, hard 
        in df.loc[:, ['Remaining Working Days', 'Hard Deadlines']].values.tolist()
    ]

    surveys = list(zip(remaining_cr, cr_rates, starting_day))
    max_extension = st.session_state.get('max_extension', DEFAULT_EXTENSION)
    max_manpower = st.session_state.get('manpower', 1)

    solutions = survey_extension_solver(
        surveys=surveys,
        hard_deadlines=hard_deadlines,
        max_extension=max_extension,
        max_manpower=max_manpower,
        top_n=5
    )


    if solutions:
        solution_options = [f'Top {i+1}' for i in range(min(5, len(solutions)))]

        with col2:
            st.selectbox(
                'Select top solutions',
                options=solution_options,
                index=0,
                key='top_n'
            )

        top_n = solution_options.index(st.session_state.get('top_n', 'Top 1'))
        agents, days = solutions[top_n]
        today = st.session_state.get('current_date', None)
        due_dates = np.busday_offset(
            dates=today,
            offsets=days,
            roll='forward'
        )
        leftover_cr = (df['Deadline Days'] * df['Avg Daily CR/agent'] * pd.Series(agents))
        solutions_df = pd.DataFrame.from_dict(
            {
                'Survey Title': df['Survey Title'],
                'Avg Daily CR/agent': df['Avg Daily CR/agent'],
                'Remaining CR': df['Remaining CR'],
                'Total CR by Deadline': leftover_cr,
                'Remaining CR by Deadline': df['Remaining CR'] - leftover_cr,
                'Remaining Working Days': pd.Series(days),
                'Optimal Due Date': due_dates,
                'Call Agents Allocation': agents,
                'Target CR/day': np.ceil(df['Remaining CR'] / df['Deadline Days']),
                'Target CR/Agent/day': np.ceil(df['Remaining CR'] / df['Deadline Days'] / agents),
                'Plan CR/day': df['Avg Daily CR/agent'] * pd.Series(agents),
            }
        )

        solutions_df = solutions_df.astype(
            {
                'Survey Title':'string',
                'Avg Daily CR/agent': 'int',
                'Remaining CR': 'int',
                'Total CR by Deadline': 'int',
                'Remaining CR by Deadline': 'int',
                'Remaining Working Days': 'int',
                'Optimal Due Date': 'string',
                'Call Agents Allocation': 'int',
                'Target CR/day': 'int',
                'Target CR/Agent/day': 'int',
                'Plan CR/day': 'int',
            },
        )
        st.table(solutions_df)
    else:
        st.write(
            'Solution not found.'
            ' Either extend the maximum extension or increase manpower.'
        )


# Main display
try:
    df = survey_input_details()
except UnboundLocalError:
    pass
try:
    if df['Survey Title'].all():
        display_solution(df)
except NameError as e:
    raise(e)
    pass