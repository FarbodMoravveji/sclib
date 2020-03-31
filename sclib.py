import sys
import numpy as np
from operator import itemgetter
import math

# parameters
class Parameters:
    """
    The Parameters class contains constant variables of the problem.
    All attributes have a getter, but no setter. The default values
    are set internally.
    """
    _q: float                       #Technological proportionality constant
    _mu_consumer_demand: float
    _sigma_consumer_demand: float
    _p_delivery: float
    _max_suppliers: int
    _input_margin: float            #Margin level of the raw materials suppliers.
    _interest_rate: float           #Interest rate constant.
    
    
    def __init__(self):
        """ Constructor """
        self._q = 0.90
        self._mu_consumer_demand = 60.00
        self._sigma_consumer_demand = 10.00
        self._p_delivery = 0.80
        self._max_suppliers = 3
        self._input_margin = 0.01
        self._interest_rate = 0.002
        
        # and so on and so forth

    #parameter getters.
    @property
    def q(self) -> float :
        return self._q
    
    @property
    def mu_consumer_demand(self) -> float :
        return self._mu_consumer_demand
    
    @property
    def sigma_consumer_demand(self) -> float :
        return self._sigma_consumer_demand
    
    @property
    def p_delivery(self) -> float :
        return self._p_delivery
    
    @property
    def max_suppliers(self) -> int:
        return self._max_suppliers
    
    @property
    def input_margin(self) -> float:
        return self._input_margin
    
    @property
    def interest_rate(self) -> float:
        return self._interest_rate


# Error codes
success = 0
abort   = 1

# Pre-defined agent roles
retailer ='r'
manufacturer ='m'
supplier ='s'

class Agent(Parameters):
    """
    The generic class to create supply chain agents.
    The initial working capital is supplied via the "working capital" variable
    and is set to default value 100.
    The type of the agent is supplied via the "role" variable supplied to the
    constructor and it can be a retailer, manufacturer or a supplier
    """
    all_agents = []     # a list that contains all agents
    
    def __init__(self, 
                 agent_id: int, 
                 role: str, 
                 working_capital: float = 100.00, 
                 selling_price: float = 5.00):
        
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
        self.__check_role()
        self.__assign_role_specific_attributes()
    
        Agent.all_agents.append(self)
    
    def __assign_role_specific_attributes(self):
        """
        Private method to add the following attributes to the following roles

        role             consumer_demand    supplier_set  consumer_set  production_capacity  received_orders  received_productions  order_quant_tracker order_quantity step_production delivery_amount
        retailer                 Y                  Y             N               N                  N                Y                  N                   Y             N                   N
        manufacturer             N                  Y             Y               Y                  Y                Y                  Y                   Y             Y                   Y
        supplier                 N                  N             Y               Y                  Y                N                  Y                   N             Y                   Y
        """
        
        # a retailer has a consumer demand attribute, but others don't have it<
        # Production capacity of the supplier and manufacturers are a proportion of their total working capital 
        if self.role == retailer:
            print(type(self.mu_consumer_demand))
            self.consumer_demand = np.random.normal(self.mu_consumer_demand, self.sigma_consumer_demand)
            self.supplier_set = []
            self.received_productions = []
            self.order_quantity = 0
        elif self.role == manufacturer:
            self.supplier_set = []
            self.consumer_set = []
            self.received_orders = 0
            self.received_productions = []
            self.prod_cap = Parameters.q * self.working_capital
            self.order_quant_tracker = []
            self.order_quantity = 0
            self.step_production = 0
            self.delivery_amount = []
        elif self.role == supplier:
            self.consumer_set = []
            self.received_orders = 0
            self.prod_cap = Parameters.q * self.working_capital
            self.order_quant_tracker = []
            self.step_production = 0
            self.delivery_amount = []

            
    def __check_role(self):
        """
        Private method to check the sanity of the role
        """
        if self.role in [retailer, manufacturer, supplier]:
            return 
        else:
            raise ValueError(f'__check_role: self.role = "{self.role}" is undefined')
            sys.exit(abort)
    
