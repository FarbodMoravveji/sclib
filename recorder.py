# -*- coding: utf-8 -*-
"""
@author: Farbod Moravveji
"""
import numpy as np, matplotlib.pyplot as plt, pandas as pd
from agents import Agents
from generate_agents import GenAgents


class Recorder():
    
    def __init__(self, excel_file: str, steps: int):
        generate = GenAgents(excel_file)
        self.model = Agents(generate.list_agents)
        self.model_agents = self.model.list_agents
        self.num_steps = steps
        self.current_step = 0
        
        self.advance = Agents.one_round()
        
        self.log_wcap = self.__create_log_wcap_df()
        
   
    
    def __create_log_wcap_df(self):
        """
        This method creates a dataframe which contains initial working capital 
        values.
        """
        wcm = np.zeros((len(self.model_agents), 1))                            # Creating a vector to save initial working capitals into. 
        
        for elem in self.model_agents:
            wcm[elem] = elem.working_capital
        
        log_wcap = pd.DataFrame(wcm, columns=['step 0'])          
        return log_wcap
    
    
    
    def update_log_wcap(self):
        """
        This method adds a new column to the log_wcap DataFrame after each step.
        The mentioned task is carried out by: 1- Creating a temporary DataFrame
        of the newly updated working capitals, 2- Concatenating the temporary 
        DataFrame with the existing self.log_wcap.
        """
        wcm = np.zeros((len(self.model_agents), 1))                            # Creating a vector to save initial working capitals into. 
        
        for elem in self.model_agents:
            wcm[elem] = elem.working_capital
        
        temp_log_wcap = pd.DataFrame(wcm, columns=[f'step "{self.current_step}"']) # The df containing updated values of working capital.
        self.log_wcap = pd.concat([self.log_wcap, temp_log_wcap],axis=1)       # Updating self.log_wcap 
        
    
    def proceed(self):
        for rep in range(self.steps):
            self.advance
            self.current_step += 1
            self.update_log_wcap()
            
        