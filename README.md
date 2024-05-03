# Call Analyst Optimization Model

## Overview
### Problem Statement
Given concurrent surveys, with different due dates and CR requirements, how do we distribute call agent in order to minimize the total number of extension days required.
This can be formulated as a Multiple Choice Knapsack Problem (src)[https://www.sciencedirect.com/science/article/abs/pii/S014971890900041X]

## Explanation
The code implements the a modified version of [this](https://stackoverflow.com/questions/74503207/knapsack-with-specific-amount-of-items-from-different-groups) stackoverflow answer.

## Installation
Clone this repo using `git clone https://github.com/INVOKE-Solutions/Call_Analyst_Optimization_Model_CAP_MODEL`

## Usage
Run the streamlit webapp using `streamlit run streamlit.py`
To deploy to the streamlit cloud, sign up [here](https://streamlit.io/) and follow the instructions [here](https://docs.streamlit.io/deploy).