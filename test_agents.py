"""
Created on Mon Apr  6 18:50:26 2020

@author: Farbod
"""
import unittest
from generate_agents import GenAgents
from agents import Agents

class Test_Agents(unittest.TestCase):
    
    def setUp(self):
        gen = GenAgents('test.xlsx')
        this = Agents(gen.list_agents)
        
        self.this = this

    
    def test_list_agents(self):
        self.assertEqual(len(self.this.list_agents) , 3)
        
    def test_ret_list(self):
        self.assertEqual(len(self.this.ret_list) , 1)
        # retailer = self.this.ret_list[0]
        # print(f"mu = {retailer.mu_consumer_demand}")
        # print(f"sigma = {retailer.sigma_consumer_demand}")
        # print("order_quantity from test_agents = %f" % retailer.order_quantity)
    
    def test_man_list(self):
        self.assertEqual(len(self.this.man_list) , 1)
    
    def test_sup_list(self):
        self.assertEqual(len(self.this.sup_list) , 1)
        
    def test_almost_equal_to_zero(self):
        this = self.this
        # retailer = this.ret_list[0]
        self.assertTrue(this.almost_equal_to_zero(0.05, 0.1))
        self.assertFalse(this.almost_equal_to_zero(0.15, 0.1))
        # self.assertFalse(this.almost_equal_to_zero(retailer.order_quantity, retailer.abs_tol))
    
    def test_find_agent_by_id(self):
        this = self.this
        a = this.find_agent_by_id(1)
        self.assertIsInstance(a, object)
   
    def test_order_to_manufacturers(self):
        this = self.this
        retailer = this.ret_list[0]
        manufacturer = this.man_list[0]
        print(f"retailer consumer demand = {retailer.consumer_demand}")
        print(f"retailer order quantity = {retailer.order_quantity}")
        print(f"manufacturer initial prod_cap = {manufacturer.prod_cap}")
        print(f"manufacturer initial received_ordes = {manufacturer.received_orders}")
        print(f"manufacturer initial order_quant_tracker = {manufacturer.order_quant_tracker}")
        this.order_to_manufacturers()
        self.assertTrue(retailer.elig_ups_agents)
        print(f"manufacturer prod_cap after method = {manufacturer.prod_cap}")
        print(f"manufacturer received_ordes after method = {manufacturer.received_orders}")
        print(f"manufacturer order_quant_tracker after method = {manufacturer.order_quant_tracker}")

        
    

if __name__ == '__main__':
    unittest.main()

