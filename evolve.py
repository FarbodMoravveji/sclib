import numpy as np
from sclib.recorder import Recorder
from sclib.order import Order_Package

class Evolve(Recorder):
    """
    This class is responsible of the evolution of a model comprised of a set of
    Agent() objects.
    """

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

    
    def determine_capacity(self):
        for agent in self.model.list_agents:
            if self.wcap_financing:
                if agent.remaining_credit_capacity == True and self.current_step >= agent.time_of_next_allowed_financing:
                    agent.prod_cap = agent.q * (agent.working_capital + agent.remaining_credit_capacity * (1 + (agent.financing_rate / 365) ** (1 / (agent.financing_period))))
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
            ret = self.model.find_agent_by_id(order.retailer_agent_id)
            elig_manufacturers= [(agent.agent_id, agent.selling_price, agent.prod_cap) for agent in self.model.man_list if agent.prod_cap > 0 and agent.selling_price < ret.selling_price]
            
            if not elig_manufacturers:
                order.order_feasibility = False
                continue
        
            elig_manufacturers.sort(key = itemgetter(1))

        # for man in self.man_list:
        #     if man.customer_set:
        #         man.customer_set = list()

        #     if man.received_orders:
        #         man.received_orders = 0.0

        #     if man.order_quant_tracker:
        #         man.order_quant_tracker = list()

        # for ret in self.ret_list:
#         if ret.consumer_demand == 0:
#             continue

#         if ret.supplier_set:
#             ret.supplier_set = list()

#         if ret.elig_ups_agents:
#             ret.elig_ups_agents = list()

#         if ret.total_order_quantity:
#             ret.total_order_quantity = 0

#         if ret.orders_succeeded:
#             ret.orders_succeeded = 0

#         ret.total_order_quantity = (min(ret.consumer_demand, ret.prod_cap))

#         if self.almost_equal_to_zero(ret.total_order_quantity, ret.abs_tol):
#             continue
        
#         ret.elig_ups_agents = [(agent.agent_id, agent.selling_price, agent.prod_cap) for   # A list of tuples containing eligible manufacturers.
#             agent in self.man_list if 
#             agent.prod_cap > 0 and 
#             agent.selling_price < ret.selling_price]

#         if not ret.elig_ups_agents:
#             continue
        
#         ret.elig_ups_agents.sort(key = itemgetter(1))
#         available_capacity = sum(k for _, _, k in ret.elig_ups_agents)
        
#         if available_capacity <= ret.total_order_quantity:                 # If available capacity  is less than retailer's total order quantity, retailer will order in sizes equal to manufacturers' production capacity. 
#             for (agent_id, _, _) in ret.elig_ups_agents:
#                 ret.supplier_set.append(agent_id)
        
#             ret.orders_succeeded = available_capacity
        
#             for agent_id in ret.supplier_set:
#                 manufacturer = self.find_agent_by_id(agent_id)                             
#                 manufacturer.customer_set.append((ret.agent_id, manufacturer.prod_cap))             # Add a retailer id to the customer_set of a choosen manufacturer.
#                 manufacturer.received_orders += manufacturer.prod_cap
#                 manufacturer.order_quant_tracker.append((ret.agent_id,
#                                                   manufacturer.prod_cap))  # A tuple of retailer id and order amount is added to the list to keep track of the orders.
#                 manufacturer.prod_cap = 0
        
#         else:                                                              # If the available capacity is more than retailers order quantity, retailer starts with the cheapest manufacturer and orders in amounts equal to its production capacity.
#             for curr,nexx in zip(ret.elig_ups_agents[:-1], ret.elig_ups_agents[1:]):
#                 if self.almost_equal_to_zero(ret.total_order_quantity, ret.abs_tol):
#                     continue
                
        
#                 if curr[1] == nexx[1] and curr[2] + nexx[2] >= ret.total_order_quantity: # If two manufacturers sell with the same price, order is distributed respective to their working capital.
#                     curr_wcap = self.find_agent_by_id(curr[0]).working_capital
#                     nexx_wcap = self.find_agent_by_id(nexx[0]).working_capital
#                     wcap_at_same_price = curr_wcap + nexx_wcap
#                     order_amount = ret.total_order_quantity * (curr_wcap / wcap_at_same_price)
#                     ret.orders_succeeded += order_amount
#                     ret.supplier_set.append(curr[0])
#                     manufacturer = self.find_agent_by_id(curr[0])
#                     manufacturer.customer_set.append((ret.agent_id, order_amount))
#                     manufacturer.received_orders += order_amount
#                     manufacturer.order_quant_tracker.append((ret.agent_id,
#                                                   order_amount))
#                     manufacturer.prod_cap -= order_amount
#                     ret.total_order_quantity -= order_amount

