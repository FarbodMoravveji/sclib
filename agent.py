import sys
from sclib.parameters import Parameters

class Agent(Parameters):
    """
    The generic class to create supply chain agents.
    The initial working capital is supplied via the "working capital" variable
    and is set to default value 100.
    The type of the agent is supplied via the "role" variable supplied to the
    constructor and it can be a retailer, manufacturer or a supplier
    """
    order_quantity: float
    consumer_demand: float
    supplier_set: list
    customer_set: list
    prod_cap: float
    received_orders: float
    received_productions: list
    order_quant_tracker: list
    order_quantity: float
    step_production: float
    delivery_amount: list
    elig_ups_agents: list
    orders_succeeded: float
    total_received_production: float
    fixed_cost: float

    def __init__(self, 
                 agent_id: int, 
                 role: str, 
                 working_capital: float = 100.00, 
                 mu_selling_price: float = 5.00,
                 sigma_selling_price: float = 0.06,
                 q: float = 0.90,
                 consumer_demand_mean: float = 60,
                 p_delivery: float = 0.80,
                 input_margin: float = 0.50,
                 interest_rate: float = 0.002,
                 fixed_cost: float = 0.0,
                 days_between_financing: int = 30,
                 financing_period: int = 90,
                 ordering_period: int = 0,
                 delivery_period: int = 2):
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
        self.mu_selling_price = mu_selling_price
        self.sigma_selling_price = sigma_selling_price
        self.selling_price = 0.0
        self.q = q
        self.consumer_demand_mean = consumer_demand_mean
        self.p_delivery = p_delivery
        self.prod_cap = 0.0
        self.fixed_cost = fixed_cost
        self.input_margin = input_margin
        self.interest_rate = interest_rate
        self.ordering_period = ordering_period
        self.delivery_period = delivery_period

        ##Financing attributes:
        self.days_between_financing = days_between_financing
        self.financing_period = financing_period
        self.financing_rate = 0.15
        self.wcap_floor = 0.5 * self.working_capital
        self.liability = 0.0
        self.financing_history = list()
        self.remaining_credit_capacity = self.working_capital
        self.time_of_next_allowed_financing = 0

        self.__check_role()
        self.__assign_role_specific_attributes()

    def __assign_role_specific_attributes(self) -> None: 
        """
        Private method to add the following attributes to the following roles:

        role             consumer_demand    supplier_set  customer_set  production_capacity  received_orders  received_productions  order_quant_tracker total_order_quantity step_production delivery_amount elig_ups_agents  orders_succeeded  total_received_production
        retailer                 Y                  Y             N               N                  N                Y                  N                         Y             N                   N           Y                     Y                    Y
        manufacturer             N                  Y             Y               Y                  Y                Y                  Y                         Y             Y                   Y           Y                     Y                    N
        supplier                 N                  N             Y               Y                  Y                N                  Y                         N             Y                   Y           N                     N                    N
        """
        # a retailer has a consumer demand attribute, but others don't have it<
        # Production capacity of the supplier and manufacturers are a proportion of their total working capital 
        if self.role == self.retailer:
            self.consumer_demand = 0.0 
            self.supplier_set = list()
            self.received_productions = list()
            self.total_order_quantity = 0.0
            self.elig_ups_agents = list()
            self.orders_succeeded = 0.0
            self.total_received_production = 0.0
        elif self.role == self.manufacturer:
            self.supplier_set = list()
            self.consumer_set = list()
            self.customer_set = list()
            self.received_orders = 0.0
            self.received_productions = list()
            self.order_quant_tracker = list()
            self.total_order_quantity = 0.0
            self.step_production = 0.0
            self.delivery_amount = list()
            self.elig_ups_agents = list()
            self.orders_succeeded = 0.0
        elif self.role == self.supplier:
            self.customer_set = list()
            self.consumer_set = list()
            self.received_orders = 0.0
            self.order_quant_tracker = list()
            self.step_production = 0.0
            self.delivery_amount = list()

    def __check_role(self) -> None:
        """
        Private method to check the sanity of the role
        """
        if self.role in [self.retailer, self.manufacturer, self.supplier]:
            return 
        else:
            raise ValueError(f'__check_role: self.role = "{self.role}" is undefined')
            sys.exit(self.abort)