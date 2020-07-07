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
            if agent.working_capital <= agent.wcap_floor:
                if self.current_step >= agent.time_of_next_allowed_financing:
                    print(f'current_step == {self.current_step}')
                    print(f'agent {agent.agent_id} with current capital of {agent.working_capital} is receiving financing')
                    wcap_loan = np.random.uniform(low = 0, high = agent.remaining_credit_capacity)
                    agent.working_capital += wcap_loan
                    agent.remaining_credit_capacity -= wcap_loan * (1 + (agent.financing_rate / 365) ** (agent.financing_period))
                    agent.liability += wcap_loan * (1 + (agent.financing_rate / 365) ** (agent.financing_period))
                    agent.time_of_next_allowed_financing = self.current_step + agent.days_between_financing
                    agent.financing_history.append((wcap_loan * (1 + (agent.financing_rate / 365)) ** (agent.financing_period), self.current_step + agent.financing_period))  #Financing history is saved as tuples in the form of (repayment_amount, repayment_due_date)
                    print(f'{wcap_loan} Loan is assigned to agent {agent.agent_id}')
                    print(f'agent {agent.agent_id} has {agent.working_capital} working capital after financing')

    def repay_loans(self) -> None:
        """
        This method is used to enable agents to repay the loans.
        """
        for agent in self._model.list_agents:
            if agent.financing_history:
                for (amount, due_date) in agent.financing_history:
                    if due_date == self.current_step:
                        agent.working_capital -= amount
                        agent.liability -= amount
                        agent.remaining_credit_capacity += amount
                        print(f'agent {agent.agent_id} repaid amount {amount} at step {self.current_step}')

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