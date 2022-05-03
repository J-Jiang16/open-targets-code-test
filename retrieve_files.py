# Import Python built-in Module
from os import makedirs

def retrieve_files(ftp_server, datatype):
    ftp_server.cwd("/pub/databases/opentargets/platform/21.11/output/etl/json/" + datatype)

    # Get list of files
    ftp_server.dir() 

    # List all ftp files in the server directory
    filenames = ftp_server.nlst()

    # Dreate a folder or sub-directory in the working directory
    makedirs(datatype)

    # Download all files in current directory in binary mode
    for filename in filenames:
        with open(datatype + filename, "wb") as file:
            # Command for Downloading the file 
            ftp_server.retrbinary('RETR ' + filename, file.write)
            file.close()
