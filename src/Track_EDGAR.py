# -*- coding: utf-8 -*-
"""
Uses the database of Securities and Exchange Commission's Electronic Data Gathering, 
Analysis and Retrieval (EDGAR) system to provide information about how users 
access EDGAR, including the first and last request time, the session duration, 
and the number of documents accessed in that session. 

Created on Wed May 23 15:43:07 2018, last updated on Sat May 26, 2018
@author: Yasaman
"""
#import datetime library
import datetime as dt
#import sys library
import sys

#use paths provided in the run shell if enough arguments were passed
if len(sys.argv) > 3:
    input_path = sys.argv[1]
    period_path = sys.argv[2]
    output_path = sys.argv[3]
else:
    #default input, output, and inactivity period directories
    input_path = './input/log.csv'
    output_path = './output/sessionization.txt'
    period_path = './input/inactivity_period.txt'

#read the inactivity period from the text file
#if the format is wrong or the value is out of range, print an error message and exit 
try:
    f_period = open(period_path, 'r')
    period=int(f_period.read())
    f_period.close() 
except:
    print('Error: Unable to get inactivity period from: '+period_path+'\
          , the inactivity period should be an integer ranging from 1 to 86,400')
    sys.exit('exit program due to TypeError')
try:
    if period <= 0 or period > 86400:
        raise ValueError
except ValueError:
    print('Error: Unable to get inactivity period from: '+period_path+'\
          , the inactivity period should be an integer ranging from 1 to 86,400')
    sys.exit('exit program due to ValueError')
    
#open the output file
f_output = open(output_path,'w+')
    
def CreateLine(ip, DateTime0, DateTimen, dur, count):
    '''gets 'ip', 'DateTime0, 'DateTimen', 'dur', and 'count', 
    combines them in a string based on the required format for the output file, 
    and return the string'''
    line=str(ip)+','+str(DateTime0)+','+str(DateTimen)+','+str(dur)+','+str(count)+'\n'
    return line

def WriteToFile(lst):
    '''the function input is a list of records. each record has two components:
        (a) message (string format) that will be printed in the output file and
        (b) variable 'obs'. the function first sorts the lines based on the 
        first time read from the input file using 'obs', 
        then writes the messages to the output file.  '''
    lst.sort(key=lambda x: x[1])
    for i in lst:
        f_output.write(i[0])

#create a dictionary to hold the active sessions; the main key is the 'ip', 
#the keys in the nested dictionary are:
    #'DateTime0': the first time that the IP accessed a document
    #'DateTimen': the last time that the IP accessed a document
    #'count': number of documents that the IP accessed in a session
    #'dur': duration of an active session
dic_ips={}
#open the input file and read the header line to determine the location of 
#'ip', 'date', and 'time'
with open(input_path, 'r') as f_input:
    headers = next(f_input, None).split(',')
    #use all lowercase values to avoid issues if headers change
    headers = [i.lower() for i in headers] 
    idx_ip = headers.index('ip')
    idx_date = headers.index('date')
    idx_time = headers.index('time')

    #variable 'obs' keeps track of the order that the IPs were read from the input file
    obs=0
    #variables 'lastTime' keeps track of the time of the last line read
    lastTime = dt.datetime(1,1,1)
    #read from the input file line by line
    for num, line in enumerate(f_input, 2):
        errorFlag = False #reset the error flag for checking date and time format
        row=line.split(',')
        #combine date and time into a string and convert it to datetime type
        combTime=row[idx_date]+' '+row[idx_time]
        #check if the format of date and time is valid, 
        #if not print an error message and skip this line from the input file
        try:
            combTime=dt.datetime.strptime(combTime , '%Y-%m-%d %H:%M:%S')
        except:
            print('invalid time or date format, record line '+str(num)+ ' was removed')
            errorFlag = True
        if not errorFlag:
            #if time has increased, find the IPs that have been inactive
            #for more than the inactivity time, sort and print them in 
            #the output file, and delete the IP from the dictionary
            if combTime != lastTime:
                lst_obs=[]
                #iterate through the list of dictionary keys to be able to
                #delete items in the same loop
                for item in list(dic_ips.keys()):
                    if dt.timedelta.total_seconds(combTime-dic_ips[item]['DateTimen'])>period:
                        lst_obs.append([CreateLine(item, dic_ips[item]['DateTime0'],
                                       dic_ips[item]['DateTimen'], dic_ips[item]['dur'],
                                       dic_ips[item]['count']),dic_ips[item]['obs']])
                        del dic_ips[item]
                WriteToFile(lst_obs)    
                
            #if the IP read in this line is not in the dictionary, 
            #add it to the dictionary
            if str(row[idx_ip]) not in dic_ips.keys():
                dic_ips[row[idx_ip]]={'DateTime0': combTime, 
                        'DateTimen': combTime,  'count': 1, 'dur': 1, 'obs': obs+1}
                obs=obs+1
            #if the IP is in the dictionary, update 'DateTimen', 'count', and 'dur'
            else:
                dic_ips[row[idx_ip]]['DateTimen'] =combTime
                dic_ips[row[idx_ip]]['count'] += 1
                dic_ips[row[idx_ip]]['dur'] = int(dt.timedelta.total_seconds(
                        combTime - dic_ips[row[idx_ip]]['DateTime0'])+1)
                        #add 1 sec because the duration is inclusive
            #update 'lastTime' 
            lastTime = combTime

            
#at the end of the input file, sort and print out the IPs left in the dictionary
lst_obs=[]
for item in dic_ips:
    lst_obs.append([CreateLine(item, dic_ips[item]['DateTime0'],
                               dic_ips[item]['DateTimen'], dic_ips[item]['dur'],
                               dic_ips[item]['count']),dic_ips[item]['obs']]) 
WriteToFile(lst_obs)

#close the output file               
f_output.close()
