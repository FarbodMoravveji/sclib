import unittest
from generate_agents import GenAgents

class Test_GenAgents(unittest.TestCase):
    
    def setUp(self):
        obj = GenAgents(r'E:\UNI\Python\ABM\3-layer prototype\Farbod\sclib\test_agents_sheets\test.xlsx')
        
        self.GA = obj
        
    def test_check_excel_file(self):
        with self.assertRaises(FileNotFoundError):
            self.GA = GenAgents("tes.xlsx")
        
    
    def test_instanciation_completion(self):
        self.assertEqual(len(self.GA.list_agents), 3)
        
    def test_instance_attrs(self):
        self.assertEqual(self.GA.list_agents[0].working_capital, 184)
        self.assertEqual(self.GA.list_agents[0].selling_price, 5.5)
        self.assertEqual(self.GA.list_agents[0].role, 'r')
        self.assertEqual(self.GA.list_agents[0].agent_id, 1)
        self.assertEqual(self.GA.list_agents[2].working_capital, 220)
        self.assertEqual(self.GA.list_agents[2].selling_price, 5.3)
        self.assertEqual(self.GA.list_agents[2].role, 's')
        self.assertEqual(self.GA.list_agents[2].agent_id, 3)
        self.assertEqual(self.GA.list_agents[2].mu_consumer_demand, 60.00)
        self.assertEqual(self.GA.list_agents[2].sigma_consumer_demand, 10.00)
        
        
if __name__ == '__main__':
    unittest.main()
    