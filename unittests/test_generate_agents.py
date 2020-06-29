import unittest
from sclib.generate_agents import GenAgents

class Test_GenAgents(unittest.TestCase):
    
    def setUp(self):
        obj = GenAgents(r'test_sheets\test.xlsx')
        
        self.GA = obj
        
    def test_check_excel_file(self):
        with self.assertRaises(FileNotFoundError):
            self.GA = GenAgents("tes.xlsx")
        
    
    def test_instanciation_completion(self):
        self.assertEqual(len(self.GA.list_agents), 3)
        
    def test_instance_attrs(self):
        self.assertEqual(self.GA.list_agents[0].working_capital, 200)
        self.assertEqual(self.GA.list_agents[0].selling_price, 0)
        self.assertEqual(self.GA.list_agents[0].role, 'm')
        self.assertEqual(self.GA.list_agents[0].agent_id,2)
        self.assertEqual(self.GA.list_agents[2].working_capital,150)
        self.assertEqual(self.GA.list_agents[2].selling_price,0)
        self.assertEqual(self.GA.list_agents[2].role, 'r')
        self.assertEqual(self.GA.list_agents[2].agent_id, 1)
        self.assertEqual(self.GA.list_agents[2].consumer_demand_mean, 60.00)
        
        
if __name__ == '__main__':
    unittest.main()
    