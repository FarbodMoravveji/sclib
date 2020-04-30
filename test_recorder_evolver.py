# -*- coding: utf-8 -*-

import unittest
from evolve import Evolve

class Test_Recorder(unittest.TestCase):
    
    def setUp(self):
        self.model = Evolve(excel_file = r'test_agents_sheets\test.xlsx', steps = 5)

    def test_log_working_capital(self):
        this = self.model
        self.assertEqual(len(this.log_working_capital,6))











if __name__ == '__main__':
    unittest.main()