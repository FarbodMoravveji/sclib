import unittest
from sclib.order import Order_Package

class Test_order(unittest.TestCase):

    def setUp(self):
        self.one = Order_Package(10, 5, 2)
        self.two = Order_Package(40, 4, 1)

    def test_order_number(self):
        self.assertNotEqual(self.one.order_number, self.two.order_number)

    def test_initial_order_amount(self):
        self.assertEqual(self.one.initial_order_amount, 10)
        self.assertEqual(self.two.initial_order_amount, 40)

    def test_retailer_agent_id(self):
        self.assertEqual(self.one.retailer_agent_id, 5)
        self.assertEqual(self.two.retailer_agent_id, 4)

    def test_order_initialization_step(self):
        self.assertEqual(self.one.order_initialization_step, 2)
        self.assertEqual(self.two.order_initialization_step, 1)

    def test_booleans(self):
        self.assertFalse(self.one.created_pairs)
        self.assertFalse(self.one.completed_ordering_to_manufacturers)
        self.assertFalse(self.one.completed_ordering_to_suppliers)
        self.assertFalse(self.one.completed_delivering_to_manufacturers)
        self.assertFalse(self.one.completed_delivering_to_retailer)
        self.assertFalse(self.one.order_completed)
        self.assertTrue(self.one.order_feasibility)

    def test_other_attributes(self):
        self.assertFalse(self.one.manufacturers)
        self.assertFalse(self.one.suppliers)
        self.assertFalse(self.one.manufacturer_supplier_pairs)
        self.assertFalse(self.one.manufacturer_delivery_plan)
        self.assertFalse(self.one.planned_manufacturers)
        self.assertFalse(self.one.manufacturers_num_partners)

if __name__ == '__main__':
    unittest.main()