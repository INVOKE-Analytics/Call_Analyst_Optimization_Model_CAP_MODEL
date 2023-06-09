import datetime
from ortools.linear_solver import pywraplp
import streamlit as st
import pandas as pd
import numpy as np
from linear_programming import round_decimals_up, linearoptimizer, reevaluation_linear_programming
from datetime import date
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

def Survey_input_details():
    Names = []
    CRs = []
    NoCallReqs = []
    NoDaysRemains = []
    MinCalls = []
    ManpowerAllocateds = []
    DueDates = []
    FinishDates = []
    for i in range(Number_running_survey):
        st.sidebar.write('#### Please enter survey details as below:')
        Name = st.sidebar.text_input(str(i)+'. Survey name ')
        CR = st.sidebar.slider(str(i)+'. Avg Daily CR/agent ', 1,50,10)
        DueDate = st.sidebar.date_input(str(i)+". Target Completion Date",)
        NoCallReq = st.sidebar.number_input(str(i)+'. Remaining CR ', 1,10000)
        PlannedCall = int()
        ManpowerAllocated = int()
        FinishDate = str()
        DueDates.append(DueDate)
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
        FinishDates.append(FinishDate)
        st.sidebar.write('***')
    data = {'Survey Title':Names,
            'Avg Daily CR/agent':CRs,
            'Remaining CR':NoCallReqs,
            'Due Date':DueDates,
            'Remaining Working Days':NoDaysRemains,
            'Target CR/day':MinCalls,
            'Plan CR/day':PlannedCall,
            'Call Agents Allocation': ManpowerAllocateds,
            'Plan finish Date': FinishDates
            }
    dataframe = pd.DataFrame.from_dict(data)
    return dataframe


