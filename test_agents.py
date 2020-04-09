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
        agents = Agents(gen.list_agents)
        
        self.agents = agents

    def test_list_agents(self):
        self.assertEqual(len(self.agents.list_agents) , 3)
        
    def test_ret_list(self):
        self.assertEqual(len(self.agents.ret_list) , 1)
    
    def test_man_list(self):
        self.assertEqual(len(self.agents.man_list) , 1)
    
    def test_sup_list(self):
        self.assertEqual(len(self.agents.sup_list) , 1)
        
    
        
        
if __name__ == '__main__':
    unittest.main()

