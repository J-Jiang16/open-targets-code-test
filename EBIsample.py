# Import Python built-in Modules
from ftplib import FTP
import pandas as pd
from threading import Thread
import _thread
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import os

# Import custom functions
from retrieve_files import *

#===========================================================================
# Initialization parameter configuration
#===========================================================================

# To download files, set True; If files already exist locally, set False
download = False

#global variables
#length for setting consumer termination condition
max_length = 0

#===========================================================================
# Download relevant files from FTP server to the working directory
#===========================================================================

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

#===========================================================================
# Load relevant information from JSON files to dataframe
#===========================================================================

 


thread_number=20

df = pd.DataFrame()

dirloc = './evidence/sourceId=eva/'

# Define a function for the thread
def create_table_single_file(filename):
    
    # Opening JSON file
    # Make sure not reading _SUCCESS file
    if not filename == '_SUCCESS':  
        f = open(dirloc + filename, 'r')
       
    # returns one dataframe with desired columns
    df_temp = pd.read_json(f, lines = True)
    f.close()
    return df_temp[['diseaseId','targetId','score']]

def create_tables(filenames, m):
    df_new=pd.DataFrame()
    for t in range(m):
        df_new = pd.concat([df_new, create_table_single_file(filenames[t])])
    print(df_new)
    return df_new

# Create one thread for each single file

    #Iterate over files to open and build sub-dataframes of the main dataframe df
obj = os.scandir(dirloc)
k=0
entry_list = []
for entry in obj:
    k+=1
#reset iterator
obj = os.scandir(dirloc)
try:
    for q in range(thread_number):
        p=0
        for entry in obj:
            p+=1
            if p >= k // thread_number * q and p < min( k // thread_number * (q + 1), k ):
                entry_list.append(entry.name)          
        df[q] = _thread.start_new_thread(create_tables, (entry_list, p,) )
except:
    print('Error: Unable to open file or start thread')

print(df)

obj.close()








queue = Queue()


def consume(max_length):

    while not event.is_set() or not queue.empty():
        try:
            i = queue.get()
            
            # writing into variables
        except:
            print ("Error: Unable to get queueing element.")
            return
        print(i)



consumer = Thread(target=consume)
consumer.start()


def produce(i):

    queue.put(i)

event = threading.Event()

with ThreadPoolExecutor(max_workers=10) as executor:
    try:
        for i in range(100):
            executor.submit(produce, i)
        # Stops executors
        executor.shutdown(wait=False)


    except:
        print("Error: executor not working.")

consumer.join()
