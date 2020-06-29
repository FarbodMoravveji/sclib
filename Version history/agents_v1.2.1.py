from operator import itemgetter
import math
from math import log
from typing import List
from random import shuffle
import numpy as np
from sclib.agent import Agent

class Agents:
    """
    This class receives a list containing Agent() objects and is responsible 
    for implementing the behaviours of the model.
    """
    list_agents: List[Agent]
    ret_list: List[Agent]
    man_list: List[Agent]
    sup_list: List[Agent]
    do_shuffle: bool
    random_node_level_disruption: bool
    seeding: bool

    def __init__(self, _list_agents) -> None:
        """
        constructor
         Input:
            _list_agents: A list containing Agent objects. This list can be
                          constructed manually or it can be extracted from a 
                          GenAgents object as is shown below:
                              list_of_agents = GenAgents(excel_file).list_agents
        """
        self._list_agents = _list_agents
        self.__break_list()
        self.__check_duplicate_id()
        self.__layers_fulfilled()
        
        self._do_shuffle = False
        self._node_level_disruption = False
        self._seeding = False

    @property
    def list_agents(self):
        return self._list_agents

    def __break_list(self) -> None:
        """
        Creates lists of retailers, manufacturers and suppliers. 
        """
        self.ret_list = [agent for agent in self._list_agents if 
                          agent.role == agent.retailer]                        # Filters list_agents for retailers who should order.
        
        self.man_list = [agent for agent in self._list_agents if 
                         agent.role == agent.manufacturer]                     # Filters list_agents for manufacturers.
        
        self.sup_list = [agent for agent in self._list_agents if 
                         agent.role == agent.supplier]                         # Filters list_agents for suppliers.

    def __check_duplicate_id(self) -> None:
        """
        Checks if list_agents contain any duplicate agent_ids.
        """
        agents_set = set()
        ids = [agent.agent_id for agent in self._list_agents]
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
        for elem in self._list_agents:
            role_set.add(elem.role)
        if len(role_set) < 3:
            raise ValueError(f"__layers_fulfilled: At least one layer doesn't contain any agents")
        if len(role_set) > 3:
            raise ValueError(f"__layers_fulfilled: Model should only consist of three layers, not more")

    def always_shuffle(self) -> None:
        """
        Creates competition in the model by shuffling the list of agents.
        """
        if not self._do_shuffle:
            self._do_shuffle = True

    def never_shuffle(self) -> None:
        """
        Cancels competition in the model by not shuffling the list of agents.
        """
        if self._do_shuffle:
            self._do_shuffle = False

    def activate_random_node_level_disruption(self) -> None:
        """
        Adds uncertainty of delivery to the model. the node_level_disruption flag
        is False by default, so this method can be called to implement
        disruption in the model.
        """
        if not self._node_level_disruption:
            self._node_level_disruption = True

    def deactivate_random_node_level_disruption(self) -> None:
        """
        This method takes the random_node_level_disruption flag back to its default
        state.
        """
        if self._node_level_disruption:
            self._node_level_disruption = False

    def turn_off_seeding(self) -> None:
        """
        Sets the seeding flag of the model to its default state which is False.
        """
        if self._seeding:
            self._seeding = False

    def turn_on_seeding(self) -> None:
        """
        Sets a np.random.seed() method on the model.
        """
        if not self._seeding:
            self._seeding = True

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

    def find_agent_by_id(self, unique_id: str) -> object:
        """
        Finds an agent whose id is equivalent to the unique_id proovided.
        
        Returns:
            An Agent() object with the agent_id that is identical to the uniqu_id
            provided as the argument of the method.
        """
        return [agent for agent in self._list_agents if unique_id == agent.agent_id][0]

    def realize_selling_prices(self):
        for agent in self._list_agents:
            step_selling_price = np.random.lognormal(mean = log(agent.mu_selling_price), sigma = agent.sigma_selling_price)
            agent.selling_price = step_selling_price   #agent.mu_selling_price if step_selling_price <= 0 else

    # if self._seeding:
    #     np.random.seed(0)

    def order_to_manufacturers(self) -> None:
        """
        This method is responsible for handling the retailers' ordering process.
        It takes advantage of the retailer's supplier set and manufacturer's 
        consumer set to save the ordering trace of retailers within it's current
        step and also facilitates the delivery of the products to the appropriate
        retailers.
        """
        if self._do_shuffle:
            shuffle(self.ret_list)                                             # No agent has priority over others in its stage.

        for man in self.man_list:
            man.prod_cap = man.q * man.working_capital
            if man.customer_set:
                man.customer_set = list()

            if man.received_orders:
                man.received_orders = 0.0

            if man.order_quant_tracker:
                man.order_quant_tracker = list()

        for ret in self.ret_list:
            ret.prod_cap = ret.q * ret.working_capital
            rand_value = np.random.exponential(scale = ret.consumer_demand_mean, size = 1)[0]
            ret.consumer_demand = rand_value                                   # Assigning consumer demand.
            
            if ret.consumer_demand == 0:
                continue

            if ret.supplier_set:
                ret.supplier_set = list()

            if ret.elig_ups_agents:
                ret.elig_ups_agents = list()

            if ret.total_order_quantity:
                ret.total_order_quantity = 0

            if ret.orders_succeeded:
                ret.orders_succeeded = 0

            ret.total_order_quantity = (min(ret.consumer_demand, ret.prod_cap))

            if self.almost_equal_to_zero(ret.total_order_quantity, ret.abs_tol):
                continue
            
            ret.elig_ups_agents = [(agent.agent_id, agent.selling_price, agent.prod_cap) for   # A list of tuples containing eligible manufacturers.
                agent in self.man_list if 
                agent.prod_cap > 0 and 
                agent.selling_price < ret.selling_price]

            if not ret.elig_ups_agents:
                continue
            
            ret.elig_ups_agents.sort(key = itemgetter(1))
            available_capacity = sum(k for _, _, k in ret.elig_ups_agents)
            
            if available_capacity <= ret.total_order_quantity:                 # If available capacity  is less than retailer's total order quantity, retailer will order in sizes equal to manufacturers' production capacity. 
                for (agent_id, _, _) in ret.elig_ups_agents:
                    ret.supplier_set.append(agent_id)
            
                ret.orders_succeeded = available_capacity
            
                for agent_id in ret.supplier_set:
                    manufacturer = self.find_agent_by_id(agent_id)                             
                    manufacturer.customer_set.append((ret.agent_id, manufacturer.prod_cap))             # Add a retailer id to the customer_set of a choosen manufacturer.
                    manufacturer.received_orders += manufacturer.prod_cap
                    manufacturer.order_quant_tracker.append((ret.agent_id,
                                                      manufacturer.prod_cap))  # A tuple of retailer id and order amount is added to the list to keep track of the orders.
                    manufacturer.prod_cap = 0
            
            else:                                                              # If the available capacity is more than retailers order quantity, retailer starts with the cheapest manufacturer and orders in amounts equal to its production capacity.
                for curr,nexx in zip(ret.elig_ups_agents[:-1], ret.elig_ups_agents[1:]):
                    if self.almost_equal_to_zero(ret.total_order_quantity, ret.abs_tol):
                        continue
                    
            
                    if curr[1] == nexx[1] and curr[2] + nexx[2] >= ret.total_order_quantity: # If two manufacturers sell with the same price, order is distributed respective to their working capital.
                        curr_wcap = self.find_agent_by_id(curr[0]).working_capital
                        nexx_wcap = self.find_agent_by_id(nexx[0]).working_capital
                        wcap_at_same_price = curr_wcap + nexx_wcap
                        order_amount = ret.total_order_quantity * (curr_wcap / wcap_at_same_price)
                        ret.orders_succeeded += order_amount
                        ret.supplier_set.append(curr[0])
                        manufacturer = self.find_agent_by_id(curr[0])
                        manufacturer.customer_set.append((ret.agent_id, order_amount))
                        manufacturer.received_orders += order_amount
                        manufacturer.order_quant_tracker.append((ret.agent_id,
                                                      order_amount))
                        manufacturer.prod_cap -= order_amount
                        ret.total_order_quantity -= order_amount

                    else:                                                      #curr[1] != nexx[1] or curr[2] + nexx[2] <= ret.total_order_quantity:
                        order_amount = min(curr[2], ret.total_order_quantity)
                        ret.orders_succeeded += order_amount
                        ret.supplier_set.append(curr[0])
                        manufacturer = self.find_agent_by_id(curr[0])
                        manufacturer.customer_set.append((ret.agent_id, order_amount))
                        manufacturer.received_orders += order_amount
                        manufacturer.order_quant_tracker.append((ret.agent_id,
                                                      order_amount))
                        manufacturer.prod_cap -= order_amount
                        ret.total_order_quantity -= order_amount

                if self.almost_equal_to_zero(ret.total_order_quantity, ret.abs_tol):
                        continue
                else:
                    last_one = ret.elig_ups_agents[-1]
                    order_amount = min(last_one[2], ret.total_order_quantity)
                    ret.orders_succeeded += order_amount
                    ret.supplier_set.append(last_one[0])
                    manufacturer = self.find_agent_by_id(last_one[0])
                    manufacturer.customer_set.append((ret.agent_id, order_amount))
                    manufacturer.received_orders += order_amount
                    manufacturer.order_quant_tracker.append((ret.agent_id,
                                                  order_amount))
                    manufacturer.prod_cap -= order_amount
                    ret.total_order_quantity -= order_amount

    def order_to_suppliers(self) -> None:
        """
        This method is responsible for handling manufacturers' ordering process.
        It receives an Agents object and takes advantage of the manufacturers'
        supplier set and suppliers' consumer set to save the ordering trace of
        the manufacturers within it's current step and also facilitates the 
        delivery of the products to the appropriate manufacturers.
        """
        if self._do_shuffle:                
            shuffle(self.man_list)                                             # No agent has priority over others in its stage.

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

            if man.total_order_quantity:
                man.total_order_quantity = 0.0

            if man.orders_succeeded:
                man.orders_succeeded = 0

            if self.almost_equal_to_zero(man.received_orders, man.abs_tol):
                continue

            man.total_order_quantity = (min(man.received_orders, man.prod_cap))
            
            man.elig_ups_agents = [(agent.agent_id, agent.selling_price, agent.prod_cap) for
                            agent in self.sup_list if 
                            agent.prod_cap > 0 and 
                            agent.selling_price < man.selling_price]
            
            if not man.elig_ups_agents:
                continue
            
            man.elig_ups_agents.sort(key = itemgetter(1))
            available_capacity = sum(k for _, _, k in man.elig_ups_agents)
            
            if available_capacity <= man.total_order_quantity:
                for (agent_id, _, _) in man.elig_ups_agents:
                    man.supplier_set.append(agent_id)
            
                man.orders_succeeded = available_capacity
            
                for agent_id in man.supplier_set:
                    supplier = self.find_agent_by_id(agent_id)                             
                    supplier.customer_set.append((man.agent_id, supplier.prod_cap))
                    supplier.received_orders += supplier.prod_cap
                    supplier.order_quant_tracker.append((man.agent_id,
                                                      supplier.prod_cap))
                    supplier.prod_cap = 0
            
            else:
                for curr,nexx in zip(man.elig_ups_agents[:-1], man.elig_ups_agents[1:]):
                    if self.almost_equal_to_zero(man.total_order_quantity, man.abs_tol):
                        continue
            
                    if curr[1] != nexx[1] or curr[2] + nexx[2] <= man.total_order_quantity:
                        order_amount = min(curr[2], man.total_order_quantity)
                        man.orders_succeeded += order_amount
                        man.supplier_set.append(curr[0])
                        supplier = self.find_agent_by_id(curr[0])
                        supplier.customer_set.append((man.agent_id, order_amount))
                        supplier.received_orders += order_amount
                        supplier.order_quant_tracker.append((man.agent_id,
                                                      order_amount))
                        supplier.prod_cap -= order_amount
                        man.total_order_quantity -= order_amount
            
                    elif curr[1] == nexx[1] and curr[2] + nexx[2] >= man.total_order_quantity:
                        curr_wcap = self.find_agent_by_id(curr[0]).working_capital
                        nexx_wcap = self.find_agent_by_id(nexx[0]).working_capital
                        wcap_at_same_price = curr_wcap + nexx_wcap
                        order_amount = man.total_order_quantity * (curr_wcap / wcap_at_same_price)
                        man.orders_succeeded += order_amount
                        man.supplier_set.append(curr[0])
                        supplier = self.find_agent_by_id(curr[0])
                        supplier.customer_set.append((man.agent_id, order_amount))
                        supplier.received_orders += order_amount
                        supplier.order_quant_tracker.append((man.agent_id,
                                                      order_amount))
                        supplier.prod_cap -= order_amount
                        man.total_order_quantity -= order_amount
            
                if self.almost_equal_to_zero(man.total_order_quantity, man.abs_tol):
                        continue
                else:
                    last_one = man.elig_ups_agents[-1]
                    order_amount = min(last_one[2], man.total_order_quantity)
                    man.orders_succeeded += order_amount
                    man.supplier_set.append(last_one[0])
                    supplier = self.find_agent_by_id(last_one[0])
                    supplier.customer_set.append((man.agent_id, order_amount))
                    supplier.received_orders += order_amount
                    supplier.order_quant_tracker.append((man.agent_id,
                                                  order_amount))
                    supplier.prod_cap -= order_amount
                    man.total_order_quantity -= order_amount

    def deliver_to_manufacturers(self) -> None:
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

            if len(sup.customer_set) == 0:                                     # Making sure supplier  has received some orders.
                sup.working_capital -= sup.fixed_cost
                continue
            else:
                if self._node_level_disruption:                                # Node level disruption is optional.
                    sup.step_production = sup.received_orders * (np.random.binomial
                                                              (n = 1, 
                                                              p = sup.p_delivery)) # Supplier produces full order amount by probability p_delivery and zero by 1-p_delivery.
                else:
                    sup.step_production = sup.received_orders

                if self.almost_equal_to_zero(sup.step_production, sup.abs_tol):
                    sup.working_capital -= sup.fixed_cost
                    continue
                else:                        
                    sup.delivery_amount =[(agent_id, sup.step_production * 
                                            (order / sup.received_orders)) for
                                          (agent_id, order) in sup.customer_set]# To deliver in amounts related to the portion of custumer order to total orders. 

                    for (agent_id, portion) in sup.delivery_amount:            # Iterating over customer agents and delivering proportionally.
                        agent = self.find_agent_by_id(agent_id)
                        agent.received_productions.append((
                            portion, sup.selling_price))                       # Kepping records of received products and their prices for customers.

                    step_profit = (sup.input_margin * sup.step_production) - ((sup.interest_rate / 12) * sup.working_capital) - sup.fixed_cost  #Calculating profit using a fixed margin for suppliers
                    sup.working_capital += step_profit                         # Updating suppliers' working capital.

    def deliver_to_retailers(self) -> None:
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

            for (amount, _) in man.received_productions:                       # Calculating total received productions.
                total_received_production += amount                            # WHAT if the length is ZERO?

            for (amount, price) in man.received_productions:                   # Calculating total money paid.
                total_money_paid += amount * price

            if len(man.customer_set) == 0 or self.almost_equal_to_zero(total_received_production, man.abs_tol):       
                man.working_capital -= man.fixed_cost
                continue
            else:
                if self._node_level_disruption:                                # Node level disruption is optional.
                    man.step_production = total_received_production * (np.random.binomial
                                                              (n = 1, 
                                                              p = man.p_delivery)) # manufacturer produces full order amount by probability p_delivery and zero by 1-p_delivery.
                else:
                    man.step_production = total_received_production

                if self.almost_equal_to_zero(man.step_production, man.abs_tol):
                    man.working_capital -= man.fixed_cost
                    continue
                else:
                    man.delivery_amount = [(agent_id, man.step_production * 
                                            (order / man.received_orders))
                                            for (agent_id, order) in man.customer_set] # Delivering in amounts related to the portion of custumer order to total orders. 

                    for (agent_id, portion) in man.delivery_amount:            # Iterating over customer agents and delivering proportionally.
                        agent = self.find_agent_by_id(agent_id)
                        agent.received_productions.append((
                            portion, man.selling_price))                      # Kepping records of received products and their prices for customers.

                    unit_production_cost = total_money_paid / total_received_production
                    step_profit = (man.selling_price * man.step_production) - (unit_production_cost * man.step_production) - ((man.interest_rate / 12) * man.working_capital) - man.fixed_cost
                    man.working_capital += step_profit

    def calculate_retailer_profit(self) -> None:
        """
        This method is responsible for calculating retailers' profits. It 
        receives an Agents object and manipulates retailers' working capital.
        """
        for ret in self.ret_list:
            if ret.total_received_production:
                ret.total_received_production = 0

            total_received_production = 0
            total_money_paid = 0

            for (amount, price) in ret.received_productions:                   # Calculating total received productions.
                total_received_production += amount                            # WHAT if the length is ZERO?                   
                total_money_paid += amount * price                             # Calculating total money paid.

            ret.total_received_production = total_received_production

            if self.almost_equal_to_zero(ret.total_received_production, ret.abs_tol):         
                ret.working_capital -= ret.fixed_cost
                continue
            else:
                unit_production_cost = total_money_paid / ret.total_received_production
                step_profit = (ret.selling_price * ret.total_received_production) - (unit_production_cost * ret.total_received_production) - ((ret.interest_rate / 12) * ret.working_capital) - ret.fixed_cost
                ret.working_capital += step_profit

    def upstream_flow(self) -> None:
        """
        Holds the methods related to the upstream flow of orders.
        """
        self.order_to_manufacturers()
        self.order_to_suppliers()

    def downstream_flow(self) -> None:
        """
        Holds the methods related to the downstraem flow of products.
        """
        self.deliver_to_manufacturers()
        self.deliver_to_retailers()
        self.calculate_retailer_profit()

    def one_round(self) -> None:
        """
        Creates a complete round of ordering and delivery.
        """
        self.realize_selling_prices()
        self.upstream_flow()
        self.downstream_flow()