# -*- coding: utf-8 -*-

from typing import List
import matplotlib.pyplot as plt
from pandas import DataFrame

class Visualizer:
    """
    This class receives a pandas DataFrame created by evolve class and provides 
    a line chart of the values related to each agent. if boolean variable named
    aggregate is set to True, only the aggregate value of each step is visualized.
    """
    def __init__(DataFrame: DataFrame, aggregate:bool = False, title:str = None, xlabel:str = None, ylabel:str = None, legend: bool = False)
        self.DF = DataFrame
        self.agg = aggregate
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.legend = legend
    
    def __aggregate(self) -> DataFrame:
        """
        This method creates a DataFrame of 1 column with aggregated values of an
        Evolve DataFrame at each step.
        """
        temp_DF = self.DF.cumsum()
        agg_DF = temp_DF.tail(1)
        agg_DF.index = ['aggregate value at step']
        agg_DF = agg_DF.transpose()
        return agg_df
        
    def line_plot(self):
        """
        This method is responsible for visualizing an Evolve DataFrame.
        """
        if self.agg:
            ax = self.__aggregate.plot(title = self.title, legend = self.legend)
            ax.set_xlabel(f"{self.xlabel}")
            ax.set_ylabel(f"{self.ylabel}")
        else:
            plotted_df = self.DF.transpose()
            ax = plotted_df.plot(title = self.title, legend = self.legend)
            ax.set_xlabel(f"{self.xlabel}")
            ax.set_ylabel(f"{self.ylabel}")
            
    
        
        
        
        
    
    