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
           
    def test_man_list(self):
        self.assertEqual(len(self.this.man_list) , 1)
    
    def test_sup_list(self):
        self.assertEqual(len(self.this.sup_list) , 1)
        
    def test_almost_equal_to_zero(self):
        this = self.this
        self.assertTrue(this.almost_equal_to_zero(0.05, 0.1))
        self.assertFalse(this.almost_equal_to_zero(0.15, 0.1))
    
    def test_find_agent_by_id(self):
        this = self.this
        a = this.find_agent_by_id(1)
        self.assertIsInstance(a, object)
   
    def test_order_to_manufacturers(self):
        this = self.this
        retailer = this.ret_list[0]
        manufacturer = this.man_list[0]
        this.order_to_manufacturers()
        self.assertTrue(retailer.elig_ups_agents)
        self.assertTrue(manufacturer.received_orders)
        self.assertTrue(manufacturer.order_quant_tracker)
        self.assertTrue(manufacturer.prod_cap)
        
        
class Test_Agents2(unittest.TestCase):
    
    def setUp(self):
        gen = GenAgents('test.xlsx')
        this = Agents(gen.list_agents)
        
        self.this = this
        
    def test_3_reps(self):
        this = self.this
        retailer = this.ret_list[0]
        manufacturer = this.man_list[0]
        for i in range(3):
            this.order_to_manufacturers()
        self.assertEqual(len(manufacturer.customer_set), 1)
        self.assertEqual(len(manufacturer.order_quant_tracker), 1)
        self.assertEqual(len(retailer.supplier_set), 1)
        self.assertEqual(len(retailer.elig_ups_agents), 1)

        
        

        
    

if __name__ == '__main__':
    unittest.main()

