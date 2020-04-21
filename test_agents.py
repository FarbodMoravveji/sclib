"""
Created on Mon Apr  6 18:50:26 2020

@author: Farbod
"""
import unittest
from generate_agents import GenAgents
from agents import Agents

class Test_Agents(unittest.TestCase):
    
    def setUp(self):
        gen = GenAgents(r'test_agents_sheets\test.xlsx')
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
   
class Test_order_to_manufscturers1(unittest.TestCase):
    
    def setUp(self):
        gen = GenAgents(r'test_agents_sheets\test.xlsx')
        this = Agents(gen.list_agents)
        
        self.this = this
    
    def test_order_to_manufacturers(self):
        this = self.this
        retailer = this.ret_list[0]
        manufacturer = this.man_list[0]
        this.order_to_manufacturers()
        self.assertTrue(retailer.elig_ups_agents)
        self.assertTrue(manufacturer.received_orders)
        self.assertTrue(manufacturer.order_quant_tracker)
        self.assertTrue(manufacturer.prod_cap)
        
        
class Test_order_to_manufscturers2(unittest.TestCase):
    
    def setUp(self):
        gen = GenAgents(r'test_agents_sheets\test.xlsx')
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
        self.assertEqual(retailer.elig_ups_agents[0], 2)
        self.assertEqual(manufacturer.customer_set[0], retailer.agent_id)
        self.assertEqual(manufacturer.order_quant_tracker[0][0], retailer.agent_id)
        self.assertEqual(manufacturer.order_quant_tracker[0][1], retailer.order_quantity)
        
class Test_order_to_manufscturers3(unittest.TestCase):
    def setUp(self):
        gen = GenAgents(r'test_agents_sheets\test_lots_of_agents.xlsx')
        this = Agents(gen.list_agents)
        
        self.this = this
        
    def test_lots_of_agents(self):
        this = self.this
        self.assertEqual(len(this.list_agents) , 45)
        self.assertEqual(len(self.this.ret_list) , 15)
        self.assertEqual(len(self.this.man_list) , 15)
        self.assertEqual(len(self.this.sup_list) , 15)
        ret1 = this.ret_list[0]
        ret6 = this.ret_list[5]
        ret15 = this.ret_list[14]
        man1 = this.man_list[0]
        man6 = this.man_list[5]
        man15 = this.man_list[14]
        this.order_to_manufacturers()
        self.assertEqual(len(ret1.supplier_set), 3)
        self.assertNotEqual(ret1.supplier_set, ret15.supplier_set)
        self.assertNotEqual(ret1.elig_ups_agents, ret6.elig_ups_agents)
        self.assertNotEqual(man1.customer_set, man15.customer_set)
        self.assertNotEqual(len(man1.customer_set), len(man15.customer_set))
        self.assertTrue(man1.order_quant_tracker)
        self.assertTrue(man6.order_quant_tracker)
        self.assertNotEqual(man1.order_quant_tracker, man6.order_quant_tracker)
        self.assertNotEqual(man1.order_quant_tracker[0][0], man6.order_quant_tracker[0][0])        
        self.assertNotEqual(man1.prod_cap, man6.prod_cap)
        self.assertNotEqual(man1.received_orders, man6.received_orders)
        
class Test_order_to_suppliers1(unittest.TestCase):
    
    def setUp(self):
        gen = GenAgents(r'test_agents_sheets\test.xlsx')
        this = Agents(gen.list_agents)
        
        self.this = this
        
    def test_3_reps(self):
        this = self.this
        manufacturer = this.man_list[0]
        supplier = this.sup_list[0]
        for i in range(3):
            this.order_to_manufacturers()
            this.order_to_suppliers()
        self.assertEqual(len(supplier.customer_set), 1)
        self.assertEqual(len(supplier.order_quant_tracker), 1)
        self.assertEqual(len(manufacturer.supplier_set), 1)
        self.assertEqual(len(manufacturer.elig_ups_agents), 1)
        self.assertEqual(manufacturer.elig_ups_agents[0], 3)
        self.assertEqual(supplier.customer_set[0], manufacturer.agent_id)
        self.assertEqual(supplier.order_quant_tracker[0][0], manufacturer.agent_id)
        self.assertEqual(supplier.order_quant_tracker[0][1], manufacturer.order_quantity)
        
    

if __name__ == '__main__':
    unittest.main()

