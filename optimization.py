from ast import Num
#from ctypes import alignment
#from timeit import repeat
#import tkinter
#from tkinter import CENTER, Variable, font
from ortools.linear_solver import pywraplp
#import datetime
#from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import math 


st.write("""
### CALL ANALYST OPTIMIZATION MODEL (CAP MODEL)

#### Description
An optimization model that will guide our call analyst allocation for survey works in order to complete all survey projects in a timely manner.

***
""")

st.sidebar.write("""## STEP 1: Input parameters""")
Number_running_survey = st.sidebar.number_input('How many surveys will be conducted today?', 1,10)
ManPower = st.sidebar.number_input('How many call agents we have?', 1,100)
today = st.sidebar.date_input("Today's date")
st.sidebar.write("""***
## STEP 2: Survey input details""")

def round_decimals_up(number:float, decimals:int=0):
    """
    Returns a value rounded up to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.ceil(number)

    factor = 10 ** decimals
    return math.ceil(number * factor) / factor

def Survey_input_details():
    #Number_running_survey = st.slider('How many surveys will be conducted today?', 1,10,5)
    #ManPower = st.slider('How many call agents we have?', 1,40,20)
    i = 1
    Names = []
    CRs = []
    NoCallReqs = []
    NoDaysRemains = []
    MinCalls = []
    PlannedCalls = []
    ManpowerAllocateds = []
    while i <= Number_running_survey:
        st.sidebar.write('#### Please enter survey details as below:')
        Name = st.sidebar.text_input(str(i)+'. Survey name ')
        CR = st.sidebar.slider(str(i)+'. Avg Daily CR/agent ', 1,50,10)
        NoCallReq = st.sidebar.number_input(str(i)+'. Remaining CR ', 1,10000)
        DueDate = st.sidebar.date_input(str(i)+". Target Completion Date",)
        #NoDaysRemain = st.sidebar.number_input(str(i)+'. Days Remaining ', 1,365)
        PlannedCall = int()
        ManpowerAllocated = int()
        Names.append(Name)
        CRs.append(CR) 
        NoCallReqs.append(int(NoCallReq))
        NoDaysRemain = np.busday_count(today,DueDate)
        NoDaysRemains.append(NoDaysRemain)
        if NoDaysRemain != 0:
            MinCall = round_decimals_up(NoCallReq/NoDaysRemain)
            MinCalls.append(int(MinCall))
        else:
            MinCall = NoCallReq/NoDaysRemain
            MinCalls.append(MinCall)      
        ManpowerAllocateds.append(ManpowerAllocated)
        st.sidebar.write('***')
        i = i+1
    data = {'Survey Title':Names,
            'Avg Daily CR/agent':CRs,
            'Remaining CR':NoCallReqs,
            'Remaining Working Days':NoDaysRemains,
            'Target CR/day':MinCalls,
            'Call Agents Allocation': ManpowerAllocateds,
            'Plan CR/day':PlannedCall}
    dataframe = pd.DataFrame.from_dict(data)
    return dataframe

df = Survey_input_details()
#st.write("""
#### Surveys Summary""")

solver = pywraplp.Solver.CreateSolver('SCIP')

#Decision Variables
# X1, X2 and X3 are integer non-negative variables

infinity = solver.infinity()

i=0
DecVar = []
while i < Number_running_survey:
    #Decision Variables
    globals()['X%s' % i] = solver.IntVar(0.0,infinity,'X'+str(i))
    DecVar.append(globals()['X%s' % i])
    #Constraints 1
    solver.Add(globals()['X%s' % i] * df.iloc[i, 1] >= df.iloc[i, 4])
    i=i+1
#Constraints 2
solver.Add(sum(DecVar) <= ManPower)

#Objective
q=0
Maxs = []
for w in DecVar:
    globals()['Max%s' % i] = w * df.iloc[q, 1]
    Maxs.append(globals()['Max%s' % i])
    q=q+1
solver.Maximize(sum(Maxs))
status = solver.Solve()

def left_align(s, props='text-align: center;'):
    return props

