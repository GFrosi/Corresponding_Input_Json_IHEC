import pandas as pd
import sys
import os
import csv


def read_csv(file_name):
    '''receives a file name 
    separated by comma and return a df'''

    df = pd.read_csv(file_name)

    return df


def get_gsm(df_no_diff):
    '''receives a df, removes the NA rows using 
    the Corresponding input column and return a list 
    of GSM without duplicates generated from the column 
    cited before
    '''

    df_no_NA = df_no_diff[df_no_diff['Corresponding_Input'].notnull()] #3622 (removing input samples - have no cctrl)
    list_gsm = df_no_NA['Corresponding_Input'].tolist()
    list_gsm_split = [ele.strip().split(',') for ele in list_gsm]
    flat_list = [result  for l in list_gsm_split for result in l]
    final_list = list(set(flat_list))
    
    return final_list #1478


def create_dict_gse(final_list, df_complete): #to work to create a list of gsm (ele) as value
    '''receives a list and a complete df 
    (including all histones samples) with 
    GSM and GSE columns. Returns a dict
    where the keys are the GSE and the values
    are a list of GSM from that GSE
    '''

    dict_gse = {}

    for ele in final_list:
        for i, row in df_complete.iterrows():
            if ele in row['GSM']:
                # print(ele)
                if row['GSE'] not in dict_gse.keys():
                    dict_gse[row['GSE']] = [ele]
                
                else:
                    dict_gse[row['GSE']].append(ele)

                # print(dict_gse)
    return dict_gse


def check_dir_gse(dict_gse):
    '''receives a dict and generates 
    a dir if the key is not a directory 
    in the current path
    '''

    list_dir = next(os.walk('.'))[1] #get dir names

    for key in dict_gse.keys():
        if key not in list_dir:
            os.mkdir(os.path.join(os.getcwd(),key))


def write_dict(dict_gse): 
    '''receives a dict and save it in a csv file'''

    with open('dict_srr_cctrl.csv', 'w') as csv_file:  
        writer = csv.writer(csv_file)
        
        for key, value in dict_gse.items():
            writer.writerow([key, value])



def create_srr_file(final_list, df_complete):
    '''receives a list and complete df, and returns
    txt files with the SRR for each GSE related with 
    the corresponding controls
     '''

    for ele in final_list: #maybe add tqdm here to have a notion #ele is a gsm
        for i, row in df_complete.iterrows():
            if ele in row['GSM']:       
                out_name = row['GSE']+'_srr_cctrl'+'.txt'
                path_out = os.path.join(os.getcwd(), row['GSE'], out_name) #each GSE_SRR_cctrl file to their correspondent dir
                list_dir_files = os.listdir(os.path.join(os.getcwd(),row['GSE']))
                
                if out_name not in list_dir_files:
                    output = open(path_out, 'a')
                    srr_list = row['SRR'].split(',')
                    to_write = '\n'.join(srr_list) + "\n"  
                    output.write(to_write)
                    
                    break
        
                
                else:      
                    output = open(path_out, "a")
                    srr_list = row['SRR'].split(',')
                    to_write = '\n'.join(srr_list) + '\n'   
                    output.write(to_write)
        
        output.close()
            
            

def main():

    df_no_diff = read_csv(sys.argv[1])
    df_complete = read_csv(sys.argv[2])
    final_list = get_gsm(df_no_diff)
    dict_gse = create_dict_gse(final_list,df_complete)
    # write_dict(dict_gse)
    check_dir_gse(dict_gse)
    create_srr_file(final_list, df_complete)



if __name__ == "__main__":


    main()
