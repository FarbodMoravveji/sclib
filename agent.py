# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 19:13:41 2020

@author: Farbod
"""
import sys
import numpy as np
from parameters import Parameters

class Agent(Parameters):
    """
    The generic class to create supply chain agents.
    The initial working capital is supplied via the "working capital" variable
    and is set to default value 100.
    The type of the agent is supplied via the "role" variable supplied to the
    constructor and it can be a retailer, manufacturer or a supplier
    """
    
    def __init__(self, 
                 agent_id: int, 
                 role: str, 
                 working_capital: float = 100.00, 
                 selling_price: float = 5.00,
                 q: float = 0.90,
                 mu_consumer_demand: float = 60.00,
                 sigma_consumer_demand: float = 10.00,
                 p_delivery: float = 0.80,
                 max_suppliers: float = 3,
                 input_margin: float = 0.01,
                 interest_rate: float = 0.002):
        
        """
        constructor
         Inputs:
            agent_id: an integer or string, unique label 
            working_capital: an integer that 
            role: a character that distinguishes the role of the agent as either
                  - 'r' for retailer
                  - 'm' for manufacturer
                  - 's' for supplier
        """
        
        Parameters.__init__(self)
        
        self.agent_id = agent_id
        self.working_capital = working_capital
        self.role = role
        self.selling_price = selling_price
        self.q = q
        self.mu_consumer_demand = mu_consumer_demand
        self.sigma_consumer_demand = sigma_consumer_demand
        self.p_delivery = p_delivery
        self.max_suppliers = max_suppliers
        self.input_margin = input_margin
        self.interest_rate = interest_rate
        self.__check_role()
        self.__assign_role_specific_attributes()
    
    def __assign_role_specific_attributes(self) -> None: 
        """
        Private method to add the following attributes to the following roles

        role             consumer_demand    supplier_set  consumer_set  production_capacity  received_orders  received_productions  order_quant_tracker order_quantity step_production delivery_amount elig_ups_agents
        retailer                 Y                  Y             N               N                  N                Y                  N                   Y             N                   N           Y
        manufacturer             N                  Y             Y               Y                  Y                Y                  Y                   Y             Y                   Y           Y
        supplier                 N                  N             Y               Y                  Y                N                  Y                   N             Y                   Y           N
        """
        
        # a retailer has a consumer demand attribute, but others don't have it<
        # Production capacity of the supplier and manufacturers are a proportion of their total working capital 
        if self.role == self.retailer:
            #print(type(self.mu_consumer_demand))
            self.consumer_demand = np.random.normal(self.mu_consumer_demand, self.sigma_consumer_demand)
            self.supplier_set = list()
            self.received_productions = list()
            self.order_quantity = 0
            self.elig_ups_agents = list()
        elif self.role == self.manufacturer:
            self.supplier_set = list()
            self.consumer_set = list()
            self.received_orders = 0
            self.received_productions = list()
            self.prod_cap = self.q * self.working_capital
            self.order_quant_tracker = list()
            self.order_quantity = 0
            self.step_production = 0
            self.delivery_amount = list()
            self.elig_ups_agents = list()
        elif self.role == self.supplier:
            self.consumer_set = list()
            self.received_orders = 0
            self.prod_cap = self.q * self.working_capital
            self.order_quant_tracker = list()
            self.step_production = 0
            self.delivery_amount = list()

            
    def __check_role(self) -> None:
        """
        Private method to check the sanity of the role
        """
        if self.role in [self.retailer, self.manufacturer, self.supplier]:
            return 
        else:
            raise ValueError(f'__check_role: self.role = "{self.role}" is undefined')
            sys.exit(self.abort)

