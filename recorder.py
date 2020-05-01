# -*- coding: utf-8 -*-
"""
@author: Farbod Moravveji
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from agents import Agents
from generate_agents import GenAgents


class Recorder():
    
    def __init__(self, list_agents):
        
        self.current_step = 0
        self._list_agents = list_agents
        self._n_agents = len(list_agents)

        self.log_working_capital = self.__create_log_wcap_df()
        
    @property
    def n_agents(self) -> int:
        return self._n_agents
    
    @property
    def list_agents(self) -> list:
        return self._list_agents
        
   
    
    def __create_log_wcap_df(self):
        """
        This method creates a dataframe which contains initial working capital 
        values.
        """
        wcv = np.zeros(self.n_agents)                                          # Creating a vector to save initial working capitals into. 
        
        for (i, elem) in enumerate(self.list_agents):
            wcv[i] = elem.working_capital
        
        log_working_capital = pd.DataFrame(wcv, columns=['step 0'])          
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
        
        temp_log_wcap = pd.DataFrame(wcv, columns=[f'step "{self.current_step}"']) # The df containing updated values of working capital.
        self.log_working_capital = pd.concat([self.log_working_capital, temp_log_wcap], axis = 1)       # Updating self.log_wcap 
        
            
        