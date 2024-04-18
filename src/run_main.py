# -*- coding: utf-8 -*-
"""
Created on Mon May 17 10:21 2021

@author: Xavier Rixhon
"""

import os, sys
from os import system
from pathlib import Path
import webbrowser
import time
import multiprocessing as mp
import pickle as pkl
import plotly.io as pio

curr_dir = Path(os.path.dirname(__file__))

pymodPath = os.path.abspath(os.path.join(curr_dir.parent,'pylib'))
sys.path.insert(0, pymodPath)

from ampl_object import AmplObject
from ampl_preprocessor import AmplPreProcessor
from ampl_collector import AmplCollector
from ampl_graph import AmplGraph


type_of_model = 'TD'
nbr_tds = 12

run_opti = True
graph = True
graph_comp = False

pth_esmy = os.path.join(curr_dir.parent,'ESMY')

pth_model = os.path.join(pth_esmy,'STEP_2_Pathway_Model')

if type_of_model == 'MO':
    mod_1_path = [os.path.join(pth_model,'PESMO_model.mod'),
                os.path.join(pth_model,'PESMO_store_variables.mod'),
                os.path.join(pth_model,'PESMO_RL/PESMO_RL_v7.mod'),
                os.path.join(pth_model,'PES_store_variables.mod')]
    mod_2_path = [os.path.join(pth_model,'PESMO_initialise_2021.mod'),
                  os.path.join(pth_model,'fix.mod')]
    dat_path = [os.path.join(pth_model,'PESMO_data_all_years.dat')]
else:
    mod_1_path = [os.path.join(pth_model,'PESTD_model.mod'),
            os.path.join(pth_model,'PESTD_store_variables.mod'),
            os.path.join(pth_model,'PESTD_RL/PESTD_RL_v8.mod'),
            os.path.join(pth_model,'PES_store_variables.mod')]
    mod_2_path = [os.path.join(pth_model,'PESTD_initialise_2021.mod'),
              os.path.join(pth_model,'fix.mod')]
    dat_path = [os.path.join(pth_model,'PESTD_data_all_years.dat'),
                os.path.join(pth_model,'PESTD_{}TD.dat'.format(nbr_tds))]

dat_path += [os.path.join(pth_model,'PES_data_all_years.dat'),
             os.path.join(pth_model,'PES_seq_opti.dat'),
             os.path.join(pth_model,'PES_data_year_related_NZE.dat'),
             os.path.join(pth_model,'PES_data_efficiencies.dat'),
             os.path.join(pth_model,'PES_data_set_AGE_2021.dat')]
dat_path_0 = dat_path + [os.path.join(pth_model,'PES_data_remaining.dat'),
             os.path.join(pth_model,'PES_data_decom_allowed_2021.dat')]

dat_path += [os.path.join(pth_model,'PES_data_remaining_wnd.dat'),
             os.path.join(pth_model,'PES_data_decom_allowed_2021.dat')]

## Options for ampl and gurobi
gurobi_options = ['predual=-1',
                'method = 2', # 2 is for barrier method
                'crossover=0', #-1 let gurobi decide
                'prepasses = 3',
                'barconvtol=1e-6',
                'presolve=-1'] # Not a good idea to put it to 0 if the model is too big

gurobi_options_str = ' '.join(gurobi_options)

ampl_options = {'show_stats': 1,
                'log_file': os.path.join(pth_model,'log.txt'),
                'presolve': 10,
                'presolve_eps': 1e-6,
                'presolve_fixeps': 1e-6,
                'show_boundtol': 0,
                'gurobi_options': gurobi_options_str,
                '_log_input_only': False}

###############################################################################
''' main script '''
###############################################################################

