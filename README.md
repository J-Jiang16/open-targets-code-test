# EBI-open-targets-code-test

This work is the coding sample for open targets coding test.
EBIsample is the main code, while make_list and retrieve_files are custom written functions.
Third-party libraries that need to be installed include pandas, and numpy.

The code first extracts all files from FTP server to local directories, then converts JSON files to pandas dataframes and carries out analysis, then outputs the resultant table to another JSON file.

This work does not yet run fully without bugs, so that output is not provided yet. However, the functionalities are full, with detailed explanations of every step in the code. Although the main code is single-thread only, consideration has been given to creating multi-threading and consumer-producer pattern to increase speed and make use of all available CPUs, the skeleton for this code is provided in the branch-with-multithreading. However, this branch is still very rough.


**Thought process behind algorithm:**

1.Batch download dataset, save and extract in JSON format - JSON Python module
	
2. Data manipulation in table format
	  Observation: file length: evidence (200x5500)> diseases(15x1500) > targets (200x300)
	  Open and iterate over each file only once, extract all relevant information then close - saves time
	  Only store useful information in variables and overwrite & delete variables over time- saves runtime memory
	  Use nested list for multiple scores - saves runtime memory and output memory
		Not creating a table of all evidence, but collapse evidence with same target-disease pair into a single row with a field containing a dictionary of ID-score pairs.
	  Take advantage of all available CPUs - multithreading in Python 
		When the time spending on I/O significantly more than the time spending on computation, it is helpful to use multithreading - this is our case where large number of input files need to be extracted from the server.
		
    Data Flow:
		Open each file in evidence, add to dataframes of ( diseaseID, targetID, {list of scores,…}), close. - use multithread, no queue
		Merge above dataframes into one 
		Open each file in target, append target.approvedSymbol to each new dataframe, close - multithread, producer-consumer queue
		Open each file in disease, append disease.name to each new dataframe, close - multithread, producer-consumer queue
		Add new fields to the list and delete {list of scores,…} field, to form: (diseaseID, targetID, disease.name, target.approvedSymbol, median score, three greatest scores, pair rank) 
		Calculate median score, three greatest scores, enter values, and sort pair rank based on median score of target-disease pairs
    
**    Final Task:**
		Count how many target-target pairs share a connection to at least two diseases.
		Sort final table obtained from main code (final_sorted_df) according to diseaseId. For each unique diseaseId, enumerate all coresponding target-target 			pairs, which is easily done in pandas. Output the pair list to a new dataframe. Loop over all diseaseId. In the new dataframe, rank target pairs 		 according to frequency. And highlight those with a frequency >=2.

		
	
