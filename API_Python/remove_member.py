#!/usr/bin/python3
'''
Description: This program is used to remove the specified member from all the project through API Python.
Usage:
     python3 remove_member.py \
            -t file  your authentication token file.\
            -f file  the member file, which you want to remove from all the project.\
            -o output_file all_project_member.txt.\
'''

import sys, os, getopt
if(len(sys.argv) < 3):  
        print ("Usage: python3",sys.argv[0]," -t token_file -f member_file -o all_project_member.txt")  
        exit(1)
opts, args = getopt.getopt(sys.argv[1:], "t:f:o:") 
token_file="" 
member_file=""
output_file=""
for op, value in opts: 
  if op == "-t": 
    token_file = value 
  elif op == "-f": 
    member_file = value 
  elif op == "-o": 
    output_file = value
    
import sevenbridges as sbg
f = open(token_file) 
info = f.readline().strip('\n')
f.close()

dict = {}
for line in open(member_file): 
     if line == '':
         break
     index = line.find('\n')
     key = line[:index]  
     dict[key] = 1

api = sbg.Api(url='https://cavatica-api.sbgenomics.com/v2', token=info)
filewriter = open(output_file,'w')
for project in api.projects.query().all():
    for member in project.get_members().all():
      #filewriter.write(project.id,project.name,member.id)
       print('\t'.join([project.id,project.name,member.id]), file=filewriter)   
       #if dict.has_key(member.id):  #python2
       if member.id in dict.keys():
          project.remove_member(user=member.id)
