# -*- coding: utf-8 -*-
"""
@author: Farbod Moravveji
"""
from typing import List
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pandas import DataFrame
from agent import Agent
from agents import Agents
from generate_agents import GenAgents


class Recorder:
    """
    A class responsible for keeping tracks of the values of variables and time steps
    within the model.
    """
    
    def __init__(self, list_agents):
        
        self.current_step = 0
        self._list_agents = list_agents
        self._n_agents = len(list_agents)

        self._log_working_capital = self.__create_log_wcap_df()
        
    @property
    def n_agents(self) -> int:
        return self._n_agents
    
    @property
    def list_agents(self) -> List[Agent]:
        return self._list_agents
    
    @property
    def log_working_capital(self) -> DataFrame:
        return self._log_working_capital
        
    
    def __create_log_wcap_df(self) -> DataFrame:
        """
        This method creates a dataframe which contains initial working capital 
        values.
        """
        wcv = np.zeros(self.n_agents)                                          # Creating a vector to save initial working capitals into. 
        
        for (i, elem) in enumerate(self.list_agents):
            wcv[i] = elem.working_capital
        
        log_working_capital = pd.DataFrame(wcv, columns =['step_0'])          
        return log_working_capital

    def update_log_wcap(self):
        """
        This method adds a new column to the log_wcap DataFrame after each step.
        The mentioned task is carried out by: 1- Creating a temporary DataFrame
        of the newly updated working capitals, 2- Concatenating the temporary 
        DataFrame with the existing self.log_wcap.
        """
        wcv = np.zeros(self.n_agents)                                          # Creating a vector to save initial working capitals into. 
        
        for (i, elem) in enumerate(self.list_agents):
            wcv[i] = elem.working_capital
        
        # temp_log_wcap = pd.DataFrame(wcv, columns=[f'step_"{self.current_step}"']) # The df containing updated values of working capital.
        # self._log_working_capital = pd.concat([self._log_working_capital, temp_log_wcap], axis = 1)       # Updating self.log_wcap 
        self.log_working_capital[f'step_"{self.current_step}"'] = wcv
            
        