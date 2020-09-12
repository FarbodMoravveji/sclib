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
        self._file_path = file_path


    def average_pd(self, i: int, n: int, wcap_financing: bool = True, SC_financing: bool = True):
        """
        This method is responsible for calculating the average probability of
        default in each layer after multiple runs.
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