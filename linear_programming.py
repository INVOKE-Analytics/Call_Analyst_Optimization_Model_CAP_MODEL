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

    #Decision Variables
    # X1, X2 and X3 are integer non-negative variables

    infinity = solver.infinity()

    i=0
    DecisionVariable = []
    while i < Number_running_survey:
        #Decision Variables
        globals()['X%s' % i] = solver.IntVar(0.0,infinity,'X'+str(i))
        DecisionVariable.append(globals()['X%s' % i])
        #Constraints 1
        solver.Add(globals()['X%s' % i] * df.iloc[i, 1] >= df.iloc[i, 4])
        i=i+1
    #Constraints 2
    solver.Add(sum(DecisionVariable) <= ManPower)

    #Objective
    q=0
    Maxs = []
    for w in DecisionVariable:
        globals()['Max%s' % i] = w * df.iloc[q, 1]
        Maxs.append(globals()['Max%s' % i])
        q=q+1
    solver.Maximize(sum(Maxs))
    return solver.Solve()