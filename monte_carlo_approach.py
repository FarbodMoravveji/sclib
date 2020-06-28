
import pandas as pd
from sclib.generate_agents import GenAgents
from sclib.agents import Agents
from sclib.evolve import Evolve
from sclib.visualizer import Visualizer

class Average_Path:
    """
    """
    
    def __init__(self, model):
        """
        """
        self._model = model
        self._num_agents = len(model.list_agents)
        
    @property
    def model(self) -> object:
        return self._model
    
    @property
    def num_agents(self) -> object:
        return self._num_agents
    
    
    def average_path(self, i: int, n: int) -> dict:
        """
        A method that simulates n replication of i_step model runs and derives the 
        average path of each agent's working capital.
        """
        model = self.model
        run_num = 1
        indexes = range(self.num_agents)
        dataframes = dict()

        for replication in range(n):
            model.proceed(i)
            wcap_dataframe = model.log_working_capital
            for agent in indexes:
                wcap_vector = wcap_dataframe[wcap_dataframe.index == agent]
                if run_num == 1:
                    index_list = [f'step_{step}' for step in range(1, i+1)]
                    column_list = [f'run_{run_num}']
                    log_path = pd.DataFrame(wcap_vector, index = index_list, columns = column_list)
                    dataframes[f'log_path_for_agent_{agent}'] = log_path
                else:
                    temp_df = pd.DataFrame(wcap_vector, columns = [f'run_{run_num}'])
                    dataframes[f'log_path_for_agent_{agent}'].join(temp_df)
            model.restart_model()
            run_num += 1

        return dataframes        
            
            

