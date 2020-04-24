# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 19:15:35 2020

@author: Farbod
"""
from operator import itemgetter
import math
from typing import List
from random import shuffle
import numpy as np
import matplotlib.pyplot as plt
from agent import Agent

class Agents:
    """
    This class receives a list containing Agent() objects and is responsible 
    for implementing the behaviours of the model.
    """
    
    list_agents : List[Agent]
    ret_list : List[Agent]
    man_list : List[Agent]
    sup_list : List[Agent]
    
    def __init__(self, _list_agents) -> None :
        self._list_agents = _list_agents
        self.__break_list()
        self.__check_duplicate_id()
        self.__layers_fulfilled()
        
        self._do_shuffle = False
        self._node_level_disruption = False
        
        self.num_steps = 0
    @property
    def list_agents(self) -> list:
        return self._list_agents
    
    
    def __break_list(self):
        """
        Creates lists of retailers, manufacturers and suppliers. 
        """
        self.ret_list = [agent for agent in self.list_agents if 
                          agent.role == agent.retailer and 
                          agent.consumer_demand != 0]                          #Filters list_agents for retailers who should order.
        
        self.man_list = [agent for agent in self.list_agents if 
                         agent.role == agent.manufacturer]                     #Filters list_agents for manufacturers.
        
        self.sup_list = [agent for agent in self.list_agents if 
                         agent.role == agent.supplier]                         #Filters list_agents for suppliers.

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
        
    def always_shuffle(self):
        if not self._do_shuffle:
            self._do_shuffle = True
            
    def random_node_level_disruption(self):
        if not self._node_level_disruption:
            self._node_level_disruption = True
        
    
    def __lt__(self, object) -> bool:
        """
        necessary for gaining the ability to make instances of a class comparable.
        """
        if self.sort_num:
            return self.number < object.number
        return self.string < object.string
    
    
    def almost_equal_to_zero(self, value: float, abs_tol: float) -> bool:
        """
        Calculats isclose(value, 0) method with absolute tolerance.
        Return Type: bool
        
        """
        return  math.isclose(value, 0, abs_tol = abs_tol)

        
    def find_agent_by_id(self, unique_id):
        """
        Finds an agent whose id is equivalent to the unique_id proovided
        """
        return [agent for agent in self.list_agents if unique_id == agent.agent_id][0]
    
    def visualize_working_capital_dynamics(self):
        """
        creates an n*m matrix where each row resembles an agent (n agents) and 
        each column resembles a step (m steps).
        """
        working_capital_matrix = np.zeros((len(self.list_agents), self._num_steps + 1))
        
        for elem in self.list_agents:
            for step in range(self.num_steps + 1):
                working_capital_matrix[elem][step] = elem.log_working_capital[step]
        
        x = range(self.num_steps + 1)
        for row in working_capital_matrix:
            plt.plot(x, row)
    
    # Behavioral functions
    def order_to_manufacturers(self) -> None:
        """
        This method is responsible for handling the retailers' ordering process.
        It receives an Agents object and takes advantage of the retailer's 
        supplier set and manufacturer's consumer set to save the ordering trace
        of retailers within it's current step and also facilitates the 
        delivery of the products to the appropriate retailers.
        """
        self.num_steps += 1
        
        temp = list()

        if self._do_shuffle:
            shuffle(self.ret_list)                                                 #No agent has priority over others in its stage.
        
        for man in self.man_list:
            man.prod_cap = man.q * man.working_capital
            if man.customer_set:
                man.customer_set = list()
                
            if man.received_orders:
                man.received_orders = 0.0
                
            if man.order_quant_tracker:
                man.order_quant_tracker = list()
        
        for ret in self.ret_list:
            rand_value = np.random.normal(ret.mu_consumer_demand, ret.sigma_consumer_demand)
            self.consumer_demand = 0.0 if rand_value < 0 else rand_value       #Assigning consumer demand
            
            if ret.supplier_set:
                ret.supplier_set = list()
            
            if ret.elig_ups_agents:
                ret.elig_ups_agents = list()
            
            ret.order_quantity = (ret.consumer_demand / ret.max_suppliers)
            
            if self.almost_equal_to_zero(ret.order_quantity, ret.abs_tol):
                continue
            
            temp = [(agent.agent_id, agent.selling_price) for                  #A list of tuples containing eligible manufacturers.
                    agent in self.man_list if 
                    agent.prod_cap > ret.order_quantity and 
                    agent.selling_price < ret.selling_price]
           
            if not temp:
                continue
            
            temp.sort(key = itemgetter(1))
            
            for (agent_id, _) in temp:
                ret.elig_ups_agents.append(agent_id)    
            
            n_elig_ups = len(ret.elig_ups_agents)
            n_append = min([n_elig_ups, ret.max_suppliers])
            ret.supplier_set.extend(ret.elig_ups_agents[:n_append])            #Adding eligible upstream agents to supplier set of the agent.
    
            for agent_id in ret.supplier_set:
                supplier = self.find_agent_by_id(agent_id)                     #Finding a manufacturer object by it's agent_id.
                supplier.customer_set.append(ret.agent_id)                     #Add a retailer id to the list.
                supplier.prod_cap -= ret.order_quantity                        #Stopping manufacturers from accepting infinite orders.
                supplier.received_orders += ret.order_quantity
                supplier.order_quant_tracker.append((ret.agent_id,
                                                  ret.order_quantity))         #Keeping track of the order quantity is important for delivering phase.   
            
    def order_to_suppliers(self):
        """
        This method is responsible for handling manufacturers' ordering process.
        It receives an Agents object and takes advantage of the manufacturers'
        supplier set and suppliers' consumer set to save the ordering trace of
        the manufacturers within it's current step and also facilitates the 
        delivery of the products to the appropriate manufacturers.
        """
        temp = list()
        
        if self._do_shuffle:                
            shuffle(self.man_list)                                                 #No agent has priority over others in its stage.
        
        for sup in self.sup_list:
            sup.prod_cap = sup.q * sup.working_capital
            if sup.customer_set:
                sup.customer_set = list()
                
            if sup.received_orders:
                sup.received_orders = 0.0
                
            if sup.order_quant_tracker:
                sup.order_quant_tracker = list()
        
        for man in self.man_list:
            if man.supplier_set:
                man.supplier_set = list()
            
            if man.elig_ups_agents:
                man.elig_ups_agents = list()
            
            man.order_quantity = (man.received_orders /man.max_suppliers)      #manufacturers order to max_suppliers suppliers in equal volumes.
            
            if self.almost_equal_to_zero(man.received_orders, man.abs_tol):
                continue
          
            temp = [(agent.agent_id, agent.selling_price) for 
                    agent in self.sup_list if 
                    agent.prod_cap >= man.order_quantity and 
                    agent.selling_price <= man.selling_price]

            if not temp:
                continue
            
            temp.sort(key = itemgetter(1))
            
            for (agent_id, _) in temp:
                man.elig_ups_agents.append(agent_id)
            
            n_elig_ups = len(man.elig_ups_agents)
            n_append = min([n_elig_ups, man.max_suppliers])
            man.supplier_set.extend(man.elig_ups_agents[:n_append])

            for agent_id in man.supplier_set:
                agent = self.find_agent_by_id(agent_id)
                agent.customer_set.append(man.agent_id)                        #Add a retailer object to the list.
                agent.prod_cap -= man.order_quantity                           #Stopping manufacturers from accepting infinite orders.
                agent.received_orders += man.order_quantity
                agent.order_quant_tracker.append((man.agent_id,
                                                  man.order_quantity))
        
    def deliver_to_manufacturers(self):
        """
        This method receives an Agents object and is responsible for
        delivering manufacturers' orders by suppliers. Delivery is subject
        to uncertainty; delivery is completed with probability p_delivery,
        otherwise no product is delivered.
        """
        
        for man in self.man_list:
            if man.received_productions:
                man.received_productions = list()
        
        for sup in self.sup_list:  
            temp = list()
            
            if len(sup.customer_set) == 0:                                     #Making sure supplier  has received some orders.
                sup.log_working_capital.append(sup.working_capital)
                continue
            
            else:
                
                if self._node_level_disruption:                                #Node level disruption is optional.
                    sup.step_production = sup.received_orders * (np.random.binomial
                                                              (n = 1, 
                                                              p = sup.p_delivery)) #Supplier produces full order amount by probability p_delivery and zero by 1-p_delivery.
                
                else:
                    sup.step_production = sup.received_orders
                
                if self.almost_equal_to_zero(sup.step_production, sup.abs_tol):
                    sup.log_working_capital.append(sup.working_capital)
                    continue
                else:
                    
                    for agent_id in sup.customer_set:
                        temp.append(self.find_agent_by_id(agent_id))
                        
                    sup.delivery_amount =[(agent.agent_id, 
                                            sup.step_production * 
                                            (agent.order_quantity / 
                                            sup.received_orders)) for agent
                                          in temp]                             #To deliver in amounts related to the portion of custumer order to total orders. 
                        
                    for (agent_id, portion) in sup.delivery_amount:            #Iterating over customer agents and delivering proportionally.
                        agent = self.find_agent_by_id(agent_id)
                        agent.received_productions.append((
                            portion, sup.selling_price))                        #Kepping records of received products and their prices for customers.
                    
                    step_profit = (sup.input_margin * sup.step_production) - ((sup.interest_rate / 12) * sup.working_capital)  #Calculating profit using a fixed margin for suppliers
                    sup.working_capital += sup.working_capital + step_profit                       # Updating suppliers' working capital.
                    sup.log_working_capital.append(sup.working_capital)

    def deliver_to_retailers(self):
        """
        This method receives a manufacturer object and is responsible for
        delivering retailers orders by  a manufacturer. Delivery is subject
        to uncertainty and is completed with probability p_delivery,
        otherwise no product is delivered.
        """
        
        for ret in self.ret_list:
            
            if ret.received_productions:
                ret.received_productions = list()
        
        for man in self.man_list:
            total_received_production = 0
            total_money_paid = 0
            temp = list()
      
            for (amount, _) in man.received_productions:                       #Calculating total received productions.
                total_received_production += amount                            #WHAT if the length is ZERO?
                
            for (amount, price) in man.received_productions:                   #Calculating total money paid.
                total_money_paid += amount * price
    
            if len(man.customer_set) == 0 or self.almost_equal_to_zero(total_received_production, man.abs_tol):       
                man.log_working_capital = man.working_capital
                continue
            else:
                if self._node_level_disruption:                                #Node level disruption is optional.
                    man.step_production = man.received_orders * (np.random.binomial
                                                              (n = 1, 
                                                              p = man.p_delivery)) #manufacturer produces full order amount by probability p_delivery and zero by 1-p_delivery.
                
                else:
                    man.step_production = man.received_orders
                
                if self.almost_equal_to_zero(man.step_production, man.abs_tol):
                    man.log_working_capital = man.working_capital
                    continue
                else:

                    for agent_id in man.customer_set:
                        temp.append(self.find_agent_by_id(agent_id))

                    man.delivery_amount = [(agent.agent_id, man.step_production * 
                                            (agent.order_quantity / man.received_orders))
                                            for agent in temp]                 #Delivering in amounts related to the portion of custumer order to total orders. 
       
                    for (agent_id, portion) in man.delivery_amount:            #Iterating over customer agents and delivering proportionally.
                        agent = self.find_agent_by_id(agent_id)
                        agent.received_productions.append((
                            portion, man.selling_price))                      #Kepping records of received products and their prices for customers.
                    
                    unit_production_cost = total_money_paid / total_received_production
                    step_profit = (man.selling_price * man.step_production) - (unit_production_cost * man.step_production) - ((man.interest_rate / 12) * man.working_capital)
                    man.working_capital += man.working_capital + step_profit
                    man.log_working_capital = man.working_capital

    def calculate_retailer_profit(self):
        """
        This method is responsible for calculating retailers' profits. It 
        receives an Agents object and manipulates retailers' working capital.
        """
        
        for ret in self.ret_list:
            total_received_production = 0
            total_money_paid = 0

            for (amount, price) in ret.received_productions:                   #Calculating total received productions.
                total_received_production += amount                            #WHAT if the length is ZERO?                   
                total_money_paid += amount * price                             # Calculating total money paid.
            
            if self.almost_equal_to_zero(total_received_production, ret.abs_tol):         
                ret.log_working_capital = ret.working_capital
                continue
            
            else:
                  unit_production_cost = total_money_paid / total_received_production
                  step_profit = (ret.selling_price * total_received_production) - (unit_production_cost * total_received_production) - ((ret.interest_rate / 12) * ret.working_capital)
                  ret.working_capital += ret.working_capital + step_profit
                  ret.log_working_capital = ret.working_capital

