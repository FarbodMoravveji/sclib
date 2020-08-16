from typing import List
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
        self._list_agents = list_agents
        self._n_agents = len(list_agents)

        self._log_working_capital = self.__create_log_wcap_df()
        self._log_financing = self.__dummy_log_financing()
        self._log_default_probability = self.__dummy_log_default()
        # self._log_orders = self.__create_log_orders_df()
        # self._log_delivery = self.__create_log_delivery_df()

        self._initial_list_agents = self._list_agents
        self._initial_log_working_capital = self._log_working_capital
        # self._initial_log_orders = self._log_orders
        # self._initial_log_delivery = self._log_delivery
        # self.__remember_initial_state()

    @property
    def n_agents(self) -> int:
        return self._n_agents

    @property
    def list_agents(self) -> List[Agent]:
        return self._list_agents

    @property
    def log_working_capital(self) -> DataFrame:
        return self._log_working_capital
    
    @property
    def log_financing(self) -> DataFrame:
        return self._log_financing

    @property
    def log_default_probability(self) -> DataFrame:
        return self._log_default_probability

    @property
    def log_orders(self) -> DataFrame:
        return self._log_orders

    @property
    def log_delivery(self) -> DataFrame:
        return self._log_delivery

    @property
    def initial_list_agents(self) -> List[Agent]:
        return self._initial_list_agents

    @property
    def initial_log_working_capital(self) -> DataFrame:
        return self._initial_log_working_capital

    @property
    def initial_log_orders(self) -> DataFrame:
        return self._initial_log_orders

    @property
    def initial_log_delivery(self) -> DataFrame:
        return self._initial_log_delivery

    def __create_log_wcap_df(self) -> DataFrame:
        """
        This method creates a dataframe which contains initial working capital 
        values.
        
        Returns:
            A pandas DataFrame consisted of only one column which holds the initial
            values of working capital related to each agent.
        """
        wcv = np.zeros(self.n_agents)                                          # Creating a vector to save initial working capitals into. 
        
        for (i, elem) in enumerate(self.list_agents):
            wcv[i] = elem.working_capital
        
        log_working_capital = pd.DataFrame(wcv, columns =['step_0'])          
        return log_working_capital
    
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

    # def __create_log_orders_df(self) -> DataFrame:
    #     """
    #     This method creates a dataframe which contains initial order values that 
    #     are equal to zero.
        
    #     Returns:
    #         A pandas DataFrame consisted of only one column which holds zeros
    #         as initial order amounts related to each agent.
    #     """
    #     wcv = np.zeros(self.n_agents)                                          
    #     log_orders = pd.DataFrame(wcv, columns =['step_0'])          
    #     return log_orders

    # def __create_log_delivery_df(self) -> DataFrame:
    #     """
    #     This method creates a dataframe which contains initial deliveries that 
    #     are equal to zero.
        
    #     Returns:
    #         A pandas DataFrame consisted of only one column which holds zeros
    #         as initial delivery amounts related to each agent.
    #     """
    #     wcv = np.zeros(self.n_agents)                                          
    #     log_delivery = pd.DataFrame(wcv, columns =['step_0'])          
    #     return log_delivery

    def __remember_initial_state(self) -> None:
        """
        This method is used in __init__ in order to save the initial state
        of model, that is combined of the initial state of list_agents, 
        the current step and logs for working capital, delivery and orders.
        """
        self._initial_list_agents = self._list_agents
        self._initial_log_working_capital = self._log_working_capital
        self._initial_log_orders = self._log_orders
        self._initial_log_delivery = self._log_delivery
   
    def restart_model(self):
        """
        This method brings the model back to its initial state.
        """
        self._list_agents = self._initial_list_agents
        self._log_working_capital = self._initial_log_working_capital
        self._log_orders = self._initial_log_orders
        self._log_delivery = self._initial_log_delivery
        self.current_step = 0
    
    def update_log_wcap(self) -> None:
        """
        This method adds a new column to the log_wcap DataFrame after each step.
        The mentioned task is carried out by: 1- Creating a temporary DataFrame
        of the newly updated working capitals, 2- Concatenating the temporary 
        DataFrame with the existing agent.working_capital.
        """
        wcv = np.zeros(self.n_agents)                                           
        
        for (i, elem) in enumerate(self.list_agents):
            wcv[i] = elem.working_capital     

        self.log_working_capital[f'step_{self.current_step}'] = wcv

    def log_short_term_financing(self, proceed_steps) -> None:
        """
        Receives:
            proceed_steps = number of steps the model has been proceeded (equal to the value passed to the model.procced() method).
        This method creates a DataFrame with financing amounts. 
        """
        v = [f'step_{i}' for i in range(1, proceed_steps + 1)]
        matrix = np.zeros([self.n_agents, proceed_steps])
        for agent in self.list_agents:
            aid = agent.agent_id
            for (amount, step, _) in agent.financing_history:
                matrix[aid][step - 1] = amount
        log_financing = pd.DataFrame(matrix, columns = v)
        self._log_financing = log_financing

    def log_default_probability(self, proceed_steps) -> None:
        """
        Receives:
            proceed_steps = number of steps the model has been proceeded (equal to the value passed to the model.procced() method).
        This method creates a DataFrame with financing amounts. 
        """
        v = [f'step_{i}' for i in range(301, proceed_steps + 1)]
        matrix = np.zeros([self.n_agents, proceed_steps - 300])
        for agent in self.list_agents:
            aid = agent.agent_id
            for (amount, step) in agent.default_probability_history:
                matrix[aid][step - 301] = amount
        log_default_probability = pd.DataFrame(matrix, columns = v)
        self._log_default_probability = log_default_probability

    # def update_log_orders(self) -> None:
    #     """
    #     This method adds a new column to the log_orders DataFrame after each step.
    #     The mentioned task is carried out by: 1- Creating a temporary DataFrame
    #     of the newly updated order amounts, 2- Concatenating the temporary 
    #     DataFrame with the existing self.log_orders.
    #     """
    #     wcv = np.zeros(self.n_agents)                                          
    #     rle = ['r','m']
    #     for (i, elem) in enumerate(self.list_agents):
    #         if elem.role in rle:
    #             wcv[i] = elem.orders_succeeded
    #         else:
    #             wcv[i] = elem.received_orders     

    #     self.log_orders[f'step_{self.current_step}'] = wcv

    # def update_log_delivery(self) -> None:
    #     """
    #     This method adds a new column to the log_orders DataFrame after each step.
    #     The mentioned task is carried out by: 1- Creating a temporary DataFrame
    #     of the newly updated order amounts, 2- Concatenating the temporary 
    #     DataFrame with the existing self.log_orders.
    #     """
    #     wcv = np.zeros(self.n_agents)                                           
    #     re = ['m','s']
    #     for (i, elem) in enumerate(self.list_agents):
    #         if elem.role in re:
    #             wcv[i] = elem.step_production
    #         else:
    #             wcv[i] = elem.total_received_production

    #     self.log_delivery[f'step_{self.current_step}'] = wcv
        
    def step_profit_dataframe(self) -> DataFrame:
        """
        Uses the log_working_capital DataFrame to create a new DataFrame containing
        step profot values with dimensions identical to log_working_capital.
        """
        log_step_profit = self.log_working_capital.diff(axis = 1)
        log_step_profit.fillna(0, inplace = True)
        return log_step_profit
    
    def Average_Profit_Dataframe(self) -> DataFrame:
        """
        Returns a DataFrame containing average profit per step for each agent.
        """
        step_profit = self.step_profit_dataframe()
        mean_dataframe = step_profit.mean(axis = 1)
        average_profit_dataframe = pd.DataFrame(mean_dataframe, columns =['average_profit_per_step'])
        return average_profit_dataframe