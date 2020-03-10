import sys
import numpy as np
from operator import itemgetter
# parameters
q=0.9
mu_consumer_demand=60
sigma_consumer_demand=10


# Error codes
success = 0
abort   = 1

# Pre-defined agent roles
retailer='r'
manufacturer='m'
supplier='s'

class agent:
    """
    The generic class to create supply chain agents.
    The initial working capital is supplied via the "working capital" variable
    and is set to default value 100.
    The type of the agent is supplied via the "role" variable supplied to the
    constructor and it can be a retailer, manufacturer or a supplier
    """
    all_agents=[]     # a list that contains all agents
    
    def __init__(self,agent_id, role, working_capital=100, selling_price=5):
        
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
        
        self.agent_id= agent_id
        self.working_capital= working_capital
        self.role= role
        self.selling_price =selling_price
        self.__check_role()
        self.__assign_role_specific_attributes()
    
        agent.all_agents.append(self)
    
    def __assign_role_specific_attributes(self):
        """
        Private method to add the following attributes to the following roles

        role             consumer_demand    supplier_set  consumer_set  production_capacity  received_orders
        retailer                 Y                  Y             N               N                  N
        manufacturer             N                  Y             Y               Y                  Y
        supplier                 N                  N             Y               Y                  Y
        """
       
        # a retailer has a consumer demand attribute, but others don't have it<
        # Production capacity of the supplier and manufacturers are a proportion of their total working capital 
        if self.role == retailer:
            self.consumer_demand = np.random.normal(mu_consumer_demand,sigma_consumer_demand)
            self.supplier_set=[]
        elif self.role == manufacturer:
            self.supplier_set=[]
            self.consumer_set=[]
            self.received_orders=0
            self.prod_cap= q*self.working_capital
        elif self.role == supplier:
            self.consumer_set=[]
            self.received_orders=0
            self.prod_cap= q*self.working_capital

            
    def __check_role(self):
        """
        Private method to check the sanity of the role
        """
        if self.role in [retailer, manufacturer, supplier]:
            return 
        else:
            raise ValueError(f'__check_role: self.role = "{self.role}" is undefined')
            sys.exit(abort)
    
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
        order_quantity=(self.consumer_demand)/3    #retailers order to 3 manufacturers in equal volumes.
        step_all_manufacturers=[agent for agent in all_agents if agent.role==manufacturer] #why is all_agents undefined?
        step_manufacturers=[(agent.agent_id, agent.selling_price) for agent in step_all_manufacturers if agent.prod_cap>=order_quantity] #a list of tuples containing available manufacturers. 
        #do i need an exception handler here? in case there is no available manufacturer.
        if len(step_manufacturers)>=3:
            step_manufacturers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
            self.supplier_set.append(step_manufacturers[:3]) #chooses three manufacturers with the least selling prices.
        elif step_manufacturers.len()==0:    #can't order anything
            return # is it true?
        else:
            step_manufacturers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
            self.supplier_set.append(step_manufacturers[:len(step_manufacturers)]) #chooses one or two manufacturers that are available.
        try:  #i'm writing this try,except cluse in case self.supplier_set is still empty, is it necessary? 
            for agent in self.supplier_set:
                agent.customer_set.append(self) #I intend to add a retailer object to the list, am i doing it right?
                agent.prod_cap-=order_quantity  # to stop manufacturers from accepting infinite orders.
                agent.received_orders+=order_quantity
        except:
            return  #is it true?
        
       
        
        def order_to_suppliers(self):
            """
            This method is responsible for handling the manufacturer ordering process.
            It receives a manufacturer_agent object and takes advantage of the
            manufacturer's supplier set and supplier's consumer set to save the 
            ordering trace of the manufacturer within it's current step and also facilitate
            the delivering of the products to the appropriate manufacturers.
            """
            order_quantity=(self.received_orders)/3    #manufacturers order to 3 suppliers in equal volumes.
            step_all_suppliers=[agent for agent in all_agents if agent.role==supplier] #why is all_agents undefined?
            step_suppliers=[(agent.agent_id, agent.selling_price) for agent in step_all_suppliers if agent.prod_cap>=order_quantity] #a list of tuples containing available suppliers. 
            #do i need an exception handler here? in case there is no available supplier.
            if len(step_suppliers)>=3:
                step_suppliers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
                self.supplier_set.append(step_suppliers[:3]) #chooses three suppliers with the least selling prices.
            elif step_suppliers.len()==0:    #can't order anything
                return # is it true?
            else:
                step_suppliers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
                self.supplier_set.append(step_suppliers[:len(step_suppliers)]) #chooses one or two manufacturers that are available.
            try:  #i'm writing this try,except cluse in case self.supplier_set is still empty, is it necessary? 
                for agent in self.supplier_set:
                    agent.customer_set.append(self) #I intend to add a retailer object to the list, am i doing it right?
                    agent.prod_cap-=order_quantity  # to stop manufacturers from accepting infinite orders.
                    agent.received_orders+=order_quantity
            except:
                return  #is it true?
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    