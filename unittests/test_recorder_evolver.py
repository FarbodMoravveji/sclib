import unittest
from sclib.generate_agents import GenAgents
from sclib.agents import Agents
from sclib.evolve import Evolve
from sclib.recorder import Recorder

class Test_Recorder(unittest.TestCase):
    def setUp(self):
        generate = GenAgents(excel_file = r'test_sheets\test.xlsx')
        agents_object = Agents(generate.list_agents)
        self.this = Evolve(agents_object)

    def test_log_working_capital(self):
        this = self.this
        self.assertEqual(len(this.log_working_capital.columns), 1)
        this.proceed(5)
        self.assertEqual(len(this.log_working_capital.columns), 6)

    def test_counter(self):
        this = self.this
        self.assertEqual(this.current_step, 0)
        this.proceed(5)
        self.assertEqual(this.current_step, 5)

    def test_log_orders(self):
        this = self.this
        self.assertEqual(len(this.log_orders.columns), 1)
        this.proceed(5)
        self.assertEqual(len(this.log_orders.columns), 6)
        print(this.log_orders)

    def test_log_delivery(self):
        this = self.this
        self.assertEqual(len(this.log_delivery.columns), 1)
        this.proceed(5)
        self.assertEqual(len(this.log_delivery.columns), 6)
        print(this.log_delivery)

    def test_restart_model(self):
        model = self.this
        model.proceed(500)
        log_wcap1 = model.log_working_capital
        model.restart_model()
        log_wcap2 = model.log_working_capital
        self.assertNotEqual(log_wcap1, log_wcap2)
        

if __name__ == '__main__':
    unittest.main()