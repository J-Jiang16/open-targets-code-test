# Import Python built-in Modules
from ftplib import FTP
import pandas as pd
import numpy as np
import os

# Import custom functions
from retrieve_files import *

#===============================================================================================================
# Initialization parameter configuration
#==============================================================================================================

# To download files, set True; If files already exist locally, set False
download = False

#================================================================================================================
# Download relevant files from FTP server to the working directory
#=================================================================================================================

# Fill Required Information
HOSTNAME = 'ftp.ebi.ac.uk'
USERNAME = 'anonymous'
PASSWORD = ''

# Connect FTP Server
try:
    ftp_server = FTP(HOSTNAME, USERNAME,PASSWORD)
except:
    print("Error: Unable to connect to FTP server.")
 
# Force UTF-8 encoding
ftp_server.encoding = "utf-8"

# Retrieve all relevant files
if download:
    retrieve_files(ftp_server,'targets/')
    retrieve_files(ftp_server,'diseases/')
    retrieve_files(ftp_server,'evidence/sourceId=eva/')

# Close the Connection
ftp_server.quit()

#==============================================================================================================
# Load relevant information from JSON files to dataframe
#==============================================================================================================


#======================================   evidence   ==========================================================
# Open evidence files
df = pd.DataFrame()

dirloc = './evidence/sourceId=eva/'


#Iterate over files to open and build sub-dataframes of the main dataframe df
obj = os.scandir(dirloc)
for entry in obj:
    if not entry.name == '_SUCCESS':  
        f = open(dirloc + entry.name, 'r')
       
    # returns one dataframe with desired columns
    df_temp = pd.read_json(f, lines = True)
    f.close()
    df = pd.concat([df, df_temp[['diseaseId','targetId','score']]])
    
obj.close()


#Group data by target-disease pairs, removing redundant evidence data
df_new = df.groupby(['diseaseId','targetId']).aggregate(make_lists).reset_index()


# Calculate three max scores, median score, and add to new columns

df_new['max 3 scores'] = 0
df_new['median'] = 0

for row in range(df_new.shape[0]):
    print(row)
    #sorted scores array
    sorted_scores = np.sort(np.array(df_new.iloc[row,2]))
    print(sorted_scores)
    #Calculate three max scores
    if len(sorted_scores) < 3:
        df_new.iloc[row,3] = sorted_scores.tolist()
    else:
        df_new.iloc[row,3] = (sorted_scores[-3:]).tolist()
     #Calculate median score   
    print( df_new.iloc[row,3])
    df_new.iloc[row,4] = np.median(np.array(df_new.iloc[row,2]))

print (df_new)

#============================================  diseases  =========================================================

# Open diseases files
dirloc = './diseases/'
# reset df
df = pd.DataFrame()

#Iterate over files to open and build sub-dataframes of the main dataframe df
obj = os.scandir(dirloc)
for entry in obj:
    if not entry.name == '_SUCCESS':  
        f = open(dirloc + entry.name, 'r')
       
    # returns one dataframe with desired columns
    df_temp = pd.read_json(f, lines = True)
    f.close()
    df = pd.concat([df, df_temp[['Id','name']]])
    
obj.close()

# Stores diseases Id and name information in this dataframe
df_diseases_new = df.drop_duplicates()

#========================================  targets  ===================================================================

# Open targets files
dirloc = './targets/'
# reset df
df = pd.DataFrame()

#Iterate over files to open and build sub-dataframes of the main dataframe df
obj = os.scandir(dirloc)
for entry in obj:
    if not entry.name == '_SUCCESS':  
        f = open(dirloc + entry.name, 'r')
       
    # returns one dataframe with desired columns
    df_temp = pd.read_json(f, lines = True)
    f.close()
    df = pd.concat([df, df_temp[['Id','approvedSymbol']]])
    
obj.close()

# Stores targets Id and approvedSymbol information in this dataframe
df_targets_new = df.drop_duplicates()

#======================== merge disease name and target approved symbol columns with main table==========================

# Use left join to join disease and target dataframes to the main dataframe. (left join: keep main intact)
df_merged1 = pd.merge(df_new, df_diseases_new, on='Key', how='left')
df_merged2 = pd.merge(df_merged1, df_targets_new, on='Key', how='left')

#Rank according to median score 
final_sorted_df = df_merged2.sort_values(by='median', ascending=False).reset_index()

print(final_sorted_df)
# At this point should return a table with columns: diseaseID, targetID, max 3 scores, median, disease name, 
# and target approvedSymbol, sorted in descending order of the median score.

#========================================================================================================================
#Output to JSON file
#========================================================================================================================
       
final_sorted_df.to_json('output.json')
