import math
from math import log
from typing import List
import numpy as np
from sclib.agent import Agent

class Agents:
    """
    This class receives a list containing Agent() objects and is responsible 
    for implementing the behaviours of the model.
    """
    list_agents: List[Agent]
    ret_list: List[Agent]
    man_list: List[Agent]
    sup_list: List[Agent]

    def __init__(self, list_agents) -> None:
        """
        constructor
         Input:
            list_agents: A list containing Agent objects. This list can be
                          constructed manually or it can be extracted from a 
                          GenAgents object as is shown below:
                              
                              list_of_agents = GenAgents(excel_file).list_agents
        """
        self.list_agents = list_agents




                             # Filters list_agents for suppliers.

    
    # def almost_equal_to_zero(self, value: float, abs_tol: float) -> bool:
    #     """
    #     Calculats isclose(value, 0) method with absolute tolerance.
    #     Return Type: bool
        
    #     """
    #     return  math.isclose(value, 0, abs_tol = abs_tol)

    # def find_agent_by_id(self, unique_id: str) -> object:
    #     """
    #     Finds an agent whose id is equivalent to the unique_id proovided.
        
    #     Returns:
    #         An Agent() object with the agent_id that is identical to the uniqu_id
    #         provided as the argument of the method.
    #     """
    #     return [agent for agent in self.list_agents if unique_id == agent.agent_id][0]

    # def realize_selling_prices(self):
    #     for agent in self.list_agents:
    #         if not agent.bankruptcy:
    #             step_selling_price = np.random.lognormal(mean = log(agent.mu_selling_price), sigma = agent.sigma_selling_price)
    #             agent.selling_price = step_selling_price