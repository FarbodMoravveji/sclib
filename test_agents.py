"""
Created on Mon Apr  6 18:50:26 2020

@author: Farbod
"""
import unittest
from GenerateAgents import GenAgents

class Test_Agents(unittest.TestCase):
    
    def setUp(self):
        gen = GenAgents('test.xlsx')
        
        self.list_agents = gen.list_agents
        # self.ret_list = gen.ret_list
        # self.man_list = gen.man_list
        # self.sup_list = gen.sup_list
        
    def test_list_agents(self):
        self.assertEqual(len(self.list_agents) , 3)
        
    # def test_ret_list(self):
    #     self.assertEqual(len(self.ret_list) , 1)
    
    # def test_man_list(self):
    #     self.assertEqual(len(self.man_list) , 1)
    
    # def test_sup_list(self):
    #     self.assertEqual(len(self.sup_list) , 1)
        
    
        
        
if __name__ == '__main__':
    unittest.main()

