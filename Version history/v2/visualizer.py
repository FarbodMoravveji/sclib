from typing import List
import matplotlib.pyplot as plt
from pandas import DataFrame

class Visualizer:
    """
    This class receives a pandas DataFrame created by evolve class and provides 
    a line chart of the values related to each agent. if boolean variable named
    aggregate is set to True, only the aggregate value of each step is visualized.
    
    """
    def __init__(self, dfrm: DataFrame, aggregate:bool = False):
        """
        constructor
        Inputs:
          dfrm: a pandas DataFrame object present in Evovle obgect.
          aggregate: A boolean parameter which creates a single column DataFrame
          containing aggregated values of dfrm at each step.
           
        Example:
            >>> generate = GenAgents(excel_file)
            >>> agents_object = Agents(generate.list_agents)
            >>> model = Evolve(agents_object)
            >>> ax = Visualize(model.log_working_capital)
            >>> ax.line_plot()
        """
        self.dfrm = dfrm
        self.agg = aggregate

    def __aggregate(self) -> DataFrame:
        """
        This method creates a DataFrame of 1 column with aggregated values of an
        Evolve DataFrame at each step.
        
        Returns:
            A pandas DataFrame consisted of only one column which holds the aggregate
            values at each step.
        """
        temp_df = self.dfrm.cumsum()
        agg_df = temp_df.tail(1)
        agg_df.index = ['aggregate value at step']
        agg_df = agg_df.transpose()
        return agg_df

    def line_plot(self, title:str = None, xlabel:str = None, ylabel:str = None,
                  legend: bool = False , dpi:int = 300) -> None:
        """
        This method is responsible for visualizing an Evolve DataFrame.
        """
        if self.agg:
            ax = self.__aggregate().plot(title = title, legend = legend)
            ax.set_xlabel(f"{xlabel}")
            ax.set_ylabel(f"{ylabel}")
        else:
            plotted_df = self.dfrm.transpose()
            ax = plotted_df.plot(title = title, legend = legend)
            ax.set_xlabel(f"{xlabel}")
            ax.set_ylabel(f"{ylabel}")