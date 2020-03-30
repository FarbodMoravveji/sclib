import unittest
import sclib


class Test_Agent(unittest.TestCase):
    def set_Up(self):
        a1 = sclib.Agent( agent_id = 1, role = 'r', working_capital = 120, selling_price = 4.5)
        a2 = sclib.Agent( agent_id = 2, role = 'r', working_capital = 125, selling_price = 4.75)
        a3 = sclib.Agent( agent_id = 3, role = 'r')
        a4 = sclib.Agent( agent_id = 4, role = 'm', working_capital = 130, selling_price = 4.4)
        a5 = sclib.Agent( agent_id = 5, role = 'm', working_capital = 135, selling_price = 4.3)
        a6 = sclib.Agent( agent_id = 6, role = 'm')
        a7 = sclib.Agent( agent_id = 7, role = 's', working_capital = 129, selling_price = 4.2)
        a8 = sclib.Agent( agent_id = 8, role = 's', working_capital = 139, selling_price = 4.1)
        a9 = sclib.Agent( agent_id = 9, role = 's')
    
        self.ret1 = a1
        self.ret2 = a2
        self.ret3 = a3
        self.man1 = a4
        self.man2 = a5
        self.man3 = a6
        self.sup1 = a7
        self.sup2 = a8
        self.sup3 = a9
        self.params = sclib.Parameters()
    
    
    def test_q(self):
        self.assertEqual(self.param._q, 0.9)
    def test_mutual_attrs(self):
        self.assertEqual(self.ret1.agent_id , 1 )
        self.assertEqual(self.ret1.role , 'r')
        
        
        
        
if __name__ == '__main__':
    unittest.main()