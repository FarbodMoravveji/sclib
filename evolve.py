# from sclib.agents import Agents
from sclib.recorder import Recorder

class Evolve(Recorder):
    """
    This class is responsible of the evolution of a model comprised of a set of
    Agent() objects.
    """

    def __init__(self, Agents_object: object):
        """
        constructor
         Input:
           Agents_object: an object of Agents class.
        """        
        Recorder.__init__(self, Agents_object.list_agents)
        self._model = Agents_object

    @property
    def model(self):
        return self._model

    def proceed(self, steps: int) -> None:
        """
        Pushes the model forward.
        """
        for _ in range(steps):
            try:
                self.current_step += 1
                self._model.one_round()
                self.update_log_wcap()
                self.update_log_orders()
                self.update_log_delivery()
            except Exception as err:
                print(err)