from random import shuffle
from operator import itemgetter
from collections import Counter
import numpy as np
from sclib.recorder import Recorder
from sclib.order import Order_Package

class Evolve(Recorder):
    """
    This class is responsible of the evolution of a model comprised of a set of
    Agent() objects.
    """

    do_shuffle: bool
    random_node_level_disruption: bool
    seeding: bool

    def __init__(self, Agents_object: object):
        """
        constructor
         Input:
           Agents_object: an object of Agents class.
        """        
        Recorder.__init__(self, Agents_object.list_agents)
        self._model = Agents_object
        self.list_orders = list()

        self._wcap_financing = False
        self._do_shuffle = False
        self._node_level_disruption = False
        self._seeding = False

    @property
    def model(self):
        return self._model

    def __lt__(self, object) -> bool:
        """
        necessary for gaining the ability to make instances of a class comparable.
        """
        if self.sort_num:
            return self.number < object.number
        return self.string < object.string

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

    def activate_wcap_financing(self) -> None:
        """
        Enables short term financing.
        """
        if not self._wcap_financing:
            self._wcap_financing = True

    def deactivate_wcap_financing(self) -> None:
        """
        Disables short term financing.
        """
        if self._wcap_financing:
            self._wcap_financing = False

    def check_credit_availability(self):
        """
        This method takes into account the time gaps between financing and credit capacity 
        considerations to determine whether an agent can seek financing or not.
        """
        for agent in self.model.list_agents:
            if self.current_step >= agent.time_of_next_allowed_financing and agent.liability < agent.total_credit_capacity:
                agent.credit_availability = True
                agent.current_credit_capacity = agent.total_credit_capacity - agent.liability
            else:
                agent.credit_availability = False

    def fixed_cost_and_cost_of_capital_subtraction(self):
        for agent in self.model.list_agents:
            step_cost = agent.fixed_cost + (agent.interest_rate / 365) * agent.working_capital
            agent.working_capital -= step_cost

    def determine_capacity(self):
        for agent in self.model.list_agents:
            if self._wcap_financing and agent.credit_availability:
                agent.prod_cap = agent.q * (agent.working_capital + agent.current_credit_capacity * (1 + (agent.financing_rate / 365) ** (1 / (agent.financing_period))))
            else:
                agent.prod_cap = agent.q * agent.working_capital

    def receive_order_by_retailers(self):
        for ret in self.model.ret_list:
            if ret.consumer_demand:
                ret.consumer_demand = 0.0
            if not self.current_step % ret.ordering_period:
                rand_value = np.random.exponential(scale = ret.consumer_demand_mean, size = 1)[0]
                ret.consumer_demand = min(rand_value, ret.prod_cap)

    def create_order_object(self):
        for ret in self.model.ret_list:
            if ret.consumer_demand:
                order_object = Order_Package(ret.consumer_demand, ret.agent_id, self.current_step)
                self.list_orders.append(order_object)

    def order_to_manufacturers(self):
        orders_to_go_up = [order for order in self.list_orders if 
                           order.completed_ordering_to_manufacturers == False]
        if self._do_shuffle:
            shuffle(orders_to_go_up)                                             # Creates Competetion within stage.

        for order in orders_to_go_up:
            order_amount = order.initial_order_amount
            retailer = self.model.find_agent_by_id(order.retailer_agent_id)

            if retailer.orders_succeeded:
                retailer.orders_succeeded = 0

            elig_manufacturers = [(agent.agent_id, agent.selling_price, agent.prod_cap) for agent in self.model.man_list if agent.prod_cap > 0 and agent.selling_price < retailer.selling_price]
            
            if not elig_manufacturers:
                order.order_feasibility = False
                continue
        
            elig_manufacturers.sort(key = itemgetter(1))
            available_capacity = sum(k for _, _, k in elig_manufacturers)

            if available_capacity <= order_amount:                 # If available capacity  is less than retailer's total order quantity, retailer will order in sizes equal to manufacturers' production capacity. 
                for (agent_id, _, _) in elig_manufacturers:
                    manufacturer = self.model.find_agent_by_id(agent_id)
                    order.manufacturers.append((agent_id, manufacturer.production_time, manufacturer.prod_cap))
                    retailer.orders_succeeded = available_capacity
                    manufacturer.prod_cap = 0
            else:
                for curr,nexx in zip(elig_manufacturers[:-1], elig_manufacturers[1:]):
                    
                    if self.almost_equal_to_zero(order_amount, retailer.abs_tol):
                        continue
                    
                    if curr[1] == nexx[1] and curr[2] + nexx[2] >= order_amount: # If two manufacturers sell with the same price, order is distributed respective to their working capital.
                        curr_wcap = self.model.find_agent_by_id(curr[0]).working_capital
                        nexx_wcap = self.model.find_agent_by_id(nexx[0]).working_capital
                        wcap_at_same_price = curr_wcap + nexx_wcap
                        amount = order_amount * (curr_wcap / wcap_at_same_price)
    
                        manufacturer = self.model.find_agent_by_id(curr[0])
                        order.manufacturers.append((manufacturer.agent_id, manufacturer.production_time, amount))
                        retailer.orders_succeeded += amount
                        manufacturer.prod_cap -= amount
                        order_amount -= amount

                    else:                                                      #curr[1] != nexx[1] or curr[2] + nexx[2] <= ret.total_order_quantity:
                        amount = min(curr[2], order_amount)
                        manufacturer = self.model.find_agent_by_id(curr[0])
                        order.manufacturers.append((manufacturer.agent_id, manufacturer.production_time, amount))
                        retailer.orders_succeeded += amount
                        manufacturer.prod_cap -= amount
                        order_amount -= amount

                if self.model.almost_equal_to_zero(order_amount, retailer.abs_tol):
                    continue
                else:
                    last_one = elig_manufacturers[-1]
                    amount = min(last_one[2], order_amount)
                    manufacturer = self.model.find_agent_by_id(last_one[0])
                    order.manufacturers.append((manufacturer.agent_id, manufacturer.production_time, amount))
                    retailer.orders_succeeded += amount
                    manufacturer.prod_cap -= amount
                    order_amount -= amount

            order.completed_ordering_to_manufacturers = True

    def order_to_supplier(self):
        orders_to_go_up = [order for order in self.list_orders if 
                           order.completed_ordering_to_manufacturers == True 
                           and order.completed_ordering_to_manufacturers == False]
        
        if self._do_shuffle:
            shuffle(orders_to_go_up)                                             # Creates Competetion within stage.

        for order in orders_to_go_up:
            for order_tuple in order.manufacturers:
                manufacturer = self.model.find_agent_by_id(order_tuple[0])
                order_amount = order_tuple[2]
                
                if manufacturer.orders_succeeded:
                    manufacturer.orders_succeeded = 0

                elig_suppliers = [(agent.agent_id, agent.selling_price, agent.prod_cap) for agent in self.model.sup_list if agent.prod_cap > 0 and agent.selling_price < manufacturer.selling_price]

                if not elig_suppliers:
                    order.order_feasibility = False
                    continue
                elig_suppliers.sort(key = itemgetter(1))
                available_capacity = sum(k for _, _, k in elig_suppliers)

                if available_capacity <= order_amount:                 # If available capacity  is less than retailer's total order quantity, retailer will order in sizes equal to manufacturers' production capacity. 
                    for (agent_id, _, _) in elig_suppliers:
                        supplier = self.model.find_agent_by_id(agent_id)
                        order.suppliers.append((agent_id, supplier.prod_cap, self.current_step + supplier.production_time, manufacturer.agent_id))
                        supplier.orders_succeeded = available_capacity
                        supplier.prod_cap = 0
                else:
                    for curr,nexx in zip(elig_suppliers[:-1], elig_suppliers[1:]):

                    if self.almost_equal_to_zero(order_amount, retailer.abs_tol):
                        continue

                        if curr[1] == nexx[1] and curr[2] + nexx[2] >= order_amount: # If two manufacturers sell with the same price, order is distributed respective to their working capital.
                            curr_wcap = self.model.find_agent_by_id(curr[0]).working_capital
                            nexx_wcap = self.model.find_agent_by_id(nexx[0]).working_capital
                            wcap_at_same_price = curr_wcap + nexx_wcap
                            amount = order_amount * (curr_wcap / wcap_at_same_price)
        
                            supplier = self.model.find_agent_by_id(curr[0])
                            order.suppliers.append((supplier.agent_id, amount, self.current_step + supplier.production_time, manufacturer.agent_id))
                            manufacturer.orders_succeeded += amount
                            supplier.prod_cap -= amount
                            order_amount -= amount
    
                        else:                                                      #curr[1] != nexx[1] or curr[2] + nexx[2] <= ret.total_order_quantity:
                            amount = min(curr[2], order_amount)
                            supplier = self.model.find_agent_by_id(curr[0])
                            order.suppliers.append((supplier.agent_id, amount, self.current_step + supplier.production_time, manufacturer.agent_id))
                            manufacturer.orders_succeeded += amount
                            supplier.prod_cap -= amount
                            order_amount -= amount
    
                    if self.model.almost_equal_to_zero(order_amount, manufacturer.abs_tol):
                        continue
                    else:
                        last_one = elig_suppliers[-1]
                        amount = min(last_one[2], order_amount)
                        supplier = self.model.find_agent_by_id(last_one[0])
                        order.suppliers.append((supplier.agent_id, amount, self.current_step + supplier.production_time, manufacturer.agent_id))
                        manufacturer.orders_succeeded += amount
                        supplier.prod_cap -= amount
                        order_amount -= amount
    
                order.completed_ordering_to_suppliers = True

    
    def calculate_order_partners(self):
        completed_order_flow = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                                        and order.completed_ordering_to_suppliers == True 
                                        and order.created_pairs == False]
        for order in completed_order_flow:
            for (supplier_id, _, _, manufacturer_id) in order.suppliers:
                if (supplier_id, manufacturer_id) in order.manufacturer_supplier_pairs:
                    raise Exception(f'There is something wrong with saving orders is order.suppliers; It is saving duplicates')
                else:
                    order.manufacturer_supplier_pairs.add((supplier_id, manufacturer_id))
            order.created_pairs == True

            counter = Counter()
            for (_, man) in order.manufacturer_supplier_pairs:
                counter[man] += 1

            for (_, man) in order.manufacturer_supplier_pairs:
                if (man, counter[man]) in order.manufacturers_num_partners:
                    continue
                else:
                    order.manufacturers_num_partners.append((man, counter[man]))

    def deliver_to_manufacturers(self):
        begin_delivery_flow = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                               and order.completed_ordering_to_suppliers == True 
                               and order.created_pairs == True
                               and order.completed_delivering_to_manufacturers == False]
        for order in begin_delivery_flow:
            for(supplier_agent_id, amount, delivery_step, manufacturer_agent_id) in order.suppliers:
                if (supplier_agent_id, manufacturer_agent_id) not in order.manufacturer_supplier_pairs:
                    raise Exception(f'There is something wrong with calculate_order_partners method; It is not making all pairs')
                if delivery_step == self.current_step:
                    supplier = self.model.find_agent_by_id(supplier_agent_id)
                    manufacturer = self.model.find_agent_by_id(manufacturer_agent_id)

                    if amount > supplier.q * supplier.working_capital:
                        excess_order = order - (supplier.q * supplier.working_capital)
                        loan_amount = excess_order / supplier.q
                        self.short_term_financing(supplier_agent_id, loan_amount)
                    
                    step_income = (supplier.selling_price * amount) - (1 - supplier.input_margin) * amount       #Calculating profit using a fixed margin for suppliers
                    supplier.working_capital += step_income
                    manufacturer.working_capital -= supplier.selling_price * amount
                    
                    for index, item in enumerate(order.manufacturers_num_partners):
                        itemlist = list(item)
                        if itemlist[0] == manufacturer_agent_id:
                            itemlist[1] = itemlist[1] - 1
                        item = tuple(itemlist)
                        if item[1] == 0:
                            order.manufacturers_num_partners.remove(order.manufacturers_num_partners[index])
                        else:
                            order.manufacturers_num_partners[index] = item
            if not order.manufacturers_num_partners:
                order.completed_delivering_to_manufacturers = True

    def plan_delivery_to_retailer(self):
        plan_delivery_list = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                              and order.completed_ordering_to_suppliers == True 
                              and order.created_pairs == True]
        for order in plan_delivery_list:
            waiting_manufacturers = [manufacturer_agent_id for (manufacturer_agent_id, _) in order.manufacturers_num_partners]
            for (manufacturer_agent_id, manufacturer_production_time, amount) in order.manufacturers:
                if manufacturer_agent_id not in waiting_manufacturers and manufacturer_agent_id not in order.planned_manufacturers:
                    order.manufacturer_delivery_plan.append((manufacturer_agent_id, self.current_step + manufacturer_production_time, amount))
                    order.planned_manufacturers.append(manufacturer_agent_id)
                    manufacturer = self.model.find_agent_by_id(manufacturer_agent_id)

                    if amount > manufacturer.q * manufacturer.working_capital:
                        excess_order = amount - (manufacturer.q * manufacturer.working_capital)
                        loan_amount = excess_order / manufacturer.q
                        self.short_term_financing(manufacturer.agent_id, loan_amount)

    def deliver_to_retailer(self):
        possible_delivery_to_retailer = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                                         and order.completed_ordering_to_suppliers == True 
                                         and order.created_pairs == True]
        for order in possible_delivery_to_retailer:
            if order.manufacturer_delivery_plan:
                for (manufacturer_agent_id, delivery_step, amount) in order.manufacturer_delivery_plan:
                    if delivery_step == self.current_step:
                        retailer = self.model.find_agent_by_id(order.retailer_agent_id)
                        manufacturer = self.model.find_agent_by_id(manufacturer_agent_id)

                        step_income = (manufacturer.selling_price * amount)        #Calculating profit using a fixed margin for suppliers
                        manufacturer.working_capital += step_income
                        retailer.working_capital -= step_income
                        order.amount_delivered_to_retailer += amount

                        for index, item in enumerate(order.manufacturer_delivery_plan):
                            itemlist = list(item)
                            if itemlist[0] == manufacturer_agent_id:
                                order.manufacturer_delivery_plan.remove(order.manufacturer_delivery_plan[index])

    def plan_delivery_by_retailer(self):
        plan_delivery_list = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                              and order.completed_ordering_to_suppliers == True 
                              and order.created_pairs == True
                              and order.amount_delivered_to_retailer == order.initial_order_amount]
        
        for order in plan_delivery_list:
            retailer = self.model.find_agent_by_id(order.retailer_agent_id)
            order.completion_step = self.current_step + retailer.production_time
            amount = order.amount_delivered_to_retailer

            if amount > retailer.q * retailer.working_capital:
                excess_order = amount - (retailer.q * retailer.working_capital)
                loan_amount = excess_order / retailer.q
                self.short_term_financing(retailer.agent_id, loan_amount)

    def retailer_delivery(self):
        delivery_by_retailer = [order for order in self.list_orders if order.completion_step == self.current_step]
        for order in delivery_by_retailer:
            retailer = self.model.find_agent_by_id(order.retailer_agent_id)
            step_income = (retailer.selling_price * order.amount_delivered_to_retailer)
            retailer.working_capital += step_income
            order.order_completed = True

    def short_term_financing(self, agent_id, amount) -> None:
        """
        This method adds to agents' working_capital.
        """
        agent = self.model.find_agent_by_id(agent_id)
        agent.working_capital += amount
        agent.liability += amount * (1 + (agent.financing_rate / 365) ** (agent.financing_period))
        agent.time_of_next_allowed_financing = self.current_step + agent.days_between_financing
        agent.financing_history.append((amount * (1 + (agent.financing_rate / 365)) ** (agent.financing_period), self.current_step + agent.financing_period))

    def repay_debt(self) -> None:
        """
        This method is used to enable agents to repay the loans.
        """
        for agent in self._model.list_agents:
            if agent.financing_history:
                for (amount, due_date) in agent.financing_history:
                    if due_date == self.current_step:
                        agent.working_capital -= amount
                        agent.liability -= amount            

    def proceed(self, steps: int) -> None:
        """
        Pushes the model forward.
        """
        for _ in range(steps):
            try:
                self.current_step += 1

                if self._wcap_financing:
                    self.repay_debt()
                    self.check_credit_availability()

                self._model.realize_selling_prices()
                self.fixed_cost_and_cost_of_capital_subtraction()
                self.determine_capacity()
                self.receive_order_by_retailers()
                self.create_order_object()
                self.order_to_manufacturers()
                self.order_to_supplier()
                self.calculate_order_partners()
                self.deliver_to_manufacturers()
                self.plan_delivery_to_retailer()
                self.deliver_to_retailer()
                self.plan_delivery_by_retailer()
                self.retailer_delivery()

                self.update_log_wcap()
                # self.update_log_orders()
                # self.update_log_delivery()
                
            except Exception as err:
                print(err)