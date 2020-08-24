from random import shuffle
from operator import itemgetter
from collections import Counter
from statistics import mean
from statistics import stdev
import scipy.stats as stats
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

    def N(self, x):
        return stats.norm.cdf(x)

    def calculate_assets_and_sigma_assets(self, E, D, T, r, sigmaE):
        """
        This method estimates assets market value and its standard deviation by
        simulating KMV formulations.
        """
        n=10000
        m=2000
        diffOld=1e6 # a very big number
        for i in np.arange(1,10):
            for j in np.arange(1,m):
                A=E+D/2+i*D/n
                sigmaA=0.05+j*(1.0-0.001)/m
                d1 = (np.log(A/D)+(r+sigmaA*sigmaA/2.)*T)/(sigmaA*np.sqrt(T))
                d2 = d1-sigmaA*np.sqrt(T)
                diff4A= (A*self.N(d1)-D*np.exp(-r*T)*self.N(d2)-E)/A # scale by assets
                diff4sigmaE= A/E*self.N(d1)*sigmaA-sigmaE # a small number
                diffNew=abs(diff4A)+abs(diff4sigmaE)
                if diffNew<diffOld:
                    diffOld=diffNew
                    output=(round(A,2),round(sigmaA,4),round(diffNew,5))
        return output

    def credit_calculations(self):
        """
        This method calculates agent's distance to default and default probability
        using the calculate_assets_and_sigma_assets method to estimate market value
        of assets and sigma assets.
        """
        for agent in self.model.list_agents:
            assets, sigma_assets, _ = self.calculate_assets_and_sigma_assets(agent.equity, agent.total_liabilities + 1, agent.duration_of_obligations, agent.financing_rate, agent.sigma_equity)
            agent.distance_to_default = (assets - agent.total_liabilities) / (assets * sigma_assets)
            agent.default_probability = self.N(-agent.distance_to_default)
            agent.default_probability_history.append((agent.default_probability, self.current_step))

    def check_receivables_and_payables(self):
        for sup in self.model.sup_list:
            if sup.receivables:
                for tup in sup.receivables:                                    # sup.receivables is a list of tuples in the form [(val, due_date, ds_id)]
                    man = self.model.find_agent_by_id(tup[2])
                    if tup[1] <= self.current_step and not man.in_default:
                        sup.working_capital += tup[0]
                        sup.receivables.remove(tup)

        for man in self.model.man_list:
            if man.receivables:
                for tup in man.receivables:                                    # man.receivables is a list of tuples in the form [(val, due_date, ds_id)]
                    ret = self.model.find_agent_by_id(tup[2])
                    if tup[1] <= self.current_step and not ret.in_default:
                        man.working_capital += tup[0]
                        man.receivables.remove(tup)

            if man.payables:
                for tup in man.payables:                                       # man.payables is a list of tuples in the form [(val, due_date, us_id)]
                    if tup[1] <= self.current_step and not man.in_default:
                        man.working_capital -= tup[0]
                        man.payables.remove(tup)

        for ret in self.model.ret_list:
            if ret.receivables:
                for tup in ret.receivables:
                    if tup[1] <= self.current_step:
                        ret.working_capital += tup[0]
                        ret.receivables.remove(tup)

            if ret.payables:
                for tup in ret.payables:
                    if tup[1] <= self.current_step and not ret.in_default:
                        ret.working_capital -= tup[0]
                        ret.payables.remove(tup)

    def calculate_inventory_receivable_payable_values(self):
        """
        This method calculates inventory value at the current step
        """
        for agent in self.model.list_agents:
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

    def update_total_assets_and_liabilities_and_equity(self):
        for agent in self.model.list_agents:
            agent.total_assets = agent.working_capital + agent.fixed_assets + agent.inventory_value + agent.receivables_value
            agent.total_liabilities = agent.liability + agent.payables_value
            agent.equity = agent.total_assets - agent.total_liabilities
            agent.list_equity.append(agent.equity)
            if self.current_step > 300:
                agent.sigma_equity = stdev(agent.list_equity)

    def calculate_duration_of_obligations(self):
        """
        Calculates the duration of all remaining loan obligations to be used as
        T in KMV formulation.
        """
        for agent in self.model.list_agents:
            l = list()
            if agent.financing_history:
                for (amount, _, due_date) in agent.financing_history:
                    if due_date > self.current_step:
                        l.append((amount, due_date - self.current_step))
                present_value = [(amount * (1 / (1 + (agent.financing_rate/ 365)) ** remaining_time), remaining_time) for (amount, remaining_time) in l ]
                pv_of_total_obligations = sum(i for i, _ in present_value)
                if pv_of_total_obligations != 0:
                    timed_obligations = sum(i * j for i, j in present_value)
                    agent.duration_of_obligations = timed_obligations / pv_of_total_obligations
                else:
                    agent.duration_of_obligations = 1
            else:
                agent.duration_of_obligations = 1

    def check_credit_availability(self):
        """
        This method takes into account the time gaps between financing and credit capacity 
        considerations to determine whether an agent can seek financing or not.
        """
        for agent in self.model.list_agents:
            if self.current_step >= agent.time_of_next_allowed_financing and agent.liability < agent.total_credit_capacity:
                agent.credit_availability = True
                if self.current_step > 20:
                    members = agent.days_between_financing
                    roww = agent.agent_id
                    df = self.log_working_capital
                    col = list(df.columns)
                    mycol = col[-members:]
                    intlist = list()
                    for columnn in mycol:
                        intlist.append(df.iloc[roww][columnn])
                    agent.total_credit_capacity = mean(intlist)
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
                agent.prod_cap = max(0, agent.q * (agent.working_capital + agent.current_credit_capacity * (1 / (1 + (agent.financing_rate / 365)) ** agent.financing_period)))
            else:
                agent.prod_cap = max(0, agent.q * agent.working_capital)

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
            remaining_order_amount = order.initial_order_amount
            retailer = self.model.find_agent_by_id(order.retailer_agent_id)
            
            if retailer.orders_succeeded:
                retailer.orders_succeeded = 0

            elig = [(agent.agent_id, agent.selling_price, agent.prod_cap) for agent in self.model.man_list if agent.prod_cap > 0 and agent.selling_price < retailer.selling_price]
            
            if not elig:
                order.order_feasibility = False
                continue
            
            elig.sort(key = itemgetter(1))
            
            for (agent_id, selling_price, cap) in elig:
                if self.model.almost_equal_to_zero(remaining_order_amount, retailer.abs_tol):
                    break
                manufacturer = self.model.find_agent_by_id(agent_id)
                amount = min(cap, remaining_order_amount)
                manufacturer.prod_cap -= amount
                order.manufacturers.append((agent_id, manufacturer.production_time, amount))
                retailer.orders_succeeded += amount
                remaining_order_amount -= amount
            
            order.completed_ordering_to_manufacturers = True
            order.num_manufacturers = len(order.manufacturers)

    def order_to_suppliers(self):
        orders_to_go_up = [order for order in self.list_orders if 
                           order.completed_ordering_to_manufacturers == True 
                           and order.completed_ordering_to_suppliers == False]

        if self._do_shuffle:
            shuffle(orders_to_go_up)                                             # Creates Competetion within stage.

        for order in orders_to_go_up:
            for order_tuple in order.manufacturers:
                manufacturer = self.model.find_agent_by_id(order_tuple[0])
                remaining_order_amount = order_tuple[2]
                
                if manufacturer.orders_succeeded:
                    manufacturer.orders_succeeded = 0

                elig = [(agent.agent_id, agent.selling_price, agent.prod_cap) for agent in self.model.sup_list if agent.prod_cap > 0 and agent.selling_price < manufacturer.selling_price]

                if not elig:
                    order.order_feasibility = False
                    continue

                elig.sort(key = itemgetter(1))

                for (agent_id, selling_price, cap) in elig:
                    
                    if self.model.almost_equal_to_zero(remaining_order_amount, manufacturer.abs_tol):
                        break

                    supplier = self.model.find_agent_by_id(agent_id)
                    amount = min(cap, remaining_order_amount)
                    supplier.prod_cap -= amount
                    order.suppliers.append((agent_id, amount, self.current_step + supplier.production_time, manufacturer.agent_id))
                    manufacturer.orders_succeeded += amount
                    remaining_order_amount -= amount
                    price_to_pay = (1 - supplier.input_margin) * amount
                    
                    if amount > supplier.q * supplier.working_capital and self._wcap_financing:
                        excess_order = amount - (supplier.q * supplier.working_capital)
                        loan_amount = excess_order / supplier.q
                        self.short_term_financing(supplier.agent_id, loan_amount)
                    
                    supplier.working_capital -= price_to_pay
                    supplier.inventory_track.append((price_to_pay, self.current_step + supplier.production_time)) #When the agent pays for raw material, it is stored in inventory_track as the tuple (value,due_date)

                order.completed_ordering_to_suppliers = True

    def calculate_order_partners(self):
        completed_order_flow = [order for order in self.list_orders if order.completed_ordering_to_manufacturers == True 
                                        and order.completed_ordering_to_suppliers == True 
                                        and order.created_pairs == False]
        for order in completed_order_flow:
            for (supplier_id, _, _, manufacturer_id) in order.suppliers:
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

                    step_income = supplier.selling_price * amount            #Calculating profit using a fixed margin for suppliers
                    compounded_for_tc = step_income * (1 + (supplier.tc_rate / 365))**supplier.payment_term   #Calculates the payment value under trade credit,
                    supplier.receivables.append((compounded_for_tc, self.current_step + supplier.payment_term, manufacturer_agent_id))# Addine TC to receivables.
                    manufacturer.payables.append((compounded_for_tc, self.current_step + supplier.payment_term, supplier_agent_id))# Adding TC to payables.
                    # supplier.working_capital += step_income
                    for tup in supplier.inventory_track:
                        if tup[1] <= self.current_step:
                            supplier.inventory_track.remove(tup)

                    price_to_pay = compounded_for_tc
                    # manufacturer.working_capital -= price_to_pay
                    manufacturer.inventory_track.append((price_to_pay, self.current_step + manufacturer.production_time))

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

                    if amount > manufacturer.q * manufacturer.working_capital and self._wcap_financing:
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

                        step_income = (manufacturer.selling_price * amount)
                        compounded_for_tc = step_income * (1 + (manufacturer.tc_rate / 365))**manufacturer.payment_term
                        manufacturer.receivables.append((compounded_for_tc, self.current_step + manufacturer.payment_term, retailer.agent_id))
                        retailer.payables.append((compounded_for_tc, self.current_step + manufacturer.payment_term, manufacturer_agent_id))
                        # manufacturer.working_capital += step_income
                        for tup in manufacturer.inventory_track:
                            if tup[1] <= self.current_step:
                                manufacturer.inventory_track.remove(tup)
                        
                        price_to_pay = compounded_for_tc
                        # retailer.working_capital -= price_to_pay
                        retailer.inventory_track.append((price_to_pay, self.current_step + retailer.production_time))

                        order.amount_delivered_to_retailer += amount

                        for index, item in enumerate(order.manufacturer_delivery_plan):
                            itemlist = list(item)
                            if itemlist[0] == manufacturer_agent_id:
                                order.manufacturer_delivery_plan.remove(order.manufacturer_delivery_plan[index])
                                order.num_delivered_to_retailer += 1

    def plan_delivery_by_retailer(self):
        plan_delivery_list = [order for order in self.list_orders if order.completed_delivering_to_manufacturers
                              and not order.planned_delivery_by_retailer
                              and order.num_delivered_to_retailer == order.num_manufacturers]

        for order in plan_delivery_list:
            retailer = self.model.find_agent_by_id(order.retailer_agent_id)
            order.completion_step = self.current_step + retailer.production_time
            amount = order.amount_delivered_to_retailer
            order.planned_delivery_by_retailer = True

            if amount > retailer.q * retailer.working_capital and self._wcap_financing:
                excess_order = amount - (retailer.q * retailer.working_capital)
                loan_amount = excess_order / retailer.q
                self.short_term_financing(retailer.agent_id, loan_amount)

    def retailer_delivery(self):
        delivery_by_retailer = [order for order in self.list_orders if order.completed_delivering_to_manufacturers
                                and not order.order_completed
                                and order.completion_step == self.current_step]
        for order in delivery_by_retailer:
            retailer = self.model.find_agent_by_id(order.retailer_agent_id)
            step_income = (retailer.selling_price * order.amount_delivered_to_retailer)
            compounded_for_tc = step_income * (1 + (retailer.tc_rate / 365))**retailer.payment_term
            retailer.receivables.append((compounded_for_tc, self.current_step + retailer.payment_term, 'outside'))
            # retailer.working_capital += step_income
            for tup in retailer.inventory_track:
                if tup[1] <= self.current_step:
                    retailer.inventory_track.remove(tup)
            order.order_completed = True

    def short_term_financing(self, agent_id, amount) -> None:
        """
        This method adds to agents' working_capital.
        """
        agent = self.model.find_agent_by_id(agent_id)
        agent.working_capital += amount
        compounded_value = (amount) * ((1 + (agent.financing_rate / 365)) ** (agent.financing_period))
        agent.liability += compounded_value
        agent.time_of_next_allowed_financing = self.current_step + agent.days_between_financing
        agent.financing_history.append((compounded_value, self.current_step, self.current_step + agent.financing_period))

    def repay_debt(self) -> None:
        """
        This method is used to enable agents to repay the loans.
        """
        for agent in self._model.list_agents:
            if agent.financing_history:
                for (amount, _, due_date) in agent.financing_history:
                    if due_date == self.current_step:
                        if agent.working_capital < amount:
                            print(f'**default situation for agent {agent.agent_id} at step {self.current_step}')
                            agent.in_default = True
                        agent.working_capital -= amount
                        agent.liability -= amount            

    def check_for_bankruptcy(self):
        for agent in self.model.list_agents:
            if not agent.bankruptcy and agent.liability > agent.working_capital:
                print(f'agent {agent.agent_id} went bankrupt in step {self.current_step} with liability = {agent.liability} and working_capital = {agent.working_capital}')
                agent.bankruptcy = True

    def check_for_bankruptcy_recovery(self):
        for agent in self.model.list_agents:
            if agent.bankruptcy and agent.liability < agent.working_capital:
                print(f'agent {agent.agent_id} recovered from bankruptcy in step {self.current_step} with liability = {agent.liability} and working_capital = {agent.working_capital}')
                agent.bankruptcy = False

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
                self.update_total_assets_and_liabilities_and_equity()
                self.calculate_duration_of_obligations()
                # if self.current_step > 300:
                #     self.credit_calculations()

                if self._wcap_financing:
                    self.repay_debt()
                    self.check_credit_availability()

                self._model.realize_selling_prices()
                self.fixed_cost_and_cost_of_capital_subtraction()
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

                if self._wcap_financing:
                    self.check_for_bankruptcy()
                    self.check_for_bankruptcy_recovery()

                self.update_log_wcap()
                # self.update_log_orders()
                # self.update_log_delivery()
                
            except Exception as err:
                print(err)