"""
The aim of this module is to capture certain behaviors of the model by replicating
a model numerous times.
"""
import numpy as np
from sclib.generate_agents import GenAgents
from sclib.evolve import Evolve


class Multiple_Runs:
    """
    The class consisting of methods for capturing the model behavior buy several
    independent runs.
    """
    def __init__(self, file_path: str):
        """

        """
        self._file_path = file_path
        # self._num_agents = len(self._Evolve_Object.model.list_agents)
        
    # @property
    # def Evolve_Object(self) -> object:
    #     return self._Evolve_Object
    
    # @property
    # def num_agents(self) -> object:
    #     return self._num_agents

    # def average_path(self, i: int, n: int) -> dict:
    #     """
    #     A method that simulates n replication of i_step Evolve_Object runs and
    #     captures the valid average path of each agent's working capital.
    #     """
    #     Evolve_Object = self._Evolve_Object
    #     run_num = 1
    #     indexes = range(self._num_agents)
    #     index_list = [f'step_{step}' for step in range(1, i + 1)]
    #     dataframes = dict()

    #     for replication in range(n):
    #         Evolve_Object.proceed(i)
    #         wcap_dataframe = Evolve_Object.log_working_capital
    #         for agent in indexes:
    #             wcap_vector = wcap_dataframe[wcap_dataframe.index == agent]
    #             if run_num == 1:
    #                 # column_list = [f'run_{run_num}']
    #                 log_path = pd.DataFrame(wcap_vector, index = index_list, columns = [f'run_{run_num}'])
    #                 dataframes[f'log_path_for_agent_{agent}'] = log_path
    #             else:
    #                 temp_df = pd.DataFrame(wcap_vector, index = index_list, columns = [f'run_{run_num}'])
    #                 dataframes[f'log_path_for_agent_{agent}'].join(temp_df)
    #         Evolve_Object.restart_model()
    #         run_num += 1

    #     return dataframes

    def average_pd(self, i: int, n: int, wcap_financing: bool = True, SC_financing: bool = True):
        """
        
        """
        matrix_dp = np.zeros([3,n])
        matrix_dn = np.zeros([3,n])
        matrix_model_avg_pd = np.zeros([3,1])
        matrix_model_avg_dn = np.zeros([3,1])
        for repeat in range(n):
            generate = GenAgents(excel_file = self._file_path)
            model = Evolve(generate.list_agents)
            if wcap_financing:
                model.activate_wcap_financing()
            if SC_financing:
                model.activate_SC_financing()
            model.always_shuffle()
            model.proceed(i)
            ret_level = 0
            man_level = 1
            sup_level = 2
            dp_list_ret = list()
            dp_list_man = list()
            dp_list_sup = list()
            dp_ret_avg = 0
            dp_man_avg = 0
            dp_sup_avg = 0
            ret_num_defs = 0
            man_num_defs = 0
            sup_num_defs = 0
            
            for agent in model.ret_list:
                if not agent.bankruptcy:
                   dp_list_ret.append(agent.default_probability)
                else:
                    ret_num_defs += 1

            if dp_list_ret:
                dp_ret_avg = np.mean(dp_list_ret)
            else:
                dp_ret_avg = 1
            
            matrix_dp[ret_level][n - 1] = dp_ret_avg
            matrix_dn[ret_level][n - 1] = ret_num_defs

            for agent in model.man_list:
                if not agent.bankruptcy:
                   dp_list_man.append(agent.default_probability)
                else:
                    man_num_defs += 1

            if dp_list_man:
                dp_man_avg = np.mean(dp_list_man)
            else:
                dp_man_avg = 1

            matrix_dp[man_level][n - 1] = dp_man_avg
            matrix_dn[man_level][n - 1] = man_num_defs
            
            for agent in model.sup_list:
                if not agent.bankruptcy:
                   dp_list_sup.append(agent.default_probability)
                else:
                    sup_num_defs += 1

            if dp_list_sup:
                dp_sup_avg = np.mean(dp_list_sup)
            else:
                dp_sup_avg = 1

            matrix_dp[sup_level][n - 1] = dp_sup_avg
            matrix_dn[sup_level][n - 1] = sup_num_defs
            
        matrix_model_avg_pd = matrix_dp.mean(1)

        matrix_model_avg_dn = matrix_dn.mean(1)
        
        return matrix_model_avg_pd, matrix_model_avg_dn