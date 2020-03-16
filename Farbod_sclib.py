import sys
import numpy as np
from operator import itemgetter

# parameters
class Parameters:
    """
    The Parameters class contains constant variables of the problem.
    All attributes have a getter, but no setter. The default values
    are set internally.
    """
    _q: float
    _mu_consumer_demand: float
    _sigma_consumer_demand: float
    _p_delivery: float
    
    def __init__(self):
        """ Constructor """
        self._q = 0.9
        self._mu_consumer_demand = 60
        self._sigma_consumer_demand = 10
        self._p_delivery= 0.8
        # and so on and so forth

#parameter getters.
    @property
    def q(self):
        return self._q
    
    @property
    def mu_consumer_demand(self):
        return self._mu_consumer_demand
    
    @property
    def sigma_consumer_demand(self):
        return self._sigma_consumer_demand
    
    @property
    def p_delivery(self):
        return self._p_delivery


# Error codes
success = 0
abort   = 1

# Pre-defined agent roles
retailer='r'
manufacturer='m'
supplier='s'

class Agent:
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
    
        Agent.all_agents.append(self)
    
    def __assign_role_specific_attributes(self):
        """
        Private method to add the following attributes to the following roles

        role             consumer_demand    supplier_set  consumer_set  production_capacity  received_orders  received_productions  order_quant_tracker order_quantity
        retailer                 Y                  Y             N               N                  N                Y                  N                   Y
        manufacturer             N                  Y             Y               Y                  Y                Y                  Y                   Y
        supplier                 N                  N             Y               Y                  Y                N                  Y                   N
        """
       
        # a retailer has a consumer demand attribute, but others don't have it<
        # Production capacity of the supplier and manufacturers are a proportion of their total working capital 
        if self.role == retailer:
            self.consumer_demand = np.random.normal(Parameters.mu_consumer_demand,Parameters.sigma_consumer_demand)
            self.supplier_set=[]
            self.received_productions=0
            self.order_quantity=0
        elif self.role == manufacturer:
            self.supplier_set=[]
            self.consumer_set=[]
            self.received_orders=0
            self.received_productions=0
            self.prod_cap= Parameters.q*self.working_capital
            self.order_quant_tracker-[]
            self.order_quantity=0
        elif self.role == supplier:
            self.consumer_set=[]
            self.received_orders=0
            self.prod_cap= Parameters.q*self.working_capital
            self.order_quant_tracker-[]


            
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
        temp_list=[]
        self.order_quantity=int((self.consumer_demand)/3)    #retailers order to 3 manufacturers in equal volumes.
        step_all_manufacturers=[agent for agent in Agent.all_agents if agent.role==manufacturer] #why is all_agents undefined?
        step_manufacturers=[(agent.agent_id, agent.selling_price) for agent in step_all_manufacturers if agent.prod_cap>=self.order_quantity] #a list of tuples containing available manufacturers. 
        #do i need an exception handler here? in case there is no available manufacturer.
        if len(step_manufacturers)>=3:
            step_manufacturers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
            temp_list.append(step_manufacturers[:3]) #chooses three manufacturers with the least selling prices.
            for atuple in temp_list:                  # save manufacturer objects to list of suupliers
                self.supplier_set.append(agent for agent in Agent.all_agents if agent.agent_id==atuple[0])
        elif step_manufacturers.len()==0:    #can't order anything
            return # is it true?
        else:
            step_manufacturers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
            temp_list.append(step_manufacturers[:len(step_manufacturers)]) #chooses one or two manufacturers that are available.
            for atuple in temp_list:
                self.supplier_set.append(agent for agent in Agent.all_agents if agent.agent_id==atuple[0])
        try:  #i'm writing this try,except cluse in case self.supplier_set is still empty, is it necessary? 
            for agent in self.supplier_set:
                agent.customer_set.append(self) #I intend to add a retailer object to the list, am i doing it right?
                agent.prod_cap-=self.order_quantity  # to stop manufacturers from accepting infinite orders.
                agent.received_orders+=self.order_quantity
                agent.order_quant_tracker.append((self.agent_id,self.order_quantity)) #keeping track of the order quantity is important for delivering phase.
                
        except:
            return  #is it true? int
        
       
        
        def order_to_suppliers(self):
            """
            This method is responsible for handling the manufacturer ordering process.
            It receives a manufacturer_agent object and takes advantage of the
            manufacturer's supplier set and supplier's consumer set to save the 
            ordering trace of the manufacturer within it's current step and also facilitate
            the delivering of the products to the appropriate manufacturers.
            """
            temp_list=[]
            self.order_quantity=int((self.received_orders)/3)    #manufacturers order to 3 suppliers in equal volumes.
            step_all_suppliers=[agent for agent in Agent.all_agents if agent.role==supplier] #why is all_agents undefined?
            step_suppliers=[(agent.agent_id, agent.selling_price) for agent in step_all_suppliers if agent.prod_cap>=self.order_quantity] #a list of tuples containing available suppliers. 
            #do i need an exception handler here? in case there is no available supplier.
            if len(step_suppliers)>=3:
                step_suppliers.sort(key=itemgetter(1)) #sorts the containers by the second item of the tuples.
                temp_list.append(step_suppliers[:3]) #chooses three suppliers with the least selling prices.
                for atuple in temp_list:
                    self.supplier_set.append(agent for agent in Agent.all_agents if agent.agent_id==atuple[0])
            elif step_suppliers.len()==0:    #can't order anything
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
            temp_list=[]
            if len(self.customer_set)==0:         #making sure self has received some orders
                return
            else:
                step_production= self.received_orders*(np.random.binomial(n=1,p=Parameters.p_delivery)) #supplier produces full order amount by probability p_delivery and zero by 1-p_delivery
                if step_production==0:
                    return
                else:
                    delivery_amount=[(agent.agent_id,step_production*((agent.order_quantity)/self.received_orders)) for agent in self.customer_set] # to deliver in amounts related to the portion of custumer order to total orders. 
                    for tup in delivery_amount:                                                          #making a list of customer agents to iterate over.
                        temp_list.append(agent for agent in Agent.all_agents if tup[0]==agent.agent_id)        
                    for agent in temp_list:                                                              #iterating over customer agents and delivering proportionally.
                        counter=0
                        agent.received_productions+=int(delivery_amount[counter][1])
                        counter+=1


        def delivered_to_retailers(self):
            if len(self.customer_set)==0 or self.received_productions==0:         
                return
            else:
                step_production= self.received_productions*(np.random.binomial(n=1,p=Parameters.p_delivery)) #manufacturer produces full order amount by probability p_delivery only if all its suppliers deliver fully.
                if step_production==0:
                    return
                else:
                    delivery_amount=[(agent.agent_id,step_production*((agent.order_quantity)/self.received_orders)) for agent in self.customer_set] # to deliver in amounts related to the portion of custumer order to total orders. 
                    for tup in delivery_amount:
                        temp_list.append(agent for agent in Agent.all_agents if tup[0]==agent.agent_id)        
                    for agent in temp_list:
                        counter=0
                        agent.received_productions+=int(delivery_amount[counter][1])
                        counter+=1
