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
    consumer_demand: float
    prod_cap: float
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
                 delivery_period: int = 2,
                 fixed_assets: float = 2000,
                 payment_term: int = 10,
                 tc_rate: float = 0.1,
                 long_term_debt: float = 100):
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
        self.production_time = delivery_period
        self.fixed_assets = fixed_assets
        self.days_between_financing = days_between_financing
        self.financing_period = financing_period
        self.inventory_value = 0.0
        self.inventory_track = list()
        self.total_assets = 0.0
        self.list_assets = list()
        self.sigma_assets = 0.0
        self.total_liabilities = 0.0
        self.equity = 0.0
        self.list_equity = list()
        self.sigma_equity = 0.0
        self.estimated_assets = 0.0
        self.estimated_sigma_assets = 0.0
        self.duration_of_obligations = 0.0
        self.distance_to_default = 0.0
        self.default_probability = 0.0
        self.default_probability_history = list()
        self.payment_term = payment_term
        self.tc_rate = tc_rate
        self.long_term_debt = long_term_debt
        self.receivables = list()
        self.receivables_value = 0.0
        self.payables = list()
        self.payables_value = 0.0
        
        self.financing_rate = 0.15
        self.total_credit_capacity = self.working_capital
        self.current_credit_capacity = 0.0
        self.liability = 0.0
        self.financing_history = list()
        self.time_of_next_allowed_financing = 0.0
        self.credit_availability = False
        self.in_default = False
        self.bankruptcy = False
        self.log_liability = list()
        self.__check_role()
        self.__assign_role_specific_attributes()

    def __assign_role_specific_attributes(self) -> None: 
        """
        Private method to add the following attributes to the following roles:

        role             consumer_demand     orders_succeeded
        retailer                 Y                 Y
        manufacturer             N                 Y
        supplier                 N                 N
        """
         
        if self.role == self.retailer:
            self.consumer_demand = 0.0
            self.orders_succeeded = 0.0

        if self.role == self.manufacturer:
            self.orders_succeeded = 0.0

    def __check_role(self) -> None:
        """
        Private method to check the sanity of the role
        """
        if self.role in [self.retailer, self.manufacturer, self.supplier]:
            return 
        else:
            raise ValueError(f'__check_role: self.role = "{self.role}" is undefined')
            sys.exit(self.abort)