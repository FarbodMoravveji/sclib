# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 09:58:25 2020

@author: Farbod
"""

class Parameters:
    """
    The Parameters class contains constant variables of the problem.
    All attributes have a getter, but no setter. The default values
    are set internally.
    """
    _q: float                       #Technological proportionality constant
    _mu_consumer_demand: float
    _sigma_consumer_demand: float
    _p_delivery: float
    _max_suppliers: int
    _input_margin: float            # Margin level of the raw materials suppliers.
    _interest_rate: float           # Interest rate constant.
    _success: int                   # error code
    _abort: int                     # error code
    _retailer: str                  # Pre-defined agent role
    _manufacturer: str              # Pre-defined agent role
    _supplier: str                  # Pre-defined agent role
    
    
    
    def __init__(self):
        """ Constructor """
        self._q = 0.90
        self._mu_consumer_demand = 60.00
        self._sigma_consumer_demand = 10.00
        self._p_delivery = 0.80
        self._max_suppliers = 3
        self._input_margin = 0.01
        self._interest_rate = 0.002
        self._success = 1
        self._abort = 0
        self._retailer = 'r'
        self._manufacturer = 'm'
        self._supplier = 's'
        

    #parameter getters.
    @property
    def q(self) -> float :
        return self._q
    
    @property
    def mu_consumer_demand(self) -> float :
        return self._mu_consumer_demand
    
    @property
    def sigma_consumer_demand(self) -> float :
        return self._sigma_consumer_demand
    
    @property
    def p_delivery(self) -> float :
        return self._p_delivery
    
    @property
    def max_suppliers(self) -> int:
        return self._max_suppliers
    
    @property
    def input_margin(self) -> float:
        return self._input_margin
    
    @property
    def interest_rate(self) -> float:
        return self._interest_rate
    
    @property
    def success(self) -> int:
        return self._success
    
    @property
    def abort(self) -> int:
        return self._abort
    
    @property
    def retailer(self) -> str:
        return self._retailer
    
    @property
    def manufacturer(self) -> str:
        return self._manufacturer
    
    @property
    def supplier(self) -> str:
        return self._supplier