def View_results():
    if df.iloc[Number_running_survey-1,2] != 1:
        if results == pywraplp.Solver.OPTIMAL:
            st.write("""
            #### Surveys Summary""")
            for y in df['Survey Title']:
                df.loc[df['Survey Title'] == y, 'Call Agents Allocation'] = SolutionValues[y]
                df.loc[df['Survey Title'] == y, 'Plan CR/day'] = SolutionValues[y] * df.loc[df['Survey Title'] == y, 'Avg Daily CR/agent']
                days = math.ceil(df.loc[df['Survey Title'] == y, 'Remaining CR'] / (SolutionValues[y] * df.loc[df['Survey Title'] == y, 'Avg Daily CR/agent']))
                df.loc[df['Survey Title'] == y, 'Plan finish Date'] = str(np.busday_offset(date.today(),days,roll='forward').astype('datetime64[D]'))
            st.write('The algorithm found the optimal call analysts allocation to maximize the total plan CR/day & meet the surveys target completion date.')
            st.table(df.drop('Due Date', axis=1))
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
                col0.metric(label='Target CR/day', value= df.iloc[0,5], help=None)
                col0.metric(label='Plan CR/day', value= df.iloc[0,6], delta=int(df.iloc[0,6]-df.iloc[0,5]), delta_color="normal", help=None)

            except Exception:
                pass
            try:
                col1.write(df.iloc[1,0])
                col1.metric(label='Target CR/day', value= df.iloc[1,5], help=None)
                col1.metric(label='Plan CR/day', value= df.iloc[1,6], delta=int(df.iloc[1,6]-df.iloc[1,5]), delta_color="normal", help=None)
            except Exception:
                pass  
            try:
                col2.write(df.iloc[2,0])
                col2.metric(label='Target CR/day', value= df.iloc[2,5], help=None)
                col2.metric(label='Plan CR/day', value= df.iloc[2,6], delta=int(df.iloc[2,6]-df.iloc[2,5]), delta_color="normal", help=None)
            except Exception:
                pass
            try:
                col3.write(df.iloc[3,0])
                col3.metric(label='Target CR/day', value= df.iloc[3,5], help=None)
                col3.metric(label='Plan CR/day', value= df.iloc[3,6], delta=int(df.iloc[3,6]-df.iloc[3,5]), delta_color="normal", help=None)
            except Exception:
                pass 
            try:
                col4.write(df.iloc[4,0])
                col4.metric(label='Target CR/day', value= df.iloc[4,5], help=None)
                col4.metric(label='Plan CR/day', value= df.iloc[4,6], delta=int(df.iloc[4,6]-df.iloc[4,5]), delta_color="normal", help=None)
            except Exception:
                pass
            try:
                col5.write(df.iloc[5,0])
                col5.metric(label='Target CR/day', value= df.iloc[5,5], help=None)
                col5.metric(label='Plan CR/day', value= df.iloc[5,6], delta=int(df.iloc[5,6]-df.iloc[5,5]), delta_color="normal", help=None)
            except Exception:
                pass 
            try:
                col6.write(df.iloc[6,0])
                col6.metric(label='Target CR/day', value= df.iloc[6,5], help=None)
                col6.metric(label='Plan CR/day', value= df.iloc[6,6], delta=int(df.iloc[6,6]-df.iloc[6,5]), delta_color="normal", help=None)
            except Exception:
                pass
            try:
                col7.write(df.iloc[7,0])
                col7.metric(label='Target CR/day', value= df.iloc[7,5], help=None)
                col7.metric(label='Plan CR/day', value= df.iloc[7,6], delta=int(df.iloc[7,6]-df.iloc[7,5]), delta_color="normal", help=None)
            except Exception:
                pass
            try:
                col8.write(df.iloc[8,0])
                col8.metric(label='Target CR/day', value= df.iloc[8,5], help=None)
                col8.metric(label='Plan CR/day', value= df.iloc[8,6], delta=int(df.iloc[8,6]-df.iloc[8,5]), delta_color="normal", help=None)
            except Exception:
                pass
            try:
                col9.write(df.iloc[9,0])
                col9.metric(label='Target CR/day', value= df.iloc[9,5], help=None)
                col9.metric(label='Plan CR/day', value= df.iloc[9,6], delta=int(df.iloc[9,6]-df.iloc[9,5]), delta_color="normal", help=None)
            except Exception:
                pass
            st.write('\n')
            st.write('##### Remark')
            st.write('The optimization only to make sure all surveys can be completed exactly on the target completion date with maximum number of total plan CR / day.\nIf the different between **plan CR / day** and **target CR / day** are skewed toward any of surveys, you can make adjustment by tuning the **Target Completion Date** of each surveys.')
        else:
            st.write("""
            #### Surveys Summary""")
            for y in df['Survey Title']:
                df.loc[df['Survey Title'] == y, 'Plan CR/day'] = 'Infeasible'
                df.loc[df['Survey Title'] == y, 'Call Agents Allocation'] = 'Infeasible'
            st.write('\n')
            st.write('The algorithm terminated successfully and determined that the problem is infeasible.')
            st.table(df.drop('Due Date', axis=1))
            st.write('\n')
            st.write('##### Remark')
            st.write('The algorithm unable to find the optimal call agents allocation to meet the surveys dateline using the available number of call agents.')
            #st.write('To re-evaluate the opmitization, You can:\n1. Manually replan by:\n\t1. extending the surveys **target completion date**.\n\t2. Increasing the **total number of call agents**.\n2. Let the algorithm suggest possible optimal solutions')
            re_evaluate = st.selectbox('To re-evaluate the opmitization, please select method of evaluation',('Manual re-evaluation', 'Algorithm suggest possible optimal solutions'))
            if re_evaluate == 'Algorithm suggest possible optimal solutions':
                params = st.selectbox('Please select parameters the algorithm need to re-evaluate?',('Extending the target completion date for less urgent surveys','Additional call agent'))
                if params == 'Extending the target completion date for less urgent surveys':
                    extend = st.multiselect('Please select surveys that can be extend the dateline',(df['Survey Title']))
                    priority = [i for i in df['Survey Title'] if i not in extend]
                    #st.write('# Priority: '+ str(priority))
                    try:
                        for i in extend:
                            st.write('Survey: ' + str(i))
                            date_value = df.loc[df['Survey Title'] == i, 'Due Date'].values[0]
                            globals()['NewDate_%s' % i] = st.date_input('The latest acceptable date to be delayed',key=str('NewDate_' + i), value=date_value)
                            AcceptableNoDaysRemain = np.busday_count(today,globals()['NewDate_%s' % i])
                            #df.loc[df['Survey Title'] == i, 'Acceptable Date'] = globals()['NewDate_%s' % i]
                            df.loc[df['Survey Title'] == i, 'Acceptable Remaining Working Days'] = int(AcceptableNoDaysRemain)
                        #st.dataframe(df)
                    except Exception as e5:
                        st.error(f"e5: {e5}") 
                    try:
                        for i in priority:
                            df.loc[df['Survey Title'] == i, 'Acceptable Remaining Working Days'] = int(df.loc[df['Survey Title'] == i, 'Remaining Working Days'])
                        #st.dataframe(df)
                    except Exception as e6:
                        st.error(f"e6: {e6}") 
                    # Calculate Mixed Integer Linear Programming                    
                    #try:
                    results2, SolutionXValues2, SolutionYValues2 = reevaluation_linear_programming(df, Number_running_survey, ManPower, priority, extend)
                    #except Exception as e3:
                    #    st.error(f"e3: {e3}")
                    
                    # print results
                    c=0
                    if results2 == pywraplp.Solver.OPTIMAL: 
                        st.write(f'The solution is optimal.')
                        for i in df['Survey Title']:
                            df.loc[df['Survey Title'] == i, 'New Remaining Working Days'] = SolutionYValues2[c]
                            df.loc[df['Survey Title'] == i, 'New Call Agents Allocation'] = SolutionXValues2[c]
                            c=c+1
                        st.Dataframe(df)
                    else:
                        st.write(str(results2))
                        st.write(SolutionXValues2)
                        st.write(SolutionYValues2)
                        st.write('The algorithm still unable to find the optimal result. You need to extend more the target completion date for less urgent surveys')
                else:
                    pass


            elif re_evaluate == 'Manual re-evaluation':
                st.write('Please manually re-evaluate by:\n1. extending the surveys **target completion date**.\n2. Increasing the **total number of call agents**.')
            else:
                pass


    else:
        st.write('\n')
        st.write('Please fill in the required information')
        st.write('\n')

# Get Input from user
try:
    df = Survey_input_details()
except Exception as e1:
    st.error(f"e1: {e1}") 

# Calculate Mixed Integer Linear Programming
try:
    results, SolutionValues = linearoptimizer(df, Number_running_survey, ManPower)
except Exception as e2:
    st.error(f"e2: {e2}") 

def left_align(s, props='text-align: center;'):
    return props

# View result
try:
    veiw = View_results()
except Exception as e4:
    st.error(f"e4: {e4}") 


# Do you want the algorithm to suggest possible optimal solutions? Which option do you prefer:
# 1. Add more manpower?
# 2. Sacrifice some of the surveys dateline?
# Please re arrange the surveys according to the urgency
# For each survey, how many days of delay are acceptable?