import pandas as pd
import sys
import os


def get_gse(df):
    '''receives a df with a column GSE
    and return a list of gse without duplicated terms'''

    gse_list = list(set(df['GSE'].tolist()))

    with open('gse_IDs.txt', 'w') as output:
        gse_write = '\n'.join(map(str, gse_list))
        output.write(gse_write)
        output.close()
    
    return gse_list


def create_dir(gse_list):
    '''receives a list of gse 
    and creates a directory using
    the gse ID'''

    for gse in gse_list:
        gse = gse.strip()
        os.mkdir(os.path.join(os.getcwd(),gse))


def get_srr(df, gse_list):
    '''receives a list of gse and a df 
    including the GSE and SRR columns. 
    Generates txt files with a list of 
    SRR per gse. Each file is saved in 
    their respective directories'''

    for gse in gse_list:
        out_name = gse+'_srr'+'.txt'
        print(gse)

        df_gse = df[df['GSE'].str.contains(gse)]
        srr_list = df_gse['SRR'].tolist()
        srr_list_split = [ele.split(',') for ele in srr_list] #ok, list of lists
        path_out = os.path.join(os.getcwd(), gse, out_name) #each GSE_SRR file to their correspondent dir
        output = open(path_out, 'w') 

        for l in srr_list_split:
            to_write = '\n'.join(l)+'\n'
            output.write(to_write)

        output.close()
 

def main():

    df_gse = pd.read_csv(sys.argv[1]) #df with GSE and SRR columns
    df = df_gse[df_gse['GSE'].notna()]
    gse_list = get_gse(df) 
    create_dir(gse_list)
    get_srr(df, gse_list)
    
    
if __name__ == "__main__":



    main()
