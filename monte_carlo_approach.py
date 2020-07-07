"""
The aim of this module is to capture certain behaviors of the model by replicating
a model numerous times.
"""
import pandas as pd
from sclib.generate_agents import GenAgents
from sclib.agents import Agents
from sclib.evolve import Evolve
from sclib.visualizer import Visualizer


class Multiple_Runs:
    """
    The class consisting of methods for capturing the model behavior.
    """
    def __init__(self, Evolve_object):
        """
        This class only receives an Evovle object, it then passes the object to different 
        methods whithin itself to 
        """
        self._Evolve_Object = Evolve_object
        self._num_agents = len(self._Evolve_Object.model.list_agents)
        
    @property
    def Evolve_Object(self) -> object:
        return self._Evolve_Object
    
    @property
    def num_agents(self) -> object:
        return self._num_agents

    def average_path(self, i: int, n: int) -> dict:
        """
        A method that simulates n replication of i_step Evolve_Object runs and
        captures the valid average path of each agent's working capital.
        """
        Evolve_Object = self._Evolve_Object
        run_num = 1
        indexes = range(self._num_agents)
        index_list = [f'step_{step}' for step in range(1, i + 1)]
        dataframes = dict()

        for replication in range(n):
            Evolve_Object.proceed(i)
            wcap_dataframe = Evolve_Object.log_working_capital
            for agent in indexes:
                wcap_vector = wcap_dataframe[wcap_dataframe.index == agent]
                if run_num == 1:
                    # column_list = [f'run_{run_num}']
                    log_path = pd.DataFrame(wcap_vector, index = index_list, columns = [f'run_{run_num}'])
                    dataframes[f'log_path_for_agent_{agent}'] = log_path
                else:
                    temp_df = pd.DataFrame(wcap_vector, index = index_list, columns = [f'run_{run_num}'])
                    dataframes[f'log_path_for_agent_{agent}'].join(temp_df)
            Evolve_Object.restart_model()
            run_num += 1

        return dataframes