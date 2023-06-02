from ortools.linear_solver import pywraplp
import math

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
    i=0
    DecisionVariable = []
    for i in range(Number_running_survey):
        #Decision Variables X0, X1, X2, ... --> Depending on number of surveys
        globals()['X%s' % i] = solver.IntVar(0.0,infinity,'X'+str(i))
        DecisionVariable.append(globals()['X%s' % i])
        #Constraint 1: X * CR/day/agent >= Target CR/day
        solver.Add(globals()['X%s' % i] * df.iloc[i, 1] >= df.iloc[i, 4])
    #Constraint 2: X1 + X2 + ... <= ManPower
    solver.Add(sum(DecisionVariable) == ManPower)

    #Objective 
    q=0
    Maxs = []
    for w in DecisionVariable:
        globals()['Max%s' % i] = w * df.iloc[q, 1]
        Maxs.append(globals()['Max%s' % i])
        q=q+1
    solver.Maximize(sum(Maxs))

    return solver.Solve(), [globals()['X%s' % i].solution_value() for i in range(Number_running_survey)]