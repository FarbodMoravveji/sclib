import math
import copy
from typing import List
from math import log
import numpy as np
import pandas as pd
from pandas import DataFrame
from sclib.agent import Agent

list_agents: List[Agent]
current_step: int

class Recorder:
    """
    A class responsible for keeping tracks of the values of variables and time steps
    within the model.
    """
    def __init__(self, list_agents):
        """
        constructor
         Input:
           list_Agent: A list of Agent objects.
        """        
        self.current_step = 0
        self.list_agents = list_agents
        self._n_agents = len(list_agents)
        self.__break_list()
        self.__check_duplicate_id()
        self.__layers_fulfilled()
        self._log_working_capital = self.__dummy_log_working_capital
        self._log_financing = self.__dummy_log_financing()
        self._log_dp = self.__dummy_log_default()
        self._log_SCF = self.__dummy_log_SCF()
        self._log_total_assets = self.__dummy_log_total_assets()
        self._log_total_liabilities = self.__dummy_log_total_liabilities()
        self._log_equity = self.__dummy_log_equity()

        self._initial_list_agents = copy.deepcopy(list_agents)
        self.__choose_default_agent_to_replace()

    @property
    def n_agents(self) -> int:
        return self._n_agents

    @property
    def log_working_capital(self) -> DataFrame:
        return self._log_working_capital
    
    @property
    def log_financing(self) -> DataFrame:
        return self._log_financing

    @property
    def log_dp(self) -> DataFrame:
        return self._log_dp

    @property
    def log_SCF(self) -> DataFrame:
        return self._log_SCF

    @property
    def log_total_assets(self) -> DataFrame:
        return self._log_total_assets

    @property
    def log_total_liabilities(self) -> DataFrame:
        return self._log_total_liabilities

    @property
    def log_equity(self) -> DataFrame:
        return self._log_equity


    @property
    def initial_list_agents(self) -> List[Agent]:
        return self._initial_list_agents

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


    def __dummy_log_working_capital(self) -> DataFrame:
        """
        this method creates a temporary dataframe which will be replaced after model
        run is completed.
        *The method log_wcap should be called in the main script before
        visualizing self.log_working_capital.
        """
        a = np.zeros(1)
        df = pd.DataFrame(a)
        return df

    def __dummy_log_financing(self) -> DataFrame:
        """
        this method creates a temporary dataframe which will be replaced after model
        run is completed.
        *The method log_financing should be called in the main script before
        visualizing self.log_financing.
        """
        a = np.zeros(1)
        df = pd.DataFrame(a)
        return df

    def __dummy_log_default(self) -> DataFrame:
        """
        this method creates a temporary dataframe which will be replaced after model
        run is completed.
        *The method log_default_probability should be called in the main script before
        visualizing self.log_default_probability.
        """
        a = np.zeros(1)
        df = pd.DataFrame(a)
        return df

    def __dummy_log_SCF(self) -> DataFrame:
        """
        this method creates a temporary dataframe which will be replaced after model
        run is completed.
        *The method log_supply_chain_financing should be called in the main script before
        visualizing self._log_SCF.
        """
        a = np.zeros(1)
        df = pd.DataFrame(a)
        return df

    def __dummy_log_total_assets(self):
        a = np.zeros(1)
        df = pd.DataFrame(a)
        return df

    def __dummy_log_total_liabilities(self):
        a = np.zeros(1)
        df = pd.DataFrame(a)
        return df

    def __dummy_log_equity(self):
        a = np.zeros(1)
        df = pd.DataFrame(a)
        return df

    def __break_list(self) -> None:
            """
            Creates lists of retailers, manufacturers and suppliers. 
            """
            self.ret_list = [agent for agent in self.list_agents if 
                              agent.role == agent.retailer]                        # Filters list_agents for retailers who should order.
            
            self.man_list = [agent for agent in self.list_agents if 
                             agent.role == agent.manufacturer]                     # Filters list_agents for manufacturers.
            
            self.sup_list = [agent for agent in self.list_agents if 
                             agent.role == agent.supplier]

    def __choose_default_agent_to_replace(self):
        defret = copy.deepcopy(self.ret_list[0])
        defman = copy.deepcopy(self.man_list[0])
        defsup = copy.deepcopy(self.sup_list[0])
        self.defaul_retailer = copy.deepcopy(defret)
        self.default_manufacturer = copy.deepcopy(defman)
        self.default_supplier = copy.deepcopy(defsup)

    # def __remember_initial_state(self) -> None:
    #     """
    #     This method is used in __init__ in order to save the initial state
    #     of model, that is combined of the initial state of list_agents, 
    #     the current step and logs for working capital, delivery and orders.
    #     """
    #     self._initial_list_agents = self.list_agents
    #     self._initial_log_working_capital = self._log_working_capital
    #     self._initial_log_orders = self._log_orders
    #     self._initial_log_delivery = self._log_delivery
   
    # def restart_model(self):
    #     """
    #     This method brings the model back to its initial state.
    #     """
    #     self.list_agents = self._initial_list_agents
    #     self._log_working_capital = self._initial_log_working_capital
    #     self._log_orders = self._initial_log_orders
    #     self._log_delivery = self._initial_log_delivery
    #     self.current_step = 0

    def log_wcap(self, proceed_steps: int, final_list_agents: list) -> None:
        """
        This method creates a DataFrame with working_capital amounts.
        Receives:
            proceed_steps = number of steps the model has been proceeded (equal to the value passed to the model.procced() method).
            final_list_agents = The final agents_object.list_agent.
            """
        v = [f'step_{i}' for i in range(1, proceed_steps + 1)]
        total_agents = len(final_list_agents)
        matrix = np.zeros([total_agents, proceed_steps])
        for agent in final_list_agents:
            aid = agent.agent_id
            for (amount, step) in agent.list_working_capital:
                matrix[aid][step - 1] = amount
        log_wcap = pd.DataFrame(matrix, columns = v)
        self._log_working_capital = log_wcap

    def log_short_term_financing(self, proceed_steps: int, final_list_agents: list) -> None:
        """
        This method creates a DataFrame with financing amounts. 
        Receives:
            proceed_steps = number of steps the model has been proceeded (equal to the value passed to the model.procced() method).
            final_list_agents = The final agents_object.list_agent.
        """
        v = [f'step_{i}' for i in range(1, proceed_steps + 1)]
        total_agents = len(final_list_agents)
        matrix = np.zeros([total_agents, proceed_steps])
        for agent in final_list_agents:
            aid = agent.agent_id
            for (amount, step, _) in agent.financing_history:
                matrix[aid][step - 1] = amount
        log_financing = pd.DataFrame(matrix, columns = v)
        self._log_financing = log_financing

    def log_default_probability(self, proceed_steps: int, final_list_agents: list) -> None:
        """
        This method creates a DataFrame showing probability of default for each agent at each step.
        Receives:
            proceed_steps = number of steps the model has been proceeded (equal to the value passed to the model.procced() method).
            final_list_agents = The final agents_object.list_agent.
        """
        v = [f'step_{i}' for i in range(301, proceed_steps + 1)]
        total_agents = len(final_list_agents)
        matrix = np.ones([total_agents, proceed_steps - 300])
        for agent in final_list_agents:
            aid = agent.agent_id
            for (amount, step) in agent.default_probability_history:
                matrix[aid][step - 301] = amount
        log_dp = pd.DataFrame(matrix, columns = v)
        self._log_dp = log_dp

    def log_supply_chain_financing(self, proceed_steps: int, final_list_agents: list) -> None:
        """
        This method creates a DataFrame for the values of SCF financing for each agent at each step.
        Receives:
            proceed_steps = number of steps the model has been proceeded (equal to the value passed to the model.procced() method).
            final_list_agents = The final agents_object.list_agent.
        """
        v = [f'step_{i}' for i in range(1, proceed_steps + 1)]
        total_agents = len(final_list_agents)
        matrix = np.zeros([total_agents, proceed_steps])
        for agent in final_list_agents:
            aid = agent.agent_id
            for (amount, step) in agent.SCF_history:
                matrix[aid][step - 1] = amount
        log_scf = pd.DataFrame(matrix, columns = v)
        self._log_SCF = log_scf

    def log_assets(self, proceed_steps: int, final_list_agents: list) -> None:
        """
        This method creates a DataFrame of total assets for each agent at each step.
        Receives:
            proceed_steps = number of steps the model has been proceeded (equal to the value passed to the model.procced() method).
            final_list_agents = The final agents_object.list_agent.
        """
        v = [f'step_{i}' for i in range(1, proceed_steps + 1)]
        total_agents = len(final_list_agents)
        matrix = np.zeros([total_agents, proceed_steps])
        for agent in final_list_agents:
            aid = agent.agent_id
            for (amount, step) in agent.total_assets_history:
                matrix[aid][step - 1] = amount
        log_assets = pd.DataFrame(matrix, columns = v)
        self._log_total_assets = log_assets

    def log_liabilities(self, proceed_steps: int, final_list_agents: list) -> None:
        """
        This method creates a DataFrame of total liabilities for each agent at each step.
        Receives:
            proceed_steps = number of steps the model has been proceeded (equal to the value passed to the model.procced() method).
            final_list_agents = The final agents_object.list_agent.
        """
        v = [f'step_{i}' for i in range(1, proceed_steps + 1)]
        total_agents = len(final_list_agents)
        matrix = np.zeros([total_agents, proceed_steps])
        for agent in final_list_agents:
            aid = agent.agent_id
            for (amount, step) in agent.total_liabilities_history:
                matrix[aid][step - 1] = amount
        log_liab = pd.DataFrame(matrix, columns = v)
        self._log_total_liabilities = log_liab

    def log_Equity(self, proceed_steps: int, final_list_agents: list) -> None:
        """
        This method creates a DataFrame of equity value for each agent at each step.
        Receives:
            proceed_steps = number of steps the model has been proceeded (equal to the value passed to the model.procced() method).
            final_list_agents = The final agents_object.list_agent.
        """
        v = [f'step_{i}' for i in range(1, proceed_steps + 1)]
        total_agents = len(final_list_agents)
        matrix = np.zeros([total_agents, proceed_steps])
        for agent in final_list_agents:
            aid = agent.agent_id
            for (amount, step) in agent.equity_history:
                matrix[aid][step - 1] = amount
        log_E = pd.DataFrame(matrix, columns = v)
        self._log_equity = log_E

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
            if not agent.bankruptcy:
                step_selling_price = np.random.lognormal(mean = log(agent.mu_selling_price), sigma = agent.sigma_selling_price)
                agent.selling_price = step_selling_price

    # def step_profit_dataframe(self) -> DataFrame:
    #     """
    #     Uses the log_working_capital DataFrame to create a new DataFrame containing
    #     step profot values with dimensions identical to log_working_capital.
    #     """
    #     log_step_profit = self.log_working_capital.diff(axis = 1)
    #     log_step_profit.fillna(0, inplace = True)
    #     return log_step_profit
    
