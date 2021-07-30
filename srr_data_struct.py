import pandas as pd
import sys
import argparse
import json
import os


def data_parse(file_n):

    '''receives a table and returns two dicts. The first one has the SRR related with each IP samples as keys and 
    a list of GSM of corresponding controls. The second ones has the GSM of each Input sample as keys and a list of their
    SRR as values.'''
    
    file_hist = open(file_n, 'r')

    dict_srr_IP = {}
    
    dict_gsm_srr_ctrl = {}
    
    for i,line in enumerate(file_hist):

        
        if i == 0: #removing the header line
        
            continue
        
        
        line = line.strip()

        splited_table = line.split('\t')[1:] #removing index column; file separated by TAB
        
        splited_table[-2] = splited_table[-2].replace('"', '') #replacing "" by nothing; Corresponding Control column

        splited_table[-4] = splited_table[-4].replace('"', '') #SRR column

        
        if splited_table[-2] != 'NA': #removing inputs
            
            srr_ip = splited_table[-4].split(',')[0] #geeting just the first SRR (in this case, the first technical replicate to filter json)
            
            gsm_ctrl = splited_table[-2].split(',')

            dict_srr_IP[srr_ip] = gsm_ctrl

        else:

            srr_ctl = splited_table[-4].split(',')[0]
            
            dict_gsm_srr_ctrl[splited_table[7]] = srr_ctl #getting each GSM cctrl from GSM column (individualy)

            
    file_hist.close()
    
    return dict_srr_IP, dict_gsm_srr_ctrl



def build_dict(dict_srr_IP, dict_gsm_srr_ctrl):

    '''Receives two dicts and returns a final dict where the keys are the SRR of each IP samples, and the value
    is a list of SRR of their corresponding controls'''

    final_dict = {}

    for k,v in dict_srr_IP.items():
        for val in v:
    
            if k not in final_dict.keys():
                final_dict[k] = [dict_gsm_srr_ctrl[val]] #SRR from IP as key and SRR from GSEM cctrl as value
            
            else: 
                final_dict[k].append(dict_gsm_srr_ctrl[val])


    return final_dict


def open_json(file_n):

    '''load the json file'''

    with open(file_n) as f:
        
        json_full = json.load(f)
        
        return json_full
       

def create_json_struc(final_dict, list_json_stand, list_ip_ssr, list_ctrl_srr):

    '''receives a dict and three lists. Returns a list of list of tuples with the IP sample from the json file and 
    the correspondent inputs'''

    general_list = []

    for ip in list_ip_ssr:
        partial_list = list_json_stand.copy()
        partial_list.append(ip)

        for ip_path in ip[1]:
            srr_ip = os.path.basename(ip_path).split('_')[0]
            srr_ctl = final_dict[srr_ip]
             
            for ctrl in list_ctrl_srr:
                for ctrl_path in ctrl[1]:
                    
                    if  os.path.basename(ctrl_path).split('_')[0] in srr_ctl:
                        partial_list.append(ctrl)
        
        general_list.append(partial_list)
    
    return general_list


def play_json(json_full, final_dict):

    '''Receives a json and a dict. It generates three lists of tuples. One list with stand keys and values from the json file. 
    The second one with the IP samples information (key and values), and the third one with the control information'''

    list_json_stand = []
    list_ip_ssr = []
    list_ctrl_srr = []

    list_keys_stand = ['chip.always_use_pooled_ctl','chip.genome_tsv',
    'chip.paired_end','chip.ctl_paired_end','chip.pipeline_type',
    'chip.aligner','chip.title','chip.description']

    for k,v in json_full.items():  
        
        if k in list_keys_stand:
            list_json_stand.append((k,v))

        if 'chip.fastqs' in k:
            list_ip_ssr.append((k,v))

        if 'chip.ctl_fastqs' in k:
            list_ctrl_srr.append((k,v))

    return create_json_struc(final_dict, list_json_stand, list_ip_ssr, list_ctrl_srr)   


def write_json(general_list):

    ctn = 0
    
    for sublist in general_list:

        ctn+=1

        json_name = 'json_'+ str(ctn) + '.json'

        output = open(json_name, 'w')

        to_write = '{\n'

        for tup in sublist:


            if isinstance(tup[1], bool):
            
                to_write += "'" + tup[0] + "'" + ':' + str(tup[1]) + ',\n'

            elif isinstance(tup[1], list):
            
                to_write += "'" + tup[0] + "'" + ':' + str(tup[1]) + ',\n'
            
            else:

                to_write += "'" + tup[0] + "'" + ':' + "'" + tup[1] + "'" + ',\n'

        to_write += '}'
        to_write = to_write.replace(',\n}','\n}')
        
        
        output.write(to_write)

        output.close()

            

def main():

    file_n = args.table
    
    dict_srr_IP, dict_gsm_srr_ctrl = data_parse(file_n)
    
    final_dict = build_dict(dict_srr_IP,dict_gsm_srr_ctrl)

    json_full = open_json(args.json)

    general_list = play_json(json_full, final_dict)

    write_json(general_list)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(

        description="A tool to filter the json input for IHEC pipeline and return jsons for each IP sample with their respective corresponding controls"
    )

    parser.add_argument('-t', '--table', action="store",
    
                        help='The table generated by word_dist script (including corresponding control column). You should save a version separated by TAB',
                        required=True
                        
                        )

    parser.add_argument('-j', '--json', action="store",
    
                        help='The complete json file (all samples of each series) generated by chip-seq-json-generator script.',
                        required=True
                        
                        )

    args = parser.parse_args()

    main()