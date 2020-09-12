class Order_Package:
    """
    An instance of this class is created each time an order is received by any
    agent in the output layer. The mentioned instance remains active in the model 
    until the order is delivered by the output layer and throughout this process
    the instance will be manipulated in order to keep track of the ordering 
    and delivery actions related to the initial irder.
    """

    order_number = 1

    def __init__(self, initial_order_amount, retailer_agent_id, order_initialization_step, retailer_selling_price):
        """
        constructor
         Input:
           initial_order_amount: The order amount received from outside of the network.
           retailer_agent_id: agent_id related to the retailer.
           order_initialization_step: Marks the step that the order object is created.
           retailer_selling_price: selling price of retailer at the moment of instanciating an order object.
        """
        self.order_number = Order_Package.order_number
        self.initial_order_amount = initial_order_amount
        self.amount_delivered_to_retailer = 0
        self.retailer_agent_id = retailer_agent_id
        self.order_initialization_step = order_initialization_step
        self.retailer_selling_price = retailer_selling_price
        self.completion_step = 0
        self.num_manufacturers = 0
        self.num_delivered_to_retailer = 0

        self.manufacturers = list()                                            #List of tuples by the form (agent_id, production_time, order_amount), delivery_time is added later
        self.suppliers = list()                                                #List of tuples by the form (agent_id, order_amount, delivery_time, manufacturer_id)
        self.manufacturer_supplier_pairs = set()
        self.manufacturer_delivery_plan = list()
        self.planned_manufacturers = list()
        self.manufacturers_num_partners = list()

        self.created_pairs = False
        self.completed_ordering_to_manufacturers = False
        self.completed_ordering_to_suppliers = False
        self.completed_delivering_to_manufacturers = False
        self.planned_delivery_by_retailer = False
        self.order_completed = False

        self.order_feasibility = True

        Order_Package.order_number += 1