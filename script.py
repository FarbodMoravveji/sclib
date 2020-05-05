# -*- coding: utf-8 -*-
        
from sclib.generate_agents import GenAgents
from sclib.agents import Agents
from sclib.evolve import Evolve
from sclib.visualizer import Visualizer

generate = GenAgents(excel_file = r'unittests\test_sheets\test.xlsx')
agents_object = Agents(generate.list_agents)
model = Evolve(agents_object)
model.proceed(5)
vis01 = Visualizer(dfrm = model.log_working_capital)
vis01.line_plot()
vis02 = Visualizer(dfrm = model.log_working_capital, aggregate = True)
vis02.line_plot()