class Agents:
    
    def __lt__(self, object):
        """
        necessary for gaining the ability of making instances of a class comparable.
        """
        if self.sort_num:
            return self.number < object.number
        return self.string < object.string
    
    # Behavioral functions
    def order_to_manufacturers(self):
        """
        This method is responsible for handling the retailer ordering process.
        It receives a retailer_agent object and takes advantage of the
        retailer's supplier set and manufacturer's consumer set to save the 
        ordering trace of the retailer within it's current step and also facilitate
        the delivering of the products to the appropriate retailers.
        """
        if self.role != retailer:
            return

        temp_list = []
        self.order_quantity = math.floor(self.consumer_demand / Parameters.max_suppliers)    #retailers order to Parameters.max_suppliers manufacturers in equal volumes.
        if self.order_quantity < 1:
            raise ValueError(f"Error: {self.order_quantity} is less than 1")
        
        step_all_manufacturers=[agent for agent in Agent.all_agents if agent.role == manufacturer]
        step_manufacturers=[(agent.agent_id, agent.selling_price) for agent in step_all_manufacturers if agent.prod_cap>=self.order_quantity] #a list of tuples containing available manufacturers. 
        #do i need an exception handler here? in case there is no available manufacturer.
        if step_manufacturers.len() == 0:    #can't order anything
            return 
        elif len(step_manufacturers) >= Parameters.max_suppliers:
            step_manufacturers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
            temp_list.append(step_manufacturers[:Parameters.max_suppliers]) #chooses three manufacturers with the least selling prices.
            for atuple in temp_list:                  # save manufacturer objects to list of suupliers
                self.supplier_set.append(agent for agent in Agent.all_agents if agent.agent_id == atuple[0])
        else:
            step_manufacturers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
            temp_list.append(step_manufacturers[:len(step_manufacturers)]) #chooses one or two manufacturers that are available.
            for atuple in temp_list:
                self.supplier_set.append(agent for agent in Agent.all_agents if agent.agent_id == atuple[0])
        
            for agent in self.supplier_set:
                agent.customer_set.append(self) #I intend to add a retailer object to the list, am i doing it right?
                agent.prod_cap -= self.order_quantity  # to stop manufacturers from accepting infinite orders.
                agent.received_orders += self.order_quantity
                agent.order_quant_tracker.append((self.agent_id,self.order_quantity)) #keeping track of the order quantity is important for delivering phase.   
                return
            
    def order_to_suppliers(self):
        """
        This method is responsible for handling the manufacturer ordering process.
        It receives a manufacturer_agent object and takes advantage of the
        manufacturer's supplier set and supplier's consumer set to save the 
        ordering trace of the manufacturer within it's current step and also facilitate
        the delivering of the products to the appropriate manufacturers.
        """
        if self.role != manufacturer:
            return
        temp_list=[]
        self.order_quantity=int((self.received_orders) / Parameters.max_suppliers)    #manufacturers order to Parameters.max_suppliers suppliers in equal volumes.
        step_all_suppliers=[agent for agent in Agent.all_agents if agent.role == supplier] #why is all_agents undefined?
        step_suppliers=[(agent.agent_id, agent.selling_price) for agent in step_all_suppliers if agent.prod_cap>=self.order_quantity] #a list of tuples containing available suppliers. 
        #do i need an exception handler here? in case there is no available supplier.
        if len(step_suppliers) >= Parameters.max_suppliers:
            step_suppliers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
            temp_list.append(step_suppliers[:Parameters.max_suppliers]) #chooses three suppliers with the least selling prices.
            for atuple in temp_list:
                self.supplier_set.append(agent for agent in Agent.all_agents if agent.agent_id == atuple[0])
        elif step_suppliers.len() == 0:    #can't order anything
            return # is it true?
        else:
            step_suppliers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
            temp_list.append(step_suppliers[:len(step_suppliers)]) #chooses one or two manufacturers that are available.
            for atuple in temp_list:
                self.supplier_set.append(agent for agent in Agent.all_agents if agent.agent_id==atuple[0])
        try:  #i'm writing this try,except cluse in case self.supplier_set is still empty, is it necessary? 
            for agent in self.supplier_set:
                agent.customer_set.append(self) #I intend to add a manufacturer object to the list, am i doing it right?
                agent.prod_cap-=self.order_quantity  # to stop manufacturers from accepting infinite orders.
                agent.received_orders+=self.order_quantity
                agent.order_quant_tracker.append((self.agent_id,self.order_quantity))

        except:
            return  #is it true?
        
        
    def deliver_to_manufacturers(self):
        """
        This method receives a supplier object and is responsible for
        delivering manufacturers orders by suppliers. Delivery is subject
        to uncertainty; delivery is completed with probability p_delivery,
        otherwise no product is delivered.
        """
        temp_list = []
        if self.role != supplier:
            return
        if len(self.customer_set) == 0:         #making sure self has received some orders
            return
        else:
            self.step_production = self.received_orders * (np.random.binomial(n = 1, p = Parameters.p_delivery)) #supplier produces full order amount by probability p_delivery and zero by 1-p_delivery
            if self.step_production == 0:
                return
            else:
                self.delivery_amount =[(agent.agent_id, self.step_production * ((agent.order_quantity) / self.received_orders)) for agent in self.customer_set] # to deliver in amounts related to the portion of custumer order to total orders. 
                for tup in self.delivery_amount:                                                          #making a list of customer agents to iterate over.
                    temp_list.append(agent for agent in Agent.all_agents if tup[0] == agent.agent_id)
                    
                for agent in temp_list:                                                              #iterating over customer agents and delivering proportionally.
                    counter = 0
                    agent.received_productions.append(int(self.delivery_amount[counter][1]), self.selling_price)  #Kepping records of received products and their prices for customers.
                    counter += 1
                step_profit = Parameters.input_margin * self.step_production - Parameters.interest_rate * self.working_capital  #calculating profit using a fixed margin for suppliers
                self.working_capital += self.working_capital + step_profit                        # Updating suppliers' working capital.

    def deliver_to_retailers(self):
        """
        This method receives a manufacturer object and is responsible for
        delivering retailers orders by  a manufacturer. Delivery is subject
        to uncertainty and is completed with probability p_delivery,
        otherwise no product is delivered.
        """
        temp_list = []
        total_received_production = 0
        total_money_paid = 0
        if self.role != manufacturer:
            return
        for i in range(len(self.received_productions)):                    # calculating total received productions.
            total_received_production += (self.received_productions[i][0]) # what if the length is ZERO?
            
        for i in range(len(self.received_productions)):                    # calculating total money paid.
            total_money_paid = (self.received_productions[i][0] * self.received_productions[i][1])

        if len(self.customer_set) == 0 or total_received_production == 0:         
            return
        else:
            self.step_production = self.received_productions * (np.random.binomial(n = 1, p = Parameters.p_delivery)) #manufacturer produces full order amount by probability p_delivery only if all its suppliers deliver fully.
            if self.step_production == 0:
                return
            else:
                self.delivery_amount = [(agent.agent_id, self.step_production * ((agent.order_quantity) / self.received_orders)) for agent in self.customer_set] # to deliver in amounts related to the portion of custumer order to total orders. 
                for tup in self.delivery_amount:
                    temp_list.append(agent for agent in Agent.all_agents if tup[0] == agent.agent_id)        
                for agent in temp_list:
                    counter = 0
                    agent.received_productions.append(int(self.delivery_amount[counter][1]), self.selling_price)  #Kepping records of received products and their prices for customers.
                    counter += 1
                
                unit_production_cost = total_money_paid / total_received_production
                step_profit = (self.selling_price * self.step_production) - (unit_production_cost * self.step_production) - (Parameters.interest_rate * self.working_capital)
                self.working_capital += self.working_capital + step_profit

    def calculate_retailer_profit(self):
        """
        This method is responsible for calculating retailers profits. It 
        receives a retailer object and manipulates its working capital.
        """
        total_received_production = 0
        total_money_paid = 0
        if self.role != retailer:
            return
        for i in range(len(self.received_productions)):                    # calculating total received productions.
            total_received_production += (self.received_productions[i][0]) # what if the length is ZERO?
        
        for i in range(len(self.received_productions)):                    # calculating total money paid.
            total_money_paid = (self.received_productions[i][0] * self.received_productions[i][1])
        
        if len(self.customer_set) == 0 or total_received_production == 0:         
            return
        
        else:
             unit_production_cost = total_money_paid / total_received_production
             step_profit = (self.selling_price * total_received_production) - (unit_production_cost * total_received_production) - (Parameters.interest_rate * self.working_capital)
             self.working_capital += self.working_capital + step_profit
