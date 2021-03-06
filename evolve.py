from random import shuffle
from operator import itemgetter
from collections import Counter
from statistics import mean
import scipy.stats as stats
import numpy as np
from numpy import diff, log
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

    def __init__(self, list_agents: list):
        """
        constructor
         Input:
           Agents_object: an object of Agents class.
        """        
        Recorder.__init__(self, list_agents)
        self.list_orders = list()
        self.next_agent_id = len(list_agents)

        self._wcap_financing = False
        self._SC_financing = False
        self._do_shuffle = False
        self._node_level_disruption = False
        self._seeding = False

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

    def activate_SC_financing(self) -> None:
        """
        Enables supply chain financing.
        """
        if not self._SC_financing:
            self._SC_financing = True

    def deactivate_SC_financing(self) -> None:
        """
        Disables supply chain financing.
        """
        if self._SC_financing:
            self._SC_financing = False

    def __break_list(self) -> None:
        """
        Creates lists of retailers, manufacturers and suppliers. 
        """
        self.ret_list = [agent for agent in self.list_agents if 
                          agent.role == agent.retailer]                        # Filters list_agents for retailers who should order.
        
        self.man_list = [agent for agent in self.list_agents if 
                         agent.role == agent.manufacturer]                     # Filters list_agents for manufacturers.
        
        self.sup_list = [agent for agent in self.list_agents if 
                         agent.role == agent.supplier]

    def N(self, x):
        return stats.norm.cdf(x)

    def credit_calculations(self):
        """
        This method calculates agent's distance to default and default probability
        using the calculate_assets_and_sigma_assets method to estimate market value
        of assets and sigma assets.
        """
        for agent in self.list_agents:
            if agent.bankruptcy:
                continue
            else:
                agent.distance_to_default = (agent.total_assets - agent.total_liabilities) / (agent.total_assets * agent.sigma_assets)
                agent.default_probability = self.N(-agent.distance_to_default)
                agent.default_probability_history.append((agent.default_probability, self.current_step))

    def calculate_agent_interest_rate(self):
        """
        After credit rating of the agent, the short term financing needs to be
        calculated accordingly.
        """
        for agent in self.list_agents:
            if agent.bankruptcy:
                continue
            else:
                new_rate = agent.default_probability + agent.interest_rate_margin
                agent.interest_rate = agent.risk_free_rate + agent.interest_rate_margin if new_rate <= agent.risk_free_rate else new_rate

    def check_receivables_and_payables(self):
        """
        This method check payables and receivables due date. If any accounts are
        due at the current step of the model, they will be handeled here.
        """
        for sup in self.sup_list:
            if sup.receivables and not sup.bankruptcy:
                for tup in sup.receivables:                                    # sup.receivables is a list of tuples in the form [(val, due_date, ds_id)]
                    man = self.find_agent_by_id(tup[2])
                    if tup[1] <= self.current_step and not man.in_default and not man.bankruptcy:
                        sup.working_capital += tup[0]
                        sup.receivables.remove(tup)

        for man in self.man_list:
            if man.receivables and not man.bankruptcy:
                for tup in man.receivables:                                    # man.receivables is a list of tuples in the form [(val, due_date, ds_id)]
                    ret = self.find_agent_by_id(tup[2])
                    if tup[1] <= self.current_step and not ret.in_default and not ret.bankruptcy:
                        man.working_capital += tup[0]
                        man.receivables.remove(tup)

            if man.payables:
                for tup in man.payables:                                       # man.payables is a list of tuples in the form [(val, due_date, us_id)]
                    if tup[1] <= self.current_step and not man.in_default:
                        man.working_capital -= tup[0]
                        man.payables.remove(tup)

            if man.scheduled_money_payment:
                for tup in man.scheduled_money_payment:
                    if tup[1] <= self.current_step and not man.in_default:
                        man.working_capital -= tup[0]
                        man.scheduled_money_payment.remove(tup)

        for ret in self.ret_list:
            if ret.receivables and not ret.bankruptcy:
                for tup in ret.receivables:
                    if tup[1] <= self.current_step:
                        ret.working_capital += tup[0]
                        ret.receivables.remove(tup)

            if ret.payables:
                for tup in ret.payables:
                    if tup[1] <= self.current_step and not ret.in_default:
                        ret.working_capital -= tup[0]
                        ret.payables.remove(tup)

            if ret.scheduled_money_payment:
                for tup in ret.scheduled_money_payment:
                    if tup[1] <= self.current_step and not ret.in_default:
                        ret.working_capital -= tup[0]
                        ret.scheduled_money_payment.remove(tup)

    def calculate_inventory_receivable_payable_values(self):
        """
        This method calculates inventory value at the current step
        """
        for agent in self.list_agents:
            if agent.bankruptcy:
                continue
            else:
                if not agent.inventory_track:                                      # Calculating inventory value
                    agent.inventory_value = 0
                else:
                    cur_inv = 0
                    for (val,due_date) in agent.inventory_track:
                        cur_inv += val
                    agent.inventory_value = cur_inv
    
                if not agent.receivables:                                          # Calculating receivables value
                    agent.receivables_value = 0
                else:
                    cur_rec = 0
                    for (val, due_date, _) in agent.receivables:
                        cur_rec += val
                    agent.receivables_value = cur_rec
                    
                if not agent.payables:                                             # Calculating payables value
                    agent.payables_value = 0
                else:
                    cur_pay = 0
                    for (val, due_date, _) in agent.payables:
                        cur_pay += val
                    agent.payables_value = cur_pay

    def periodic_long_term_debt_revision(self):
        """
        """
        for agent in self.list_agents:
            if not self.current_step % self._half_year and not agent.bankruptcy:
                long_term_debt_value = agent.long_term_debt
                low = long_term_debt_value * (1 - agent.ltd_volatility)
                high = long_term_debt_value * (1 + agent.ltd_volatility)
                new_long_term_debt_value = np.random.uniform(low, high)
                agent.long_term_debt = new_long_term_debt_value
                print(f'long term debt revised for agent {agent.agent_id} at step {self.current_step}')

    def update_total_assets_and_liabilities_and_equity(self):
        """
        The value of total_assets, total liabilities and equity of each agent is
        calculated by this method at the beginning of each step.
        """
        for agent in self.list_agents:
            if not agent.bankruptcy:
                agent.total_assets = agent.working_capital + agent.fixed_assets + agent.inventory_value + agent.receivables_value
                agent.list_assets.append(agent.total_assets)
                agent.total_assets_history.append((agent.total_assets, self.current_step))
                agent.total_liabilities = agent.liability + agent.payables_value + agent.long_term_debt
                agent.total_liabilities_history.append((agent.total_liabilities, self.current_step))
                agent.equity = agent.total_assets - agent.total_liabilities
                agent.list_equity.append(agent.equity)
                agent.equity_history.append((agent.equity, self.current_step))

                if self.current_step > self._credit_rating_step:
                    daily_log_return_list = diff(log(agent.list_assets))
                    yearly_log_return_list = list()
                    for i in range(len(daily_log_return_list) - self._half_year):
                        yearly_log_return_list.append(sum(daily_log_return_list[i:i + self._half_year]))
                    agent.sigma_assets = np.std(yearly_log_return_list)

    def calculate_duration_of_obligations(self):
        """
        Calculates the duration of all remaining loan obligations of the agent.
        """
        for agent in self.list_agents:
            l = list()
            if agent.financing_history:
                for (amount, _, due_date) in agent.financing_history:
                    if due_date > self.current_step:
                        l.append((amount, due_date - self.current_step))
                present_value = [(amount * (1 / (1 + (agent.financing_rate/ self._year)) ** remaining_time), remaining_time) for (amount, remaining_time) in l ]
                pv_of_total_obligations = sum(i for i, _ in present_value)
                if pv_of_total_obligations != 0:
                    timed_obligations = sum(i * j for i, j in present_value)
                    agent.duration_of_obligations = timed_obligations / pv_of_total_obligations
                else:
                    agent.duration_of_obligations = 1
            else:
                agent.duration_of_obligations = 1

    def check_reverse_factoring_availability(self):
        """
        This method goes through agent's accounts receivable to check if there
        is any sellable that can be sold. The important feature that makes a 
        receivable sellable is the better credit rating of downstream partners.
        """
        eligable_agents = [agent for agent in self.list_agents if agent.role == 's' or agent.role == 'm']
        for agent in eligable_agents:
            agent.SCF_availability = False
            if not agent.receivables:
                continue
            else:
                sellable_receivables = 0
                for (_, _, buyer_id) in agent.receivables:
                    buyer = self.find_agent_by_id(buyer_id)
                    if buyer.default_probability < agent.default_probability:
                        sellable_receivables += 1
                if sellable_receivables >= 1:
                    agent.SCF_availability = True

    def check_credit_availability(self):
        """
        This method takes into account the time gaps between financing and credit capacity 
        considerations to determine whether an agent can seek financing or not.
        """
        for agent in self.list_agents:
            if self.current_step >= agent.time_of_next_allowed_financing and agent.liability < agent.total_credit_capacity and not agent.bankruptcy:
                agent.credit_availability = True
                if len(agent.list_working_capital) > agent.days_between_financing:
                    members = agent.days_between_financing
                    tuplist = list()
                    intlist = list()
                    listt = agent.list_working_capital
                    tuplist = listt[-members:]
                    intlist = [val for val,_ in tuplist]
                    agent.total_credit_capacity = mean(intlist)
                else:
                    agent.total_credit_capacity = 100
                agent.current_credit_capacity = agent.total_credit_capacity - agent.liability
            else:
                agent.credit_availability = False

    def fixed_cost_and_cost_of_capital_subtraction(self):
        """
        This method calculates and subtracts the daily costs for each agent.
        """
        for agent in self.list_agents:
            if not agent.bankruptcy:
                step_cost = agent.fixed_cost + (agent.risk_free_rate / self._year) * agent.working_capital
                agent.working_capital -= step_cost

    def determine_capacity(self):
        """
        Production capacity of each agent is determined in this method by 
        considering its working capital and possible financing values.
        """
        for agent in self.list_agents:
            agent.SCF_capacity = 0
            agent.RF_eligible_contracts = list()
            price_mean = agent.mu_selling_price + 0.1
            if self._wcap_financing and agent.credit_availability and self._SC_financing and agent.SCF_availability and not agent.bankruptcy:
                for (amount, due_date, buyer_id) in agent.receivables:
                    buyer = self.find_agent_by_id(buyer_id)
                    if buyer.default_probability < agent.default_probability:
                        agent.RF_eligible_contracts.append((amount, due_date, buyer_id))
                for (amount, due_date, buyer_id) in agent.RF_eligible_contracts:
                    discounted_amount = (amount / (1 + (buyer.interest_rate/self._year)) ** (due_date - self.current_step))
                    feasible_amount = discounted_amount * agent.RF_ratio
                    agent.SCF_capacity += feasible_amount

                agent.prod_cap = max(0, (agent.working_capital + agent.current_credit_capacity * (1 / (1 + (agent.financing_rate / self._year)) ** agent.financing_period) + agent.SCF_capacity) / price_mean)
            elif self._wcap_financing and agent.credit_availability and not self._SC_financing and not agent.bankruptcy:
                agent.prod_cap = max(0, (agent.working_capital + agent.current_credit_capacity * (1 / (1 + (agent.financing_rate / self._year)) ** agent.financing_period)) / price_mean)
            else:
                agent.prod_cap = max(0, agent.working_capital / price_mean)

    def receive_order_by_retailers(self):
        """
        Retailers receive orders in different frequencies. In this method we 
        check to see if it is the time for agent to receive orders from costumers
        outside the supply chain.
        """
        for ret in self.ret_list:
            if ret.consumer_demand:
                ret.consumer_demand = 0.0
            if not self.current_step % ret.ordering_period and not ret.bankruptcy:
                rand_value = np.random.exponential(scale = ret.consumer_demand_mean, size = 1)[0]
                ret.consumer_demand = min(rand_value, ret.prod_cap)

    def create_order_object(self):
        """
        An order object according to order details received by the retailer is 
        created in this method.
        """
        for ret in self.ret_list:
            if ret.consumer_demand and not ret.bankruptcy:
                order_object = Order_Package(ret.consumer_demand, ret.agent_id, self.current_step, ret.selling_price)
                self.list_orders.append(order_object)

    def order_to_manufacturers(self):
        """
        Ordering behavior of retailers.
        """
        orders_to_go_up = [order for order in self.list_orders if 
                            order.completed_ordering_to_manufacturers == False]
        if self._do_shuffle:
            shuffle(orders_to_go_up)                                             # Creates Competetion within stage.

        for order in orders_to_go_up:
            remaining_order_amount = order.initial_order_amount
            retailer = self.find_agent_by_id(order.retailer_agent_id)

            elig = [(agent.agent_id, agent.selling_price, agent.prod_cap) for agent in self.man_list if agent.prod_cap > 0 and agent.selling_price < retailer.selling_price and not agent.bankruptcy]
            
            if not elig:
                order.order_feasibility = False
                continue
            
            elig.sort(key = itemgetter(1))
            
            for (agent_id, selling_price, cap) in elig:
                if self.almost_equal_to_zero(remaining_order_amount, retailer.abs_tol):
                    break
                manufacturer = self.find_agent_by_id(agent_id)
                amount = min(cap, remaining_order_amount)
                manufacturer.prod_cap -= amount
                order.manufacturers.append((agent_id, manufacturer.production_time, amount, manufacturer.selling_price))
                # retailer.orders_succeeded += amount
                remaining_order_amount -= amount
            
            order.completed_ordering_to_manufacturers = True
            order.num_manufacturers = len(order.manufacturers)

    def order_to_suppliers(self):
        """
        Ordering behavior of manufacturers.
        """
        orders_to_go_up = [order for order in self.list_orders if 
                           order.completed_ordering_to_manufacturers == True 
                           and order.completed_ordering_to_suppliers == False]

        if self._do_shuffle:
            shuffle(orders_to_go_up)                                             # Creates Competetion within stage.

        for order in orders_to_go_up:
            for order_tuple in order.manufacturers:
                manufacturer = self.find_agent_by_id(order_tuple[0])
                remaining_order_amount = order_tuple[2]
                

                elig = [(agent.agent_id, agent.selling_price, agent.prod_cap) for agent in self.sup_list if agent.prod_cap > 0 and agent.selling_price < manufacturer.selling_price and not agent.bankruptcy]

                if not elig:
                    order.order_feasibility = False
                    continue

                elig.sort(key = itemgetter(1))

                for (agent_id, selling_price, cap) in elig:
                    
                    if self.almost_equal_to_zero(remaining_order_amount, manufacturer.abs_tol):
                        break

                    supplier = self.find_agent_by_id(agent_id)
                    amount = min(cap, remaining_order_amount)
                    supplier.prod_cap -= amount
                    order.suppliers.append((agent_id, amount, self.current_step + supplier.production_time, manufacturer.agent_id, supplier.selling_price))
                    # manufacturer.orders_succeeded += amount
                    remaining_order_amount -= amount
                    price_to_pay = (1 - supplier.input_margin) * amount

                    if amount > supplier.q * supplier.working_capital and self._wcap_financing and supplier.SCF_capacity:

                        supplier.working_capital += supplier.SCF_capacity
                        supplier.SCF_history.append((supplier.SCF_capacity, self.current_step))

                        for tup1 in supplier.receivables:
                            for tup2 in supplier.RF_eligible_contracts:
                                if tup1 == tup2:
                                    buyer = self.find_agent_by_id(tup1[2])
                                    supplier.receivables.remove(tup1)
                                    new_amount = tup2[0] * (1 - supplier.RF_ratio)
                                    supplier.receivables.append((new_amount, tup2[1], tup2[2]))
                                    for tup in buyer.payables:
                                        if tup[0] == tup1[0] and tup[1] == tup1[1]:
                                            pay_to_bank = tup[0] - new_amount
                                            buyer.payables.remove(tup)
                                            buyer.payables.append((new_amount, tup[1], tup[2]))
                                            buyer.scheduled_money_payment.append((pay_to_bank, tup2[1]))
                        
                        excess_order = amount - (supplier.q * (supplier.working_capital + supplier.SCF_capacity))
                        if excess_order > 0:
                            loan_amount = excess_order / supplier.q
                            self.short_term_financing(supplier.agent_id, loan_amount)

                    elif amount > supplier.q * supplier.working_capital and self._wcap_financing:
                        excess_order = amount - (supplier.q * supplier.working_capital)
                        loan_amount = excess_order / supplier.q
                        self.short_term_financing(supplier.agent_id, loan_amount)
                    
                    supplier.working_capital -= price_to_pay
                    supplier.inventory_track.append((price_to_pay, self.current_step + supplier.production_time)) #When the agent pays for raw material, it is stored in inventory_track as the tuple (value,due_date)

                order.completed_ordering_to_suppliers = True

    def calculate_order_partners(self):
        """
        Order objects with completed ordering flow are checked in this method to
        identify agents participating in the order object.
        """
        completed_order_flow = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                                        and order.completed_ordering_to_suppliers == True 
                                        and order.created_pairs == False]
        for order in completed_order_flow:
            for (supplier_id, _, _, manufacturer_id, _) in order.suppliers:
                order.manufacturer_supplier_pairs.add((supplier_id, manufacturer_id))

            order.created_pairs = True

            counter = Counter()
            for (_, man) in order.manufacturer_supplier_pairs:
                counter[man] += 1

            for (_, man) in order.manufacturer_supplier_pairs:
                if (man, counter[man]) in order.manufacturers_num_partners:
                    continue
                else:
                    order.manufacturers_num_partners.append((man, counter[man]))

    def deliver_to_manufacturers(self):
        """
        Delivery behavior of suppliers.
        """
        begin_delivery_flow = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                               and order.completed_ordering_to_suppliers == True 
                               and order.created_pairs == True
                               and order.completed_delivering_to_manufacturers == False]
        for order in begin_delivery_flow:
            for(supplier_agent_id, amount, delivery_step, manufacturer_agent_id, price) in order.suppliers:
                if (supplier_agent_id, manufacturer_agent_id) not in order.manufacturer_supplier_pairs:
                    raise Exception(f'There is something wrong with calculate_order_partners method; It is not making all pairs')
                if delivery_step == self.current_step:
                    supplier = self.find_agent_by_id(supplier_agent_id)
                    manufacturer = self.find_agent_by_id(manufacturer_agent_id)

                    step_income = price * amount            #Calculating profit using a fixed margin for suppliers
                    # compounded_for_tc = step_income * (1 + (supplier.tc_rate / self._year))**supplier.payment_term   #Calculates the payment value under trade credit,
                    supplier.receivables.append((step_income, self.current_step + supplier.payment_term, manufacturer_agent_id))# Addine TC to receivables.
                    manufacturer.payables.append((step_income, self.current_step + supplier.payment_term, supplier_agent_id))# Adding TC to payables.
                    # supplier.working_capital += step_income
                    for tup in supplier.inventory_track:
                        if tup[1] <= self.current_step:
                            supplier.inventory_track.remove(tup)

                    # price_to_pay = compounded_for_tc
                    # manufacturer.working_capital -= price_to_pay
                    manufacturer.inventory_track.append((step_income, self.current_step + manufacturer.production_time))

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
        """
        Short  financing of manufacturers and payment to manufacturers
        are planned in this method.
        """
        plan_delivery_list = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                              and order.completed_ordering_to_suppliers == True 
                              and order.created_pairs == True]
        for order in plan_delivery_list:
            waiting_manufacturers = [manufacturer_agent_id for (manufacturer_agent_id, _) in order.manufacturers_num_partners]
            for (manufacturer_agent_id, manufacturer_production_time, amount, price) in order.manufacturers:
                if manufacturer_agent_id not in waiting_manufacturers and manufacturer_agent_id not in order.planned_manufacturers:
                    order.manufacturer_delivery_plan.append((manufacturer_agent_id, self.current_step + manufacturer_production_time, amount, price))
                    order.planned_manufacturers.append(manufacturer_agent_id)
                    manufacturer = self.find_agent_by_id(manufacturer_agent_id)

                    if amount > manufacturer.q * manufacturer.working_capital and self._wcap_financing and manufacturer.SCF_capacity:

                        manufacturer.working_capital += manufacturer.SCF_capacity
                        manufacturer.SCF_history.append((manufacturer.SCF_capacity, self.current_step))

                        for tup1 in manufacturer.receivables:
                            for tup2 in manufacturer.RF_eligible_contracts:
                                if tup1 == tup2:
                                    buyer = self.find_agent_by_id(tup1[2])
                                    manufacturer.receivables.remove(tup1)
                                    new_amount = tup2[0] * (1 - manufacturer.RF_ratio)
                                    manufacturer.receivables.append((new_amount, tup2[1], tup2[2]))
                                    for tup in buyer.payables:
                                        if tup[0] == tup1[0] and tup[1] == tup1[1]:
                                            pay_to_bank = tup[0] - new_amount
                                            buyer.payables.remove(tup)
                                            buyer.payables.append((new_amount, tup[1], tup[2]))
                                            buyer.scheduled_money_payment.append((pay_to_bank, tup2[1]))
                        
                        excess_order = amount - (manufacturer.q * (manufacturer.working_capital + manufacturer.SCF_capacity))
                        if excess_order > 0:
                            loan_amount = excess_order / manufacturer.q
                            self.short_term_financing(manufacturer.agent_id, loan_amount)

                    elif amount > manufacturer.q * manufacturer.working_capital and self._wcap_financing:
                        excess_order = amount - (manufacturer.q * manufacturer.working_capital)
                        loan_amount = excess_order / manufacturer.q
                        self.short_term_financing(manufacturer.agent_id, loan_amount)

    def deliver_to_retailer(self):
        """
        Delivery behavior of manufacturer.
        """
        possible_delivery_to_retailer = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                                         and order.completed_ordering_to_suppliers == True 
                                         and order.created_pairs == True]
        for order in possible_delivery_to_retailer:
            if order.manufacturer_delivery_plan:
                for (manufacturer_agent_id, delivery_step, amount, price) in order.manufacturer_delivery_plan:
                    if delivery_step == self.current_step:
                        retailer = self.find_agent_by_id(order.retailer_agent_id)
                        manufacturer = self.find_agent_by_id(manufacturer_agent_id)

                        step_income = (price * amount)
                        # compounded_for_tc = step_income * (1 + (manufacturer.tc_rate / self._year))**manufacturer.payment_term
                        manufacturer.receivables.append((step_income, self.current_step + manufacturer.payment_term, retailer.agent_id))
                        retailer.payables.append((step_income, self.current_step + manufacturer.payment_term, manufacturer_agent_id))
                        # manufacturer.working_capital += step_income
                        for tup in manufacturer.inventory_track:
                            if tup[1] <= self.current_step:
                                manufacturer.inventory_track.remove(tup)

                        # price_to_pay = compounded_for_tc
                        # retailer.working_capital -= price_to_pay
                        retailer.inventory_track.append((step_income, self.current_step + retailer.production_time))

                        order.amount_delivered_to_retailer += amount

                        for index, item in enumerate(order.manufacturer_delivery_plan):
                            itemlist = list(item)
                            if itemlist[0] == manufacturer_agent_id:
                                order.manufacturer_delivery_plan.remove(order.manufacturer_delivery_plan[index])
                                order.num_delivered_to_retailer += 1

    def plan_delivery_by_retailer(self):
        """
        Short term bank financing of retailer is planned in this method.
        """
        plan_delivery_list = [order for order in self.list_orders if order.completed_delivering_to_manufacturers
                              and not order.planned_delivery_by_retailer
                              and order.num_delivered_to_retailer == order.num_manufacturers]

        for order in plan_delivery_list:
            retailer = self.find_agent_by_id(order.retailer_agent_id)
            order.completion_step = self.current_step + retailer.production_time
            amount = order.amount_delivered_to_retailer
            order.planned_delivery_by_retailer = True

            if amount > retailer.q * retailer.working_capital and self._wcap_financing:
                excess_order = amount - (retailer.q * retailer.working_capital)
                loan_amount = excess_order / retailer.q
                self.short_term_financing(retailer.agent_id, loan_amount)

    def retailer_delivery(self):
        """
        Delivery behavior of retailers.
        """
        delivery_by_retailer = [order for order in self.list_orders if order.completed_delivering_to_manufacturers
                                and not order.order_completed
                                and order.completion_step == self.current_step]
        for order in delivery_by_retailer:
            retailer = self.find_agent_by_id(order.retailer_agent_id)
            step_income = (order.retailer_selling_price * order.amount_delivered_to_retailer)
            # compounded_for_tc = step_income * (1 + (retailer.tc_rate / self._year))**retailer.payment_term
            retailer.receivables.append((step_income, self.current_step + retailer.payment_term, 'outside'))
            # retailer.working_capital += step_income
            for tup in retailer.inventory_track:
                if tup[1] <= self.current_step:
                    retailer.inventory_track.remove(tup)
            order.order_completed = True

    def short_term_financing(self, agent_id, amount) -> None:
        """
        This method adds to agents' working_capital.
        """
        agent = self.find_agent_by_id(agent_id)
        agent.working_capital += amount
        compounded_value = (amount) * ((1 + (agent.financing_rate / self._year)) ** (agent.financing_period))
        agent.liability += compounded_value
        agent.time_of_next_allowed_financing = self.current_step + agent.days_between_financing
        agent.financing_history.append((compounded_value, self.current_step, self.current_step + agent.financing_period))

    def repay_debt(self) -> None:
        """
        This method is used to enable agents to repay the loans.
        """
        for agent in self.list_agents:
            if agent.financing_history and not agent.bankruptcy:
                for (amount, _, due_date) in agent.financing_history:
                    if due_date == self.current_step:
                        if agent.working_capital < amount:
                            print(f'**default situation for agent {agent.agent_id} at step {self.current_step}')
                            agent.in_default = True
                        agent.working_capital -= amount
                        agent.liability -= amount

    def check_for_bankruptcy(self):
        """
        Checking if the equity value of an agent has reached zero.
        """
        for agent in self.list_agents:
            if agent.equity <= 0 and not agent.bankruptcy:
                bankrupted_agent_role = agent.role
                agent.bankruptcy = True
                print(f'bankruptcy noticed for agent {agent.agent_id}')

                if bankrupted_agent_role == 'r':
                    self.ret_list.remove(agent)

                if bankrupted_agent_role == 'm':
                    self.man_list.remove(agent)

                if bankrupted_agent_role == 's':
                    self.sup_list.remove(agent)

    def check_working_capital(self):
        """
        This method is responsible for tracking working capital of agents at the
        end of each step.
        """
        step = self.current_step
        for agent in self.list_agents:
            if not agent.bankruptcy:
                agent.list_working_capital.append((agent.working_capital, step))

    def proceed(self, steps: int) -> None:
        """
        Pushes the model forward.
        """
        for _ in range(steps):
            try:
                self.current_step += 1
                print(f'at step: {self.current_step}')

                self.check_receivables_and_payables()
                self.calculate_inventory_receivable_payable_values()

                if self.current_step >= self._half_year:
                    self.periodic_long_term_debt_revision()

                self.update_total_assets_and_liabilities_and_equity()
                self.fixed_cost_and_cost_of_capital_subtraction()
                self.check_for_bankruptcy()

                if self.current_step > self._credit_rating_step:
                    self.credit_calculations()
                    self.calculate_agent_interest_rate()

                if self._SC_financing:
                    self.check_reverse_factoring_availability()

                if self._wcap_financing:
                    self.repay_debt()
                    self.check_credit_availability()

                self.realize_selling_prices()
                self.determine_capacity()
                self.receive_order_by_retailers()
                self.create_order_object()
                self.order_to_manufacturers()
                self.order_to_suppliers()
                self.calculate_order_partners()
                self.deliver_to_manufacturers()
                self.plan_delivery_to_retailer()
                self.deliver_to_retailer()
                self.plan_delivery_by_retailer()
                self.retailer_delivery()
                self.check_working_capital()

            except Exception as err:
                print(err)