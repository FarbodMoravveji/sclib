import unittest
import sclib

class Test_Agent(unittest.TestCase):
    def setUp(self):
        a1 = sclib.Agent( agent_id = 1, role = 'r', working_capital = 120.00, selling_price = 4.50)
        a2 = sclib.Agent( agent_id = 2, role = 'r', working_capital = 125.00, selling_price = 4.75)
        a3 = sclib.Agent( agent_id = 3, role = 'r')
        a4 = sclib.Agent( agent_id = 4, role = 'm', working_capital = 130.00, selling_price = 4.40)
        a5 = sclib.Agent( agent_id = 5, role = 'm', working_capital = 135.00, selling_price = 4.30)
        a6 = sclib.Agent( agent_id = 6, role = 'm')
        a7 = sclib.Agent( agent_id = 7, role = 's', working_capital = 140.00, selling_price = 4.20)
        a8 = sclib.Agent( agent_id = 8, role = 's', working_capital = 139.00, selling_price = 4.10)
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
  
    def test_q(self):
        self.assertEqual(self.ret1.q, 0.9)
        
    # def test_len_al_agents(self):
    #     self.assertEqual(len(self.all_agents) , 9)

    def test_retailer_is(self):
        dct = self.ret1.__dict__
        self.assertIn('consumer_demand', dct)
        self.assertIn('supplier_set', dct)
    
    def test_mutual_attrs(self):
        self.assertEqual(self.ret1.agent_id , 1 )
        self.assertEqual(self.ret1.role , 'r')
        self.assertEqual(self.ret1.working_capital , 120)        
        self.assertEqual(self.ret1.selling_price , 4.5)
        
    def test_default_values(self):
        self.assertEqual(self.ret3.working_capital , 100)
        self.assertEqual(self.ret3.selling_price , 5)

   
    def test_retailer_attrs(self):
        self.assertNotEqual(self.ret3.consumer_demand , self.ret2.consumer_demand)
        self.assertFalse(self.ret1.supplier_set)
        self.assertFalse(self.ret1.order_quantity)
        self.assertEqual(self.ret1.supplier_set, self.ret1.received_productions)
        
    
    def test_manufacturers_attrs(self):
        self.assertFalse(self.man1.supplier_set)
        self.assertFalse(self.man1.consumer_set)
        self.assertFalse(self.man1.received_orders)
        self.assertFalse(self.man1.order_quant_tracker)
        self.assertFalse(self.man1.step_production)
        self.assertFalse(self.man1.delivery_amount)
        self.assertEqual(self.man1.prod_cap, 117)
        self.assertEqual(self.man3.prod_cap, 90)
        
    def test_suppliers_attrs(self):
        self.assertFalse(self.sup1.consumer_set)
        self.assertFalse(self.sup1.received_orders)
        self.assertFalse(self.sup1.step_production)
        self.assertFalse(self.sup1.delivery_amount)
        self.assertEqual(self.sup1.prod_cap, 126)
        self.assertEqual(self.sup3.prod_cap, 90)
    
    # def test_order_to_manuf():
    #     sclib.Agents.order_to_manufacturers(self.ret1)
        
        
if __name__ == '__main__':
    unittest.main()
