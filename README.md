# Introduction
This code uses the database of Securities and Exchange Commission's Electronic Data Gathering, Analysis and Retrieval (EDGAR) system to provide information about how users access EDGAR, including the first and last request time, the session duration, and the number of documents accessed in that session. 

# Programming Language
The code is written in Python 3. It requires sys and datetime libraries.

# Run Instructions
From the main folder, run 'run.sh' to execute the code. From a command prompt you can also type 'python ./src/Track_EDGAR.py ./input/log.csv ./input/inactivity_period.txt ./output/sessionization.txt', providing the directory path of the code and 3 arguments (2 input files and an output file). You can also run the code without these arguments and default values will be used.

# Inputs
The code requires 2 input files, a data log named 'log.csv' in a folder called 'input' and an input file named 'inactivity_period.txt' in the same folder.
The log file should be a comma separated line in the same format as the data log from EDGAR system, with the first line being a header and all future lines each being a web request. 
The inactivity period file should include a single integer in the range of 1 and 86,400 which represents the number of seconds to wait before closing a session for inactivity. If the value in this file is out of range, or not an integer, the program will exit with an error. 

# Output
The program generates an output file called 'sessionization.txt' which lists the web request information with one line per user session. Each line has the following fields separated by commas:
* IP address of the user exactly as found in `log.csv`
* date and time of the first webpage request in the session (yyyy-mm-dd hh:mm:ss)
* date and time of the last webpage request in the session (yyyy-mm-dd hh:mm:ss)
* duration of the session in seconds
* count of webpage requests during the session

Example output: 101.81.133.jja,2017-06-30 00:00:00,2017-06-30 00:00:00,1,1

The web requests are in chronological order based on when the session ended. The web requests that ended at the same time are listed in the same order as the user's first request for that session appeared in the input file.

# Assumptions
* Web requests in the log file are in chronological order.
* The session duration is inclusive and the minimum duration of a session is 1.
* All sessions end at the end of the file.
* Every time a user accesses a document, that request is counted, even if the user is requesting the same document multiple times, including when multiple requests come in the same second.  
* If the time of the request is not in the correct format, the entire request is skipped.
* The lines in the data file follow the same order as the file's header.
* Since all records accessed are counted (including duplicates) and the record info (cik, accession, and extention) is not recorded, there is no need to store these values for each web request.

# Approach
objective: The code processes the input file "log.csv" to determine the active sessions (based on the inactivity period defined in the "inactivity_period.txt") and records the IP address, beginning and end time of the session, duration of the session, and the number of documents accessed in the output file "sessionization.txt" according to the format mentioned above. 

First the input and output files are opened (either provided as an argument when running the code or using the default directories). Particular care is taken to handle errors with the inactivity period input file, as this is a likely source of error if the file does not exist, is empty, or does not contain a  single positive integer.

The first line of the data log is a header, which is parsed to determine the index of the key input values 'ip', 'date', 'time' in future lines.  Since even duplicate document requests by the same IP are being counted separately, there is no need to consider the three parameters that identify the document. After parsing the header, the data log is read line by line, pulling the 'ip', 'date', and 'time' fields.

The active sessions are recorded in a dictionary with their 'ip' as the key. Each IP is then composed of a dictionary with values tracking the beginning of a session (the first datetime that the IP requested a document), the last active time (the last time that the IP requested a document), the count of the number of files that have been requested by the IP in the session, the current duration of the IP's session (last request time - first request time + 1 in seconds), and an integer 'obs' which keeps track of the order of web requests. 'obs' is used to order the sessions chronologically when multiple sessions end at the same time. A dictionary was used because it can contain many different types of data structures, can be searched for the 'key' much faster than a large list, and scales better than objects like a Pandas 'DataFrame'. 

There are 2 functions in the code:
1. The "CreateLine" function takes the values recorded in the dictionary and turns them into a properly formatted line message to be added to the output file. Calling this function avoids writing out the line format more than once and makes it easier to change the output format in the future.
2. The "WriteToFile" function takes the list of inactive records generated when the dictionary is checked, and sorts that list by "obs", then write the messages line by line into the output file. It was necessary to have this extra list because the dictionary does not keep the order and all sessions that ended at the same time needed to be recorded in the chronological order based on when they were first read from the input file. 

To calculate the duration of a session and compare the time passed between input lines, the 'date' and 'time' fields are combined and parsed into a datetime object. If the date or time was in an improper format, that line of data is skipped.

As each line is read from the log file, if the IP does not match one of the active session IPs, that line is parsed and added to the active session dictionary. If it does match one of the active sessions, the data for that session is updated by increasing the count, updating the last activity time, and updating the duration.

Any time the log file time is different from the last recorded time, the active session dictionary is checked to determine if any of the IPs have been inactive for a time greater than the defined inactivity period. All IPs that surpass this period are parsed into a message line to be recorded in the output file (using "CreateLine" function). The message and the sessions' 'obs' number are added to a list which is used as the input of "WriteToFile" function. The inactive IP is deleted from the dictionary.

This processes of reading data log lines continues until the entire data log has been read. Throughout this process a single IP can have multiple sessions. Once an active session ends, the IP is removed from the dictionary, however, the same IP can be used to create a new entry in the dictionary, in case of future web requests.

Once the data log has been completely read (end of the input file), all remaining active sessions are considered to have ended and are added to the output file by formatting message lines (using "CreateLine" function), appending them along with 'obs' to a list and then calling "WriteToFile" function to order the messages and write them to the output file. 

#Future Effort
The eventual goal for this code is to act as a pipeline taking data logs in real time from the SEC's logs of access to the EDGAR database and tracking active sessions and passing them to some GUI which displays this info. Hundreds of thousand requests are coming in a second to the EDGAR database, so it is important to keep the code as lean and fast as possible. Therefore, some more effort should be made to optimize the speed and avoid unnecessary calculations. Once real time access is available the code will likely need to be modified to be multi-threading and to have event handlers which handle when a new log line is available for adding to the dictionary, but this would require some effort to make sure each thread is addressing the same dictionary and that the output log is still written in chronological order. 