if __name__ == '__main__':
    
    ## Paths
    pth_output_all = os.path.join(curr_dir.parent,'out')
    
    N_year_opti = [30]
    N_year_overlap = [0]


    for m in range(len(N_year_opti)):
        
        # TO DO ONCE AT INITIALISATION OF THE ENVIRONMENT
        i = 0
        n_year_opti = N_year_opti[m]
        n_year_overlap = N_year_overlap[m]
        
      
        case_study = '{}_{}_{}_gwp_limit_all_the_way'.format(type_of_model,n_year_opti,n_year_overlap)
        expl_text = 'GWP limit all the way up to 2050, to reach carbon neutrality with {} years of time window and {} years of overlap'.format(n_year_opti,n_year_overlap)
        
        output_folder = os.path.join(pth_output_all,case_study)
        output_file = os.path.join(output_folder,'_Results.pkl')
        ampl_0 = AmplObject(mod_1_path, mod_2_path, dat_path_0, ampl_options, type_model = type_of_model)
        ampl_0.clean_history()
        ampl_pre = AmplPreProcessor(ampl_0, n_year_opti, n_year_overlap)
        ampl_collector = AmplCollector(ampl_pre, output_file, expl_text)
        
        t = time.time()
        
        if run_opti:
        
            for i in range(len(ampl_pre.years_opti)):
            # TO DO AT EVERY STEP OF THE TRANSITION
                t_i = time.time()
                curr_years_wnd = ampl_pre.write_seq_opti(i).copy()
                ampl_pre.remaining_update(i)
                
                ampl = AmplObject(mod_1_path, mod_2_path, dat_path, ampl_options, type_model = type_of_model)
                
                ampl.set_params('gwp_limit',{('YEAR_2015'):800000}) # 150000
                ampl.set_params('gwp_limit',{('YEAR_2021'):800000}) # 150000
                ampl.set_params('gwp_limit',{('YEAR_2025'):20833})  # 95486
                ampl.set_params('gwp_limit',{('YEAR_2030'):16666})  # 71615
                ampl.set_params('gwp_limit',{('YEAR_2035'):12499})  # 47743
                ampl.set_params('gwp_limit',{('YEAR_2040'):8332})  # 32329
                ampl.set_params('gwp_limit',{('YEAR_2045'):4165})  # 16915
                ampl.set_params('gwp_limit',{('YEAR_2050'):50})   # 1500

                # ampl.set_params('gwp_limit',{('YEAR_2015'):800000}) # 150000
                # ampl.set_params('gwp_limit',{('YEAR_2021'):800000}) # 150000
                # ampl.set_params('gwp_limit',{('YEAR_2025'):20833})  # 95486
                # ampl.set_params('gwp_limit',{('YEAR_2030'):16666})  # 71615
                # ampl.set_params('gwp_limit',{('YEAR_2035'):12499})  # 47743
                # ampl.set_params('gwp_limit',{('YEAR_2040'):8332})  # 32329
                # ampl.set_params('gwp_limit',{('YEAR_2045'):4165})  # 16915
                # ampl.set_params('gwp_limit',{('YEAR_2050'):25})   # 1500

                # ampl.set_params('gwp_limit',{('YEAR_2015'):800000}) # 150000
                # ampl.set_params('gwp_limit',{('YEAR_2021'):800000}) # 150000
                # ampl.set_params('gwp_limit',{('YEAR_2025'):24064})  # 95486
                # ampl.set_params('gwp_limit',{('YEAR_2030'):23064})  # 71615
                # ampl.set_params('gwp_limit',{('YEAR_2035'):22064})  # 47743
                # ampl.set_params('gwp_limit',{('YEAR_2040'):21064})  # 32329
                # ampl.set_params('gwp_limit',{('YEAR_2045'):20064})  # 16915
                # ampl.set_params('gwp_limit',{('YEAR_2050'):17750})   # 1500

                # ampl.set_params('gwp_limit',{('YEAR_2015'):800000}) # 150000
                # ampl.set_params('gwp_limit',{('YEAR_2021'):800000}) # 150000
                # ampl.set_params('gwp_limit',{('YEAR_2025'):24064})  # 95486
                # ampl.set_params('gwp_limit',{('YEAR_2030'):23064})  # 71615
                # ampl.set_params('gwp_limit',{('YEAR_2035'):22064})  # 47743
                # ampl.set_params('gwp_limit',{('YEAR_2040'):21064})  # 32329
                # ampl.set_params('gwp_limit',{('YEAR_2045'):20064})  # 16915
                # ampl.set_params('gwp_limit',{('YEAR_2050'):17750})   # 1500

                # ampl.set_params('gwp_limit',{('YEAR_2015'):800000}) # 150000
                # ampl.set_params('gwp_limit',{('YEAR_2021'):800000}) # 150000
                # ampl.set_params('gwp_limit',{('YEAR_2025'):800000})  # 95486
                # ampl.set_params('gwp_limit',{('YEAR_2030'):800000})  # 71615
                # ampl.set_params('gwp_limit',{('YEAR_2035'):800000})  # 47743
                # ampl.set_params('gwp_limit',{('YEAR_2040'):800000})  # 32329
                # ampl.set_params('gwp_limit',{('YEAR_2045'):800000})  # 16915
                # ampl.set_params('gwp_limit',{('YEAR_2050'):800000})   # 1500

                # valor_gwp_limit_transition = 90000
                # ampl.set_params('gwp_limit_transition', valor_gwp_limit_transition)

                solve_result = ampl.run_ampl()
                ampl.get_results()
                
                if i==0: 
                    ampl_collector.init_storage(ampl)
                
                
                if i > 0:
                    curr_years_wnd.remove(ampl_pre.year_to_rm)
                
                ampl_collector.update_storage(ampl,curr_years_wnd,i)
                
                ampl.set_init_sol()
                
                elapsed_i = time.time()-t_i
                print('Time to solve the window #'+str(i+1)+': ',elapsed_i)
                
                
                if i == len(ampl_pre.years_opti)-1:
                    elapsed = time.time()-t
                    print('Time to solve the whole problem: ',elapsed)
                    ampl_collector.clean_collector()
                    ampl_collector.pkl()
                    break
        if graph:
            ampl_graph = AmplGraph(output_file, ampl_0, case_study)
            z_Results = ampl_graph.ampl_collector
            z_Assets = z_Results['Assets'].copy()
            z_Cost_breakdown = z_Results['Cost_breakdown'].copy()
            z_Resources = z_Results['Resources'].copy()
            z_Year_balance = z_Results['Year_balance'].copy()
            z_gwp_breakdown = z_Results['Gwp_breakdown'].copy()
            
            # Define the directory to save CSV files
            csv_dir = os.path.join(output_folder, 'csv_result_files')
            
            # Create the directory if it doesn't exist
            os.makedirs(csv_dir, exist_ok=True)
            
            # Save each DataFrame to a separate CSV file with ';' separator and including the index
            z_Assets.to_csv(os.path.join(csv_dir, 'assets.csv'), sep=';', index=True)
            z_Cost_breakdown.to_csv(os.path.join(csv_dir, 'cost_breakdown.csv'), sep=';', index=True)
            z_Resources.to_csv(os.path.join(csv_dir, 'resources.csv'), sep=';', index=True)
            z_Year_balance.to_csv(os.path.join(csv_dir, 'year_balance.csv'), sep=';', index=True)
            z_gwp_breakdown.to_csv(os.path.join(csv_dir, 'gwp_breakdown.csv'), sep=';', index=True)
            
            # Generate the plotly figure
            html_file_path = ampl_graph.graph_resource()  # This now returns the path to the HTML file
            
            # Print the path to the HTML file for reference
            print("HTML file saved at:", html_file_path)

            ampl_graph.graph_tech_cap()
            ampl_graph.graph_gwp_per_sector()
