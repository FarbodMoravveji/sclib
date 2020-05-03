# -*- coding: utf-8 -*-
        
from generate_agents import GenAgents
from agents import Agents
from evolve import Evolve
from visualizer import Visualizer

generate = GenAgents(excel_file = r'test_agents_sheets\test.xlsx')
agents_object = Agents(generate.list_agents)
model = Evolve(agents_object)
model.proceed(5)
Visualizer.line_plot(DataFrame = model.log_working_capital)