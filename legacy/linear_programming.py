from ortools.linear_solver import pywraplp
import math

def round_decimals_up(number:float, decimals:int=0):
    '''
    Used to return integral values for call agents.
    '''
    if not isinstance(decimals, int):
        raise TypeError('decimal places must be an integer')
    elif decimals < 0:
        raise ValueError('decimal places has to be 0 or more')
    elif decimals == 0:
        return math.ceil(number)

    factor = 10 ** decimals 
    return math.ceil(number * factor) / factor

def linearoptimizer(df, Number_running_survey, ManPower):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    infinity = solver.infinity()

    DecisionVariable = [solver.IntVar(0.0, infinity, f'X{i}')
                        for i
                        in range(Number_running_survey)]

    # Constraint 1: X_i * CR/day/agent >= Target CR/day
    for idx, var in enumerate(DecisionVariable):
        solver.Add(var * df.iloc[idx, 1] >= df.iloc[idx, 4])

    # Constraint 2: X1 + X2 + ... <= ManPower
    solver.Add(sum(DecisionVariable) == ManPower)

    # Objective, Maximize: SUM(X_i * CR/day/agent) 
    Maxs = [var * df.iloc[idx, 1]
            for idx, var 
            in enumerate(DecisionVariable)]
    solver.Maximize(sum(Maxs))

    return solver.Solve(), [var.solution_value() for var in DecisionVariable]
