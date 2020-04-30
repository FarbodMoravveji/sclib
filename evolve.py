# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from agents import Agents
from generate_agents import GenAgents
from recorder import Recorder


class Evolve(Recorder):
    
    def __init__(self, excel_file: str, steps: int):
        
        Recorder.__init__(self, excel_file, steps)

    
    def proceed(self):
        for _ in range(self.num_steps):
            try:
                self.model.one_round()
                self.current_step += 1
                self.update_log_wcap()
            except Exception as err:
                print(err)
            
        