# -*- coding: utf-8 -*-
"""
Created on Sun Apr  5 12:17:26 2020

@author: Farbod
"""
import unittest
from agent import Agent

class Test_Agent(unittest.TestCase):
    def setUp(self):
        a1 = Agent( agent_id = 1, role = 'r', working_capital = 120.00, selling_price = 4.50)
        
        self.ret1 = a1
  
    def test_q(self):
        self.assertEqual(self.ret1.q, 0.9)
     
    def test_mu_consumer_demand(self):
        self.assertEqual(self.ret1.mu_consumer_demand, 60)
        
    def test_sigma_consumer_demand(self):
        self.assertEqual(self.ret1.sigma_consumer_demand, 10)
    
    def test_p_delivery(self):
        self.assertEqual(self.ret1.p_delivery, 0.80)
        
    def test_max_suppliers(self):
        self.assertEqual(self.ret1.max_suppliers, 3)
        
    def test_input_margin(self):
        self.assertEqual(self.ret1.input_margin, 0.01)
        
    def test_interest_rate(self):
        self.assertEqual(self.ret1.interest_rate, 0.002) 
    
    def test_success(self):
        self.assertEqual(self.ret1.success, 1)
        
    def test_abort(self):
        self.assertEqual(self.ret1.abort, 0)
        
    def test_retailer(self):
        self.assertEqual(self.ret1.retailer,'r')
    
    def test_manufacturer(self):
        self.assertEqual(self.ret1.manufacturer, 'm')
        
    def test_supplier(self):
        self.assertEqual(self.ret1.supplier, 's')
    
    
            
if __name__ == '__main__':
    unittest.main()