if df.iloc[0,0] != '':
    if status == pywraplp.Solver.OPTIMAL:
        st.write("""
        #### Surveys Summary""")
        y=0
        while y < Number_running_survey:
            df.iloc[y,5] = globals()['X%s' % y].solution_value()
            df.iloc[y,6] = globals()['X%s' % y].solution_value() * df.iloc[y,1]
            y=y+1
        st.write('The algorithm found the optimal call analysts allocation to maximize the total plan CR/day & meet the surveys target completion date.')
        st.table(df)
        st.write('##### Target vs Plan CR/day')
        if Number_running_survey == 1:
            col0 = st.columns(1)
        elif Number_running_survey == 2:
            col0,col1 = st.columns(2)
        elif Number_running_survey == 3:
            col0,col1,col2 = st.columns(3)
        elif Number_running_survey == 4:
            col0,col1,col2,col3 = st.columns(4)
        elif Number_running_survey == 5:
            col0,col1,col2,col3,col4 = st.columns(5)
        elif Number_running_survey == 6:
            col0,col1,col2,col3,col4,col5 = st.columns(6)
        elif Number_running_survey == 7:
            col0,col1,col2,col3,col4,col5,col6 = st.columns(7)
        elif Number_running_survey == 8:
            col0,col1,col2,col3,col4,col5,col6,col7 = st.columns(8)
        elif Number_running_survey == 9:
            col0,col1,col2,col3,col4,col5,col6,col7,col8 = st.columns(9)
        else:
            col0,col1,col2,col3,col4,col5,col6,col7,col8,col9 = st.columns(10)
        
        try:
            col0.write(df.iloc[0,0])
            col0.metric(label='Target CR/day', value= df.iloc[0,4], help=None)
            col0.metric(label='Plan CR/day', value= df.iloc[0,6], delta=int(df.iloc[0,6]-df.iloc[0,4]), delta_color="normal", help=None)

        except Exception:
            pass
        try:
            col1.write(df.iloc[1,0])
            col1.metric(label='Target CR/day', value= df.iloc[1,4], help=None)
            col1.metric(label='Plan CR/day', value= df.iloc[1,6], delta=int(df.iloc[1,6]-df.iloc[1,4]), delta_color="normal", help=None)
        except Exception:
            pass  
        try:
            col2.write(df.iloc[2,0])
            col2.metric(label='Target CR/day', value= df.iloc[2,4], help=None)
            col2.metric(label='Plan CR/day', value= df.iloc[2,6], delta=int(df.iloc[2,6]-df.iloc[2,4]), delta_color="normal", help=None)
        except Exception:
            pass
        try:
            col3.write(df.iloc[3,0])
            col3.metric(label='Target CR/day', value= df.iloc[3,4], help=None)
            col3.metric(label='Plan CR/day', value= df.iloc[3,6], delta=int(df.iloc[3,6]-df.iloc[3,4]), delta_color="normal", help=None)
        except Exception:
            pass 
        try:
            col4.write(df.iloc[4,0])
            col4.metric(label='Target CR/day', value= df.iloc[4,4], help=None)
            col4.metric(label='Plan CR/day', value= df.iloc[4,6], delta=int(df.iloc[4,6]-df.iloc[4,4]), delta_color="normal", help=None)
        except Exception:
            pass
        try:
            col5.write(df.iloc[5,0])
            col5.metric(label='Target CR/day', value= df.iloc[5,4], help=None)
            col5.metric(label='Plan CR/day', value= df.iloc[5,6], delta=int(df.iloc[5,6]-df.iloc[5,4]), delta_color="normal", help=None)
        except Exception:
            pass 
        try:
            col6.write(df.iloc[6,0])
            col6.metric(label='Target CR/day', value= df.iloc[6,4], help=None)
            col6.metric(label='Plan CR/day', value= df.iloc[6,6], delta=int(df.iloc[6,6]-df.iloc[6,4]), delta_color="normal", help=None)
        except Exception:
            pass
        try:
            col7.write(df.iloc[7,0])
            col7.metric(label='Target CR/day', value= df.iloc[7,4], help=None)
            col7.metric(label='Plan CR/day', value= df.iloc[7,6], delta=int(df.iloc[7,6]-df.iloc[7,4]), delta_color="normal", help=None)
        except Exception:
            pass
        try:
            col8.write(df.iloc[8,0])
            col8.metric(label='Target CR/day', value= df.iloc[8,4], help=None)
            col8.metric(label='Plan CR/day', value= df.iloc[8,6], delta=int(df.iloc[8,6]-df.iloc[8,4]), delta_color="normal", help=None)
        except Exception:
            pass
        try:
            col9.write(df.iloc[9,0])
            col9.metric(label='Target CR/day', value= df.iloc[9,4], help=None)
            col9.metric(label='Plan CR/day', value= df.iloc[9,6], delta=int(df.iloc[9,6]-df.iloc[9,4]), delta_color="normal", help=None)
        except Exception:
            pass
        st.write('\n')
        st.write('##### Remark')
        st.write('The optimization only to make sure all surveys can be completed exactly on the target completion date with maximum number of total plan CR / day.\nIf the different between **plan CR / day** and **target CR / day** are skewed toward any of surveys, you can make adjustment by tuning the **Target Completion Date** of each surveys.')
    else:
        st.write("""
        #### Surveys Summary""")
        y=0
        while y < Number_running_survey:
            df.iloc[y,5] = 'Infeasible'
            df.iloc[y,6] = 'Infeasible'
            y=y+1
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
