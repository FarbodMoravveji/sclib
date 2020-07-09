from typing import List
import numpy as np
import pandas as pd

initial_order_amount: float
retailer_agent_id: int
order_initialization_step: int

class Order_Package:
    """
    An instance of this class is created each time an order is received by any
    agent in the output layer. The mentioned instance will exist in the model 
    until the order is delivered by the output layer and throughout this process
    the instance will be manipulated in order to keep track of the ordering 
    and delivery actions related to the initial irder.
    """

    order_number = 1

    def __init__(self, initial_order_amount, retailer_agent_id, order_initialization_step):
        """
        constructor
         Input:
           initial_order_amount: The order amount received from outside of the network.
           retailer_agent_id: agent_id related to the retailer.
           order_initialization_step: marks the step that the order object is created.
        """
        self.order_number = cls.order_number
        self.initial_order_amount = initial_order_amount
        self.retailer_agent_id = retailer_agent_id
        self.order_initialization_step = order_initialization_step

        self.manufacturers = list()                                            #List of tuples by the form (agent_id, production_time, order_amount)
        self.suppliers = list()
        
        self.completed_ordering_to_manufacturers = False
        self.completed_ordering_to_suppliers = False

        self.order_feasibility = True

        cls.order_number += 1