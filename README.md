# Call Analyst Optimization Model

## Overview
Linear programming is a simple technique where we depict complex relationships through linear functions and then find the optimum points. The important word in the previous sentence is depicted. The real relationships might be much more complex – but we can simplify them to linear relationships.

## Objective
To build an optimization model that guide our manpower (call agents) allocation for survey works in order to complete all survey projects in a timely manner.

## Dependencies
1. [Streamlit](https://docs.streamlit.io/) - Data Driven Web-based apps
2. [Google OR-Tools](https://developers.google.com/optimization/introduction) - Linear Optimization

## LP Solver
[SCIP](https://www.scipopt.org/)

## Future work
1. Each jobs have it own dateline, to re-visit the solution approach to relocate the manpower once any of the job's dateline has completed.
2. To formulate a mitigation action if the model unable to find an optimal solution.<br />
   i.  To declare dateline as another manipulative vars.<br />
       Remark: Problem with more than 1 manipulative vars can be a non-linear programming<br />
   ii. [Constraint Programming](https://developers.google.com/optimization/cp)<br />
       CP is based on feasibility (finding a feasible solution) rather than optimization (finding an optimal solution) and focuses on the constraints and variables rather than the objective function. The goal may simply be to narrow down a very large set of possible solutions to a more manageable subset by adding constraints to the problem.

## Data Driven Web-based apps application using Streamlit
[Streamlit Apps](https://invoke-analytics-call-analyst-optimization-mod-streamlit-q2rqkk.streamlit.app/)

## Resources
1. [linear programming python](https://realpython.com/linear-programming-python/#linear-programming-solvers)
2. [Introduction to Linear Programming in Python](https://mlabonne.github.io/blog/posts/2022-03-02-linear_programming.html#v.-optimize)
3. [4 Ways to Solve Linear Programming in Python](https://medium.com/@chongjingting/4-ways-to-solve-linear-programming-in-python-b4af36b7894d)
4. [Constraint Programming](https://developers.google.com/optimization/cp)
