# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 19:15:35 2020

@author: Farbod
"""
import numpy as np
from operator import itemgetter
import math
from typing import List
from random import shuffle
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
    
    def __init__(self, list_agents) -> None :
        self.list_agents = list_agents
        self.__break_list()
        
    def __break_list(self):
        self.ret_list = [agent for agent in self.list_agents if 
                          agent.role == agent.retailer and 
                          agent.consumer_demand != 0]                          #Filters list_agents for retailers who should order.
        
        self.man_list = [agent for agent in self.list_agents if 
                         agent.role == agent.manufacturer]                                    #Filters list_agents for manufacturers.
        
        self.sup_list = [agent for agent in self.list_agents if 
                         agent.role == agent.supplier]                                    #Filters list_agents for suppliers.

    
    def __lt__(self, object) -> bool:
        """
        necessary for gaining the ability to make instances of a class comparable.
        """
        if self.sort_num:
            return self.number < object.number
        return self.string < object.string
    
    
    # Behavioral functions
    def order_to_manufacturers(self):
        """
        This method is responsible for handling the retailers' ordering process.
        It receives an Agents object and takes advantage of the retailer's 
        supplier set and manufacturer's consumer set to save the ordering trace
        of retailers within it's current step and also facilitates the 
        delivery of the products to the appropriate retailers.
        """

        temp_list = list()
        
        shuffle(self.ret_list)                                                 #No agent has priority over others in its stage.
        
        for agent in self.ret_list:                                            #Retailers order to self.max_suppliers manufacturers in equal volumes.
            agent.order_quantity = (agent.consumer_demand / 
                                              agent.max_suppliers)
        
        for agent in self.ret_list:
            if agent.order_quantity < 1:
                raise ValueError(f"Error: {agent.order_quantity} is less than 1")
        
        for ret in self.ret_list:
            ret.elig_ups_agents = [(agent.agent_id, agent.selling_price) for 
                                agent in self.man_list if 
                                agent.prod_cap >= ret.order_quantity and 
                                agent.selling_price <= ret.selling_price]      #A list of tuples containing eligible manufacturers.
            if ret.elig_ups_agents.len() == 0:    #can't order anything 
                return 
            elif len(ret.elig_ups_agents) >= ret.max_suppliers:
                ret.elig_ups_agents.sort(key=itemgetter(1))                    #Sorts the containers by the second item of the tuples.
                temp_list.append(ret.elig_ups_agents[:ret.max_suppliers])      #Chooses three manufacturers with the least selling prices.
                for atuple in temp_list:                                       #Saves manufacturer objects to list of step suupliers.
                    ret.supplier_set.append(agent for agent in self.man_list
                                            if agent.agent_id == atuple[0])
            else:
                ret.elig_ups_agents.sort(key=itemgetter(1))                    #Sorts the container by the second item of the tuples.
                temp_list.append(ret.elig_ups_agents[:len(ret.elig_ups_agents)]) #Chooses one or two manufacturers that are available.
                for atuple in temp_list:
                    ret.supplier_set.append(agent for agent in self.man_list
                                            if agent.agent_id == atuple[0])
            
            try:
                for agent in ret.supplier_set:
                    agent.customer_set.append(ret)                             #Add a retailer object to the list.
                    agent.prod_cap -= ret.order_quantity                       #Stopping manufacturers from accepting infinite orders.
                    agent.received_orders += ret.order_quantity
                    agent.order_quant_tracker.append((ret.agent_id,
                                                      ret.order_quantity))     #Keeping track of the order quantity is important for delivering phase.   
            except:
                return
            
    def order_to_suppliers(self):
        """
        This method is responsible for handling manufacturers' ordering process.
        It receives an Agents object and takes advantage of the manufacturers'
        supplier set and suppliers' consumer set to save the ordering trace of
        the manufacturers within it's current step and also facilitates the 
        delivery of the products to the appropriate manufacturers.
        """

        temp_list = list()
                        
        shuffle(self.man_list)                                                 #No agent has priority over others in its stage.
        
        for agent in self.man_list:
            agent.order_quantity = (agent.received_orders /agent.max_suppliers)               #manufacturers order to max_suppliers suppliers in equal volumes.
            
        for agent in self.man_list:
            if agent.received_orders < 1:
                raise ValueError(f"Error: {agent.received_orders} is less than 1")
        
        for man in self.man_list:
            man.elig_ups_agents = [(agent.agent_id, agent.selling_price) for 
                                agent in self.sup_list if 
                                agent.prod_cap >= man.order_quantity and 
                                agent.selling_price <= man.selling_price]      #A list of tuples containing eligible suppliers.

            if man.elig_ups_agents.len() == 0:                                 #Can't order anything.
                return 
            
            elif len(man.elig_ups_agents) >= man.max_suppliers:
                man.elig_ups_agents.sort(key=itemgetter(1))                    #Sorts the container by the second item of the tuples.
                temp_list.append(man.elig_ups_agents[:man.max_suppliers])      #Chooses three suppliers with the least selling prices.
                for atuple in temp_list:
                    man.supplier_set.append(agent for agent in self.sup_list
                                            if agent.agent_id == atuple[0])
            
            else:
                man.elig_ups_agents.sort(key=itemgetter(1))                    #Sorts the container by the second item of the tuples.
                temp_list.append(man.elig_ups_agents[:len(man.elig_ups_agents)]) #chooses one or two manufacturers that are available.
                for atuple in temp_list:
                    man.supplier_set.append(agent for agent in self.sup_list
                                            if agent.agent_id == atuple[0])
            try:                                                               #This try,except cluse is writtenin case man.supplier_set is still empty, is it necessary? 
                for agent in man.supplier_set:
                    agent.customer_set.append(man)                             #Add a manufacturer object to the list.
                    agent.prod_cap -= man.order_quantity                       #To stop suppliers from accepting infinite orders.
                    agent.received_orders += man.order_quantity
                    agent.order_quant_tracker.append((man.agent_id,
                                                      man.order_quantity))
            
            except:
                return
        
    def deliver_to_manufacturers(self):
        """
        This method receives an Agents object and is responsible for
        delivering manufacturers' orders by suppliers. Delivery is subject
        to uncertainty; delivery is completed with probability p_delivery,
        otherwise no product is delivered.
        """
        temp_list = []

        for sup in self.sup_list:  
            
            if len(sup.customer_set) == 0:                                     #Making sure supplier  has received some orders.
                return
            else:
                sup.step_production = sup.received_orders * (np.random.binomial
                                                             (n = 1, 
                                                              p = sup.p_delivery)) #Supplier produces full order amount by probability p_delivery and zero by 1-p_delivery.
                if sup.step_production == 0:
                    return
                else:
                    sup.delivery_amount =[(agent.agent_id, 
                                           sup.step_production * 
                                           (agent.order_quantity / 
                                            sup.received_orders)) for agent
                                          in sup.customer_set]                 #To deliver in amounts related to the portion of custumer order to total orders. 
                    for tup in sup.delivery_amount:                            #Making a list of customer agents to iterate over.
                        temp_list.append(agent for agent in self.man_list
                                         if tup[0] == agent.agent_id)
                        
                    for agent in temp_list:                                    #Iterating over customer agents and delivering proportionally.
                        counter = 0
                        agent.received_productions.append(
                            sup.delivery_amount[counter][1],
                            sup.selling_price)                                 #Kepping records of received products and their prices for customers.
                        counter += 1
                    step_profit = sup.input_margin * sup.step_production - sup.interest_rate * sup.working_capital  #Calculating profit using a fixed margin for suppliers
                    sup.working_capital += sup.working_capital + step_profit                        # Updating suppliers' working capital.

    def deliver_to_retailers(self):
        """
        This method receives a manufacturer object and is responsible for
        delivering retailers orders by  a manufacturer. Delivery is subject
        to uncertainty and is completed with probability p_delivery,
        otherwise no product is delivered.
        """
        temp_list = []
        
        for man in self.man_list:
            total_received_production = 0
            total_money_paid = 0
      
            for i in range(len(man.received_productions)):                     #Calculating total received productions.
                total_received_production += (man.received_productions[i][0])  #WHAT if the length is ZERO?
                
            for i in range(len(man.received_productions)):                     #Calculating total money paid.
                total_money_paid = (man.received_productions[i][0] * man.received_productions[i][1])
    
            if len(man.customer_set) == 0 or total_received_production == 0:         
                return
            else:
                man.step_production = man.received_productions * (np.random.binomial
                                                                  (n = 1, p = man.p_delivery)) #Manufacturer produces full order amount by probability p_delivery only if all its suppliers deliver fully.
                if man.step_production == 0:
                    return
                else:
                    man.delivery_amount = [(agent.agent_id, man.step_production * 
                                            (agent.order_quantity / man.received_orders))
                                           for agent in man.customer_set]      #Delivering in amounts related to the portion of custumer order to total orders. 
                    for tup in man.delivery_amount:
                        temp_list.append(agent for agent in self.ret_list if 
                                         tup[0] == agent.agent_id)        
                    for agent in temp_list:
                        counter = 0
                        agent.received_productions.append(
                            man.delivery_amount[counter][1], man.selling_price)  #Kepping records of received products and their prices for customers.
                        counter += 1
                    
                    unit_production_cost = total_money_paid / total_received_production
                    step_profit = (man.selling_price * man.step_production) - (unit_production_cost * man.step_production) - (man.interest_rate * man.working_capital)
                    man.working_capital += man.working_capital + step_profit

    def calculate_retailer_profit(self):
        """
        This method is responsible for calculating retailers' profits. It 
        receives an Agents object and manipulates retailers' working capital.
        """
        
        for ret in self.ret_list:
            total_received_production = 0
            total_money_paid = 0

            for i in range(len(ret.received_productions)):                    #Calculating total received productions.
                total_received_production += (ret.received_productions[i][0]) #WHAT if the length is ZERO?                   
                total_money_paid = (ret.received_productions[i][0] * ret.received_productions[i][1]) # Calculating total money paid.
            
            if len(ret.customer_set) == 0 or total_received_production == 0:         
                return
            
            else:
                 unit_production_cost = total_money_paid / total_received_production
                 step_profit = (ret.selling_price * total_received_production) - (unit_production_cost * total_received_production) - (ret.interest_rate * ret.working_capital)
                 ret.working_capital += ret.working_capital + step_profit

