# -*- coding: utf-8 -*-

from agents import Agents
from recorder import Recorder


class Evolve(Recorder):
    
    def __init__(self, Agents_object: object):
        
        Recorder.__init__(self, Agents_object.list_agents)
        
        self._model = Agents_object

    @property
    def model(self) -> Agents:
        return self._model


    def proceed(self, steps: int):
        for _ in range(steps):
            try:
                self._model.one_round()
                self.current_step += 1
                self.update_log_wcap()
            except Exception as err:
                print(err)
            
        