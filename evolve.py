import numpy as np
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

        self._wcap_financing = False
    @property
    def model(self):
        return self._model

    def activate_wcap_financing(self) -> None:
        """
        Enables short term financing.
        """
        if not self._wcap_financing:
            self._wcap_financing = True

    def deactivate_wcap_financing(self) -> None:
        """
        Disables short term financing.
        """
        if self._wcap_financing:
            self._wcap_financing = False

    def short_term_financing(self) -> None:
        """
        This method adds to agents' working_capital.
        """
        for agent in self._model._list_agents:
            if agent.working_capital < agent.wcap_floor:
                print(f'agent {agent.agent_id} with {agent.working_capital} is receiving financing')
                remaining_credit_capacity = agent.credit_capacity - agent.liability
                wcap_loan = np.random.uniform(low = 0, high = remaining_credit_capacity)
                agent.working_capital += wcap_loan
                agent.financing_history.append((wcap_loan * (1 + (agent.financing_rate / 12)), self.current_step))  #Financing history is saved as tuples in the form of (repayment_amount, repayment_due_date)
                agent.liability += wcap_loan * (1 + (agent.financing_rate / 12))
                print(f'{wcap_loan} Loan is assigned to agent {agent.agent_id}')
                print(f'agent {agent.agent_id} with {agent.working_capital} has received financing')

    def repay_loans(self) -> None:
        """
        This method is used to enable agents to repay the loans.
        """
        for agent in self._model._list_agents:
            if agent.financing_history:
                for (amount, due_date) in agent.financing_history:
                    if due_date == self.current_step:
                        agent.working_capital -= amount
                        agent.liability -= amount
                        print(f'agent {agent.agent_id} with {agent.working_capital} has repaid financing')

    def proceed(self, steps: int) -> None:
        """
        Pushes the model forward.
        """
        for _ in range(steps):
            try:
                self.current_step += 1
                if self._wcap_financing:
                    self.short_term_financing()
                self._model.one_round()
                if self._wcap_financing:
                    self.repay_loans()
                self.update_log_wcap()
                self.update_log_orders()
                self.update_log_delivery()
                
            except Exception as err:
                print(err)