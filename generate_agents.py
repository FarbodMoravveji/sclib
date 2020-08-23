import sys, os
from typing import List
import pandas as pd
from sclib.agent import Agent 

class GenAgents:
    """
    This class is responsible for generating instances of agent.Agent() by
    reading arguments from an excel sheet. It stores the generated agents in a
    list called list_agents and returns that list.
    """
    list_agents: List[Agent]
    def __init__(self, excel_file: str):
        """
        constructor
         Input:
           excel_file: A file.xlsx that provides parameters of Agent() class 
                       in the proper order.
        """
        self.excel_file = excel_file
        self.__check_excel_file()
        self.list_agents = list()

        self.__read_excel_file()
        self.__get_list_agents()

    def __check_excel_file(self) -> None:
        """
        This method makes sure that a proper excel sheet is passed to the class.
        """
        if not os.path.exists(self.excel_file):
            raise FileNotFoundError
            sys.exit(1)

    def __read_excel_file(self) -> None:
        """
        This method creates a dataframe from the excel_file passed to the 
        GenAgents class as an argument
        """
        df = pd.read_excel(self.excel_file)
        self.df = df
        print(self.df)

    def __get_list_agents(self) -> None:
        """
        This method is responsible for instanciating Agent() objects and adding
        those objects to self.list_agents.
        """
        for i in range(len(self.df)):
            x = Agent(self.df["agent_id"].at[i], 
                      self.df["role"].at[i], 
                      self.df["working_capital"].at[i], 
                      self.df["mu_selling_price"].at[i],
                      self.df["sigma_selling_price"].at[i],
                      self.df["q"].at[i], 
                      self.df["consumer_demand_mean"].at[i], 
                      self.df["p_delivery"].at[i],
                      self.df["input_margin"].at[i],
                      self.df["interest_rate"].at[i],
                      self.df["fixed_cost"].at[i],
                      self.df["days_between_financing"].at[i],
                      self.df["financing_period"].at[i],
                      self.df["ordering_period"].at[i],
                      self.df["delivery_period"].at[i],
                      self.df["fixed_assets"].at[i])
            self.list_agents.append(x)