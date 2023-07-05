import numpy as np
import pandas as pd
import streamlit as st
from ortools.linear_solver import pywraplp
from utils.linear_programming import round_decimals_up, linearoptimizer
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

st.sidebar.write('''## STEP 1: Input parameters''')
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
st.sidebar.write('''
***
## STEP 2: Survey input details
''')

def Survey_input_details():
    Names = []
    CRs = []
    NoCallReqs = []
    NoDaysRemains = []
    MinCalls = []
    ManpowerAllocateds = []

    for i in range(Number_running_survey):
        st.sidebar.write('#### Please enter survey details as below:')

        Name = st.sidebar.text_input(f'{i}. Survey name ')
        CR = st.sidebar.slider(
            f'{i}. Avg Daily CR/agent ',
            1,
            50,
            10
        )
        NoCallReq = st.sidebar.number_input(
            f'{i}. Remaining CR ',
            1,
            10000
        )
        DueDate = st.sidebar.date_input(
            f'{i}. Target Completion Date', 
            value=np.busday_offset(today, 1, 'forward').tolist(), 
            min_value=today, 
            key=f'{i}_complete_date'
        )

        PlannedCall = int()
        ManpowerAllocated = int()
        Names.append(Name)
        CRs.append(CR) 
        NoCallReqs.append(int(NoCallReq))
        NoDaysRemain = np.busday_count(today, DueDate)
        NoDaysRemains.append(NoDaysRemain)

        if NoDaysRemain != 0:
            MinCall = round_decimals_up(NoCallReq / NoDaysRemain)
            MinCalls.append(int(MinCall))
        else:
            MinCall = NoCallReq / NoDaysRemain
            MinCalls.append(MinCall)

        ManpowerAllocateds.append(ManpowerAllocated)
        st.sidebar.write('***')

    data = {
        'Survey Title': Names,
        'Avg Daily CR/agent': CRs,
        'Remaining CR': NoCallReqs,
        'Remaining Working Days': NoDaysRemains,
        'Target CR/day': MinCalls,
        'Call Agents Allocation': ManpowerAllocateds,
        'Plan CR/day': PlannedCall
    }

    dataframe = pd.DataFrame.from_dict(data)
    return dataframe


def View_results():
    if df.iloc[0, 0] == '':
        st.write('\nPlease fill in the required information\n')
        return None

    if results == pywraplp.Solver.OPTIMAL:
        st.write('#### Surveys Summary')

        for y in range(Number_running_survey):
            df.iloc[y,5] = SolutionValues[y]
            df.iloc[y,6] = SolutionValues[y] * df.iloc[y,1]

        st.write(
            'The algorithm found the optimal call analysts allocation'
            ' to maximize the total plan CR/day & meet the surveys target'
            ' completion date.'
        )
        st.table(df)
        st.write('##### Target vs Plan CR/day')
        columns = [*st.columns(Number_running_survey)]

        for i in range(Number_running_survey):
            try:
                columns[i].write(df.iloc[i, 0])
                columns[i].metric(
                    label='Target CR/day',
                    value=df.iloc[i, 4],
                    help=None
                )
                columns[i].metric(
                    label='Plan CR/day',
                    value=df.iloc[i, 6],
                    delta=int(df.iloc[i, 6] - df.iloc[i, 4]),
                    delta_color='normal',
                    help=None
                )

                agent_difference = (df.iloc[i, 6] - df.iloc[i, 4]) // df.iloc[i, 1] or "0"
                agent_color = 'off' if agent_difference in ('-', '0', 'None') else 'normal'
                columns[i].metric(
                    label='Agents',
                    value=df.iloc[i, 5],
                    delta=str(agent_difference),
                    delta_color=agent_color,
                    help=None
                )

            except Exception as e:
                raise e
                pass

        st.write('\n')
        st.write('##### Remark')
        st.write(
            'The optimization only to make sure all surveys can be'
            ' completed exactly on the target completion date with'
            ' maximum number of total plan CR / day.\nIf the'
            ' different between **plan CR / day** and **target CR / day**'
            ' are skewed toward any of surveys, you can make adjustment'
            ' by tuning the **Target Completion Date** of each surveys.'
        )

    else:
        st.write('##### Surveys Summary')
        df.iloc[:,[5, 6]] = 'Infeasible'

        st.write('\n')
        st.write(
            'The algorithm terminated successfully and determined '
            'that the problem is infeasible.'
        )
        st.table(df)
        st.write('\n')
        st.write('##### Remark')
        st.write(
            'The algorithm unable to find the optimal call agents '
            'allocation to meet the surveys dateline.\nTo re-evaluate '
            'the opmitization, You may replan by:\n1. extending the '
            'surveys **target completion date**.\n2. Increasing the '
            '**total number of call agents**.'
        )


def View_Optimal():
    survey_cr = df['Remaining CR'].tolist()
    survey_rate = df['Avg Daily CR/agent'].tolist()
    survey_day = [0 for _ in range(df.shape[0])]
    
    surveys = list(zip(survey_cr, survey_rate, survey_day))
    max_extension = st.session_state.get('max_extension', 10)
    max_manpower = ManPower

    solutions = survey_extension_solver(
        surveys=surveys,
        max_extension=max_extension,
        max_manpower=max_manpower,
    )
    if solutions:
        solution_df = pd.DataFrame()
        agents, days = solutions[0]
        solution_df = solution_df.assign(
            **{
                'Survey Title': df['Survey Title'],
                'Avg Daily CR/agent': df['Avg Daily CR/agent'],
                'Remaining CR': df['Remaining CR'],
                'Remaining Working Days': days,
                'Target CR/day': df['Remaining CR'] // pd.Series(days),
                'Call Agents Allocation': agents,
                'Plan CR/day': df['Avg Daily CR/agent'] * pd.Series(agents)
            },
        )
        st.table(solution_df)
    else:
        st.write("Solution not found. Either extend the maximum extension or increase manpower.")

# Get Input from user
try:
    df = Survey_input_details()
except Exception as e1:
    st.error(f'e1: {e1}') 

# Calculate Mixed Integer Linear Programming
try:
    results, SolutionValues = linearoptimizer(df, Number_running_survey, ManPower)
except Exception as e2:
    st.error(f'e2: {e2}')


# View result
try:
    veiw = View_results()
    if df.iloc[0, 5] == 'Infeasible' and (df.iloc[:, 3] > 0).all():
        calculate_alternative(df, ManPower, today)
        View_Optimal()

except Exception as e3:
    raise e3
    st.error(f'e3: {e3}')
