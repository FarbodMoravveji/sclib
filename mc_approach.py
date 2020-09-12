from sclib.monte_carlo_approach import Multiple_Runs

mr = Multiple_Runs(r'run_sheets\new.xlsx')
average_pds, average_dns = mr.average_pd(1000,2)
print(average_pds)
print(average_dns)
average_pds1, average_dns1 = mr.average_pd(1000,2,SC_financing = False)
print(average_pds1)
print(average_dns1)