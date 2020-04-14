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
        retailer = self.this.ret_list[0]
        print("order quantity = %f" % retailer.order_quantity)
    
    def test_man_list(self):
        self.assertEqual(len(self.this.man_list) , 1)
    
    def test_sup_list(self):
        self.assertEqual(len(self.this.sup_list) , 1)
        
    def test_almost_equal_to_zero(self):
        this = self.this
        retailer = this.ret_list[0]
        self.assertTrue(this.almost_equal_to_zero(0.05, 0.1))
        self.assertFalse(this.almost_equal_to_zero(0.15, 0.1))
        # self.assertFalse(this.almost_equal_to_zero(retailer.order_quantity, retailer.abs_tol))
    
        
    # def test_order_to_manufacturer(self):
    #     this = self.this
    #     this.order_to_manufacturers()
    #     retailer = this.ret_list[0]
    #     id_ret = retailer.agent_id
    #     manufacturer = this.man_list[0]
    #     id_man = manufacturer.agent_id
    #     self.assertTrue(retailer.elig_ups_agents)
        
        
    

if __name__ == '__main__':
    unittest.main()

