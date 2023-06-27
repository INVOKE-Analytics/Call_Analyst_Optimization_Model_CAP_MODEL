from math import ceil
from itertools import repeat

import numpy as np
import pandas as pd
import streamlit as st
from ortools.linear_solver import pywraplp
from linear_programming import round_decimals_up, linearoptimizer

st.write('''
### CALL ANALYST OPTIMIZATION MODEL (CAP MODEL)

#### Description
An optimization model that will guide our call analyst allocation for survey works in order to complete all survey projects in a timely manner.

***
''')

st.sidebar.write('''## STEP 1: Input parameters''')
Number_running_survey = st.sidebar.number_input('How many surveys will be conducted today? (Max: 10)', 1, 10)
ManPower = st.sidebar.number_input('How many call agents we have? (Max: 100)', 1, 100)
today = st.sidebar.date_input("Today's date")
st.sidebar.write('''***
## STEP 2: Survey input details''')

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
        CR = st.sidebar.slider(f'{i}. Avg Daily CR/agent ', 1, 50, 10)
        NoCallReq = st.sidebar.number_input(f'{i}. Remaining CR ', 1, 10000)
        DueDate = st.sidebar.date_input(f'{i}. Target Completion Date',)

        # Somehow this enables the dataframe to deduce the datatype as int
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

    data = {'Survey Title': Names,
            'Avg Daily CR/agent': CRs,
            'Remaining CR': NoCallReqs,
            'Remaining Working Days': NoDaysRemains,
            'Target CR/day': MinCalls,
            'Call Agents Allocation': ManpowerAllocateds,
            'Plan CR/day': PlannedCall}
    dataframe = pd.DataFrame.from_dict(data)
    return dataframe


def View_results():
    if df.iloc[0,0] != '':
        if results == pywraplp.Solver.OPTIMAL:
            st.write('''#### Surveys Summary''')

            for y in range(Number_running_survey):
                df.iloc[y,5] = SolutionValues[y]
                df.iloc[y,6] = SolutionValues[y] * df.iloc[y,1]

            st.write('The algorithm found the optimal call analysts allocation to maximize the total plan CR/day & meet the surveys target completion date.')
            st.table(df)
            st.write('##### Target vs Plan CR/day')
            columns = [*st.columns(Number_running_survey)]

            for i in range(Number_running_survey):
                try:
                    columns[i].write(df.iloc[i, 0])
                    columns[i].metric(label='Target CR/day', value=df.iloc[i, 4], help=None)
                    columns[i].metric(label='Plan CR/day', value=df.iloc[i, 6], delta=int(df.iloc[i, 6]-df.iloc[i, 4]), delta_color='normal', help=None)

                except Exception as e:
                    pass

            st.write('\n')
            st.write('##### Remark')
            st.write('The optimization only to make sure all surveys can be completed exactly on the target completion date with maximum number of total plan CR / day.\nIf the different between **plan CR / day** and **target CR / day** are skewed toward any of surveys, you can make adjustment by tuning the **Target Completion Date** of each surveys.')

        else:
            st.write('''
            ##### Surveys Summary''')
            for y in range(Number_running_survey):
                df.iloc[y,5] = 'Infeasible'
                df.iloc[y,6] = 'Infeasible'

            st.write('\n')
            st.write('The algorithm terminated successfully and determined that the problem is infeasible.')
            st.table(df)
            st.write('\n')
            st.write('##### Remark')
            st.write('The algorithm unable to find the optimal call agents allocation to meet the surveys dateline.\nTo re-evaluate the opmitization, You may replan by:\n1. extending the surveys **target completion date**.\n2. Increasing the **total number of call agents**.')

    else:
        st.write('\n')
        st.write('Please fill in the required information')
        st.write('\n')

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

def left_align(s, props='text-align: center;'):
    return props

def create_table(surveys: list, rates: list, to_df=False):
    # using the c,s,e formulation for surveys with d = e - s + 1
    n = len(surveys)
    m = max([e for c,s,e in surveys])
    table = np.zeros(shape=(n,m))
    data = zip(surveys, rates)

    for idx, ((c, s, e), r) in enumerate(data):
        d = max(1, e-s)
        agents = ceil(c/(r*d))
        table[idx][s:e] = agents

    if to_df:
        table = np.vstack((table, table.sum(axis=0)))
        table = pd.DataFrame(table, columns=[f'Day {i}' for i in range(1, m+1)]).astype(int)
        table.insert(loc=0, column='Surveys', value=[f'{df["Survey Title"].values[0]}' for i in range(1, n+1)]+['Required Call Agents'])
        table.set_index('Surveys', inplace=True)
        return table
    else:
        return table

# View result
try:
    veiw = View_results()
    surveys = list(zip(df['Remaining CR'], repeat(0), df['Remaining Working Days']))
    rates = df['Avg Daily CR/agent']

    schedule = create_table(surveys=surveys, rates=df['Avg Daily CR/agent'], to_df=True)
    delta_agents = np.ceil(df['Remaining CR'] / (df['Avg Daily CR/agent'] * df['Remaining Working Days'].clip(1, None))) - np.ceil(df['Remaining CR'] / (df['Avg Daily CR/agent'] * (df['Remaining Working Days'] + 1)))
    st.write('#### Minimum Agent Requirements')
    st.write('')
    st.table(schedule)

except Exception as e3:
    raise e3
    st.error(f'e3: {e3}')
