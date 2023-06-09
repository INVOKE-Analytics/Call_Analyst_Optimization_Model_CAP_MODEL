from ortools.linear_solver import pywraplp
import math
import streamlit as st
from gekko import GEKKO



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

def linearoptimizer(df, Number_running_survey, ManPower):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    infinity = solver.infinity()
    #i=0
    DecisionVariable = []
    for i in range(Number_running_survey):
        #Decision Variables X0, X1, X2, ... --> Depending on number of surveys
        globals()['X%s' % i] = solver.IntVar(0.0,infinity,'X'+str(i))
        DecisionVariable.append(globals()['X%s' % i])
        #Constraint 1: X * CR/day/agent >= Target CR/day
        solver.Add(globals()['X%s' % i] * df.iloc[i, 1] >= df.iloc[i, 5])
    #Constraint 2: X1 + X2 + ... <= ManPower
    solver.Add(sum(DecisionVariable) == ManPower)

    #Objective 
    q=0
    Maxs = []
    for w in DecisionVariable:
        globals()['Max%s' % q] = w * df.iloc[q, 1]
        Maxs.append(globals()['Max%s' % q])
        q=q+1
    solver.Maximize(sum(Maxs))

    return solver.Solve(), [globals()['X%s' % i].solution_value() for i in range(Number_running_survey)]

def reevaluation_linear_programming(df, Number_running_survey, ManPower, priority, extend):
    solver1 = pywraplp.Solver.CreateSolver('SCIP')
    infinity = solver1.infinity()
    DecisionVariable_X = []
    DecisionVariable_Y = []
    #DecisionVariable_Y_obj = []
    c=0
    st.dataframe(df)
    for i in df['Survey Title']:
        st.write('Currently looping: ' + str(i)) 
        if i in priority:
            
            #Decision Variables X0, X1, X2, ... --> Depending on number of surveys
            globals()['X%s' % c] = solver1.IntVar(0.0,infinity,'X'+str(c))
            globals()['Y%s' % c] = solver1.IntVar(0.0,infinity,'Y'+str(c))
            DecisionVariable_X.append(globals()['X%s' % c])
            DecisionVariable_Y.append(globals()['Y%s' % c])
            #Constraint 1: X == (Remaining CR) / (Remaining Working Days * Avg Daily CR/agent)
            solver1.Add(globals()['X%s' % c] == (int(df.loc[df['Survey Title'] == i, 'Remaining CR'])) / (int(df.loc[df['Survey Title'] == i, 'Acceptable Remaining Working Days']) * int(df.loc[df['Survey Title'] == i, 'Avg Daily CR/agent'])))
            #Constraint 2: Y == Remaining Working Days
            solver1.Add(globals()['Y%s' % c] == int(df.loc[df['Survey Title'] == i, 'Acceptable Remaining Working Days']))
        else:
            #Decision Variables X0, X1, X2, ... --> Depending on number of surveys
            globals()['X%s' % c] = solver1.IntVar(0.0,infinity,'X'+str(c))
            globals()['Y%s' % c] = solver1.IntVar(0.0,infinity,'Y'+str(c))
            DecisionVariable_X.append(globals()['X%s' % c])
            DecisionVariable_Y.append(globals()['Y%s' % c])
            #DecisionVariable_Y_obj.append(globals()['Y%s' % c])
            #Constraint 3: Y * X * Avg Daily CR/agent >= Remaining CR
            # solver1.Add(globals()['Y%s' % c] * globals()['X%s' % c] * int(df.loc[df['Survey Title'] == i, 'Avg Daily CR/agent']) >= int(df.loc[df['Survey Title'] == i, 'Remaining CR']))
            
            #Constraint 1: X <= (Remaining CR) / (Acceptable Remaining Working Days * Avg Daily CR/agent)
            solver1.Add(globals()['X%s' % c] <= (int(df.loc[df['Survey Title'] == i, 'Remaining CR'])) / (int(df.loc[df['Survey Title'] == i, 'Acceptable Remaining Working Days']) * int(df.loc[df['Survey Title'] == i, 'Avg Daily CR/agent'])))
            #Constraint 2: Y <= Acceptable Remaining Working Days
            solver1.Add(globals()['Y%s' % c] <= int(df.loc[df['Survey Title'] == i, 'Acceptable Remaining Working Days']))
            #Constraint 3: Y * Avg Daily CR/agent/day * X >= Remaining CR
            solver1.Add(globals()['Y%s' % c] * globals()['X%s' % c] * int(df.loc[df['Survey Title'] == i, 'Avg Daily CR/agent']) >= int(df.loc[df['Survey Title'] == i, 'Remaining CR']))
            #Constraint 4: X >= (Remaining CR) / (Y * Avg Daily CR/agent)
            #solver1.Add(globals()['X%s' % c] >= (int(df.loc[df['Survey Title'] == i, 'Remaining CR'])) / globals()['Y%s' % c] * int(df.loc[df['Survey Title'] == i, 'Avg Daily CR/agent']))
            st.write('Noonnnnn')
            #solver1.Add(int(df.loc[df['Survey Title'] == i, 'Remaining CR']) <= globals()['Y%s' % c] * globals()['X%s' % c] * int(df.loc[df['Survey Title'] == i, 'Avg Daily CR/agent']))
        c=c+1          
    #Constraint 3: X1 + X2 + ... <= ManPower
    solver1.Add(sum(DecisionVariable_X) == ManPower)
    
    #Objective 
    q=0
    objs = []
    for w in DecisionVariable_Y:
        globals()['obj%s' % q] = w * df.iloc[q, 9]
        objs.append(globals()['obj%s' % q])
        q=q+1
    solver1.Minimize(sum(objs))
    
    return solver1.Solve(), [globals()['X%s' % i].solution_value() for i in range(Number_running_survey)], [globals()['Y%s' % i].solution_value() for i in range(Number_running_survey)]

def reevaluation_quadratic_programming(df, Number_running_survey, ManPower, priority, extend):
    solver = GEKKO(remote=False)
    DecisionVariable_X = []
    DecisionVariable_Y = []
    c=0
    st.dataframe(df)