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
    
    def __init__(self, excel_file: str, steps: int):
        generate = GenAgents(excel_file)
        self.model = Agents(generate.list_agents)
        self.model_agents = self.model.list_agents
        self.num_steps = steps
        self.current_step = 0
        self._n_agents = len(self.model_agents)

        self.log_working_capital = self.__create_log_wcap_df()
        
    @property
    def n_agents(self) -> int:
        return self._n_agents
        
   
    
    def __create_log_wcap_df(self):
        """
        This method creates a dataframe which contains initial working capital 
        values.
        """
        wcv = np.zeros(n_agents)                                               # Creating a vector to save initial working capitals into. 
        
        for (i, elem) in enumerate(self.model_agents):
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
        
        for elem in self.model_agents:
            wcv[elem] = elem.working_capital
        
        temp_log_wcap = pd.DataFrame(wcv, columns=[f'step "{self.current_step}"']) # The df containing updated values of working capital.
        self.log_working_capital = pd.concat([self.log_working_capital, temp_log_wcap], axis = 1)       # Updating self.log_wcap 
        
            
        