#        if graph:
#            ampl_graph = AmplGraph(output_file, ampl_0, case_study)
#            z_Results = ampl_graph.ampl_collector
#            z_Assets = z_Results['Assets'].copy()
#            z_Cost_breakdown = z_Results['Cost_breakdown'].copy()
#            z_Resources = z_Results['Resources'].copy()
#            z_Year_balance = z_Results['Year_balance'].copy()
#            z_gwp_breakdown = z_Results['Gwp_breakdown'].copy()
#            a_website = "https://www.google.com"
#            webbrowser.open_new(a_website)
#            ampl_graph.graph_resource()
#            # ampl_graph.graph_cost()
#            # ampl_graph.graph_gwp_per_sector()
#            # ampl_graph.graph_cost_inv_phase_tech()
#            # ampl_graph.graph_cost_return()
#            # ampl_graph.graph_cost_op_phase()
#        
#            
#            # ampl_graph.graph_layer()
#            # ampl_graph.graph_gwp()
#            # ampl_graph.graph_tech_cap()
#            # ampl_graph.graph_total_cost_per_year()
#            # ampl_graph.graph_load_factor()
#            # df_unused = ampl_graph.graph_load_factor_2()
#            # ampl_graph.graph_new_old_decom()
        if graph_comp:
            ampl_graph = AmplGraph(output_file, ampl_0,case_study)
            
            case_study_1 = '{}_{}_{}_gwp_limit_all_the_way'.format('TD',30,0)
            output_folder_1 = os.path.join(pth_output_all,case_study_1)
            output_file_1 = os.path.join(output_folder_1,'_Results.pkl')
            
            case_study_2 = '{}_{}_{}_gwp_limit_all_the_way'.format('TD',10,5)
            output_folder_2 = os.path.join(pth_output_all,case_study_2)
            output_file_2 = os.path.join(output_folder_2,'_Results.pkl')
            
            
            output_files = [output_file_1,output_file_2]
            
            # ampl_graph.graph_comparison(output_files,'C_inv_phase_tech')
            ampl_graph.graph_comparison(output_files,'C_op_phase')
            # ampl_graph.graph_comparison(output_files,'Tech_cap')
            

            
        ###############################################################################
        ''' main script ends here '''
        ###############################################################################
        
