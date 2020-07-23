import unittest
from sclib.generate_agents import GenAgents
from sclib.agents import Agents
from sclib.evolve import Evolve

class Test_methods(unittest.TestCase):
    def setUp(self):
        generate = GenAgents(excel_file = r'test_sheets\test_evolve\monopoly.xlsx')
        agents_object = Agents(generate.list_agents)
        self.this = Evolve(agents_object)

    def test_check_credit_availability(self):
        model = self.this
        model.check_credit_availability()
        retailer = model.model.list_agents[0]
        manufacturer = model.model.list_agents[1]
        supplier = model.model.list_agents[2]
        self.assertTrue(retailer.credit_availability)
        self.assertTrue(manufacturer.credit_availability)
        self.assertTrue(supplier.credit_availability)

    def test_fixed_cost_and_cost_of_capital_subtraction(self):
        model = self.this
        retailer, manufacturer, supplier = model.model.list_agents
        initial_retailer_wcap = retailer.working_capital
        initial_manufacturer_wcap = manufacturer.working_capital
        initial_supplier_wcap = supplier.working_capital
        model.fixed_cost_and_cost_of_capital_subtraction()
        self.assertLess(retailer.working_capital, initial_retailer_wcap)
        self.assertLess(manufacturer.working_capital, initial_manufacturer_wcap)
        self.assertLess(supplier.working_capital, initial_supplier_wcap)


if __name__ == '__main__':
    unittest.main()