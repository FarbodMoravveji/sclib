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
        self.__break_list()
        self.__check_duplicate_id()
        self.__layers_fulfilled()



    def __break_list(self) -> None:
        """
        Creates lists of retailers, manufacturers and suppliers. 
        """
        self.ret_list = [agent for agent in self.list_agents if 
                          agent.role == agent.retailer]                        # Filters list_agents for retailers who should order.
        
        self.man_list = [agent for agent in self.list_agents if 
                         agent.role == agent.manufacturer]                     # Filters list_agents for manufacturers.
        
        self.sup_list = [agent for agent in self.list_agents if 
                         agent.role == agent.supplier]                         # Filters list_agents for suppliers.

    def __check_duplicate_id(self) -> None:
        """
        Checks if list_agents contain any duplicate agent_ids.
        """
        agents_set = set()
        ids = [agent.agent_id for agent in self.list_agents]
        for elem in ids:
            if elem in agents_set:
                raise ValueError(f'__check_duplicate_id: Agents.list_agents contains at least one duplicate id')
            else:
                agents_set.add(elem)

    def __layers_fulfilled(self) -> None:
        """
        This method makes sure that there is at least one agent in each layer        
        """
        role_set = set()
        for elem in self.list_agents:
            role_set.add(elem.role)
        if len(role_set) < 3:
            raise ValueError(f"__layers_fulfilled: At least one layer doesn't contain any agents")
        if len(role_set) > 3:
            raise ValueError(f"__layers_fulfilled: Model should only consist of three layers, not more")

    def almost_equal_to_zero(self, value: float, abs_tol: float) -> bool:
        """
        Calculats isclose(value, 0) method with absolute tolerance.
        Return Type: bool
        
        """
        return  math.isclose(value, 0, abs_tol = abs_tol)

    def find_agent_by_id(self, unique_id: str) -> object:
        """
        Finds an agent whose id is equivalent to the unique_id proovided.
        
        Returns:
            An Agent() object with the agent_id that is identical to the uniqu_id
            provided as the argument of the method.
        """
        return [agent for agent in self.list_agents if unique_id == agent.agent_id][0]

    def realize_selling_prices(self):
        for agent in self.list_agents:
            step_selling_price = np.random.lognormal(mean = log(agent.mu_selling_price), sigma = agent.sigma_selling_price)
            agent.selling_price = step_selling_price