#                 else:                                                      #curr[1] != nexx[1] or curr[2] + nexx[2] <= ret.total_order_quantity:
#                     order_amount = min(curr[2], ret.total_order_quantity)
#                     ret.orders_succeeded += order_amount
#                     ret.supplier_set.append(curr[0])
#                     manufacturer = self.find_agent_by_id(curr[0])
#                     manufacturer.customer_set.append((ret.agent_id, order_amount))
#                     manufacturer.received_orders += order_amount
#                     manufacturer.order_quant_tracker.append((ret.agent_id,
#                                                   order_amount))
#                     manufacturer.prod_cap -= order_amount
#                     ret.total_order_quantity -= order_amount

#             if self.almost_equal_to_zero(ret.total_order_quantity, ret.abs_tol):
#                     continue
#             else:
#                 last_one = ret.elig_ups_agents[-1]
#                 order_amount = min(last_one[2], ret.total_order_quantity)
#                 ret.orders_succeeded += order_amount
#                 ret.supplier_set.append(last_one[0])
#                 manufacturer = self.find_agent_by_id(last_one[0])
#                 manufacturer.customer_set.append((ret.agent_id, order_amount))
#                 manufacturer.received_orders += order_amount
#                 manufacturer.order_quant_tracker.append((ret.agent_id,
#                                               order_amount))
#                 manufacturer.prod_cap -= order_amount
#                 ret.total_order_quantity -= order_amount
            
                
                
                
                
                
                
                




                






    # def short_term_financing(self) -> None:
    #     """
    #     This method adds to agents' working_capital.
    #     """
    #     for agent in self._model._list_agents:
    #         if agent.working_capital <= agent.wcap_floor:
    #             if self.current_step >= agent.time_of_next_allowed_financing:
    #                 print(f'current_step == {self.current_step}')
    #                 print(f'agent {agent.agent_id} with current capital of {agent.working_capital} is receiving financing')
    #                 wcap_loan = np.random.uniform(low = 0, high = agent.remaining_credit_capacity * (1 + (agent.financing_rate / 365) ** (1 / (agent.financing_period))))
    #                 agent.working_capital += wcap_loan
    #                 agent.remaining_credit_capacity -= wcap_loan * (1 + (agent.financing_rate / 365) ** (agent.financing_period))
    #                 agent.liability += wcap_loan * (1 + (agent.financing_rate / 365) ** (agent.financing_period))
    #                 agent.time_of_next_allowed_financing = self.current_step + agent.days_between_financing
    #                 agent.financing_history.append((wcap_loan * (1 + (agent.financing_rate / 365)) ** (agent.financing_period), self.current_step + agent.financing_period))  #Financing history is saved as tuples in the form of (repayment_amount, repayment_due_date)
    #                 print(f'{wcap_loan} Loan is assigned to agent {agent.agent_id}')
    #                 print(f'agent {agent.agent_id} has {agent.working_capital} working capital after financing')

    # def repay_loans(self) -> None:
    #     """
    #     This method is used to enable agents to repay the loans.
    #     """
    #     for agent in self._model.list_agents:
    #         if agent.financing_history:
    #             for (amount, due_date) in agent.financing_history:
    #                 if due_date == self.current_step:
    #                     agent.working_capital -= amount
    #                     agent.liability -= amount
    #                     agent.remaining_credit_capacity += amount
    #                     print(f'agent {agent.agent_id} repaid amount {amount} at step {self.current_step}')
            
                
                
                
    # def proceed(self, steps: int) -> None:
    #     """
    #     Pushes the model forward.
    #     """
    #     for _ in range(steps):
    #         try:
    #             self.current_step += 1
    #             if self._wcap_financing:
    #                 self.short_term_financing()
    #             self._model.one_round()
    #             if self._wcap_financing:
    #                 self.repay_loans()
    #             self.update_log_wcap()
    #             self.update_log_orders()
    #             self.update_log_delivery()
                
    #         except Exception as err:
    #             print(err)