# -*- coding: utf-8 -*-

import unittest
from generate_agents import GenAgents
from agents import Agents
from evolve import Evolve
from recorder import Recorder

class Test_Recorder(unittest.TestCase):
    

    def setUp(self):
        generate = GenAgents(excel_file = r'test_agents_sheets\test.xlsx')
        agents_object = Agents(generate.list_agents)
        self.this = Evolve(agents_object)

    def test_log_working_capital(self):
        this = self.this
        self.assertEqual(len(this.log_working_capital.columns), 1)
        this.proceed(5)
        self.assertEqual(len(this.log_working_capital.columns), 6)
        print(this.log_working_capital)
        print(this.log_working_capital.values.strides)
        print('...................')
        print(this.log_working_capital.tail(1))
        # this.log_working_capital.plot()
        b = this.log_working_capital.transpose()
        ax = b.plot(title='title')
        ax.set_xlabel("x label")
        # plt.show()
        
        
    def test_counter(self):
        this = self.this
        self.assertEqual(this.current_step, 0)
        this.proceed(5)
        self.assertEqual(this.current_step, 5)










if __name__ == '__main__':
    unittest.main()