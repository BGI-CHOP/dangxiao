"""Linter for CWL v1.0"""

import argparse
import sys
import os
#import yaml
import ruamel.yaml as yaml

parser = argparse.ArgumentParser()
parser.add_argument("-cwl", required=True,help="CWL CommandLineTool or Workflow")
args = parser.parse_args()

#check running the CWL file
a=os.popen("cwltool " + args.cwl + "> filename 2>&1;grep 'usage:' filename").read()
if a:
  print ("\nRun CWL file ok")
else:
  print ("\nERROR: Fail to run the CWL file, please check!")

# load input cwl file as json object in order and check YAML format and cwlVersion
file_input_yaml = args.cwl
try:
  with open(file_input_yaml, 'r') as f:
    file_input = yaml.load(f,Loader=yaml.RoundTripLoader)
except ValueError:
            sys.exit("invalid YAML file")

if 'cwlVersion' not in file_input.keys():
    print ("\nERROR: CWL file does not contain the field: 'cwlVersion'")
if file_input['cwlVersion'] != 'v1.0':
    print ("\nWARNING: please CHECK CWL version is not v1.0")
if file_input['class'] not in ["CommandLineTool", "Workflow", "ExpressionTool"]:
    print ("\nWARNING: please CHECK CWL class is not CommandLineTool or Workflow or ExpressionTool")

# check the required order and Fields 
order = ('cwlVersion', 'class', 'id', 'requirements', 'baseCommand', 'arguments', 'inputs', 'outputs', 'expression', 'steps');
list=[order.index(key) for key in file_input if key in order]
li=[order[k] for k in sorted(list)]
if sorted(list) != list :
  print ("\nWARNING: your class is: ",file_input['class'],"\nThe recommended order:\n","\n".join(li),sep="")

# check the format
#inputs  outputs
#bam:
#   type: File           bam:File
for i in ['inputs', 'outputs']:
    for j in file_input[i]:
        z=file_input[i][j]
        if isinstance(z,dict) and len(z)==1:
            print ("\nWARNING: plese check your format:\nThe field:",i,"\nYour format:",j,"\t",z,"\nRecommended format:eg: input_file:File")

# check the steps order for Workflow
step = ('run', 'in', 'scatter', 'out')
if file_input['class'] == 'Workflow':
    if '$namespaces' not in file_input.keys():
        print ("\nWARNING: you need to add the following field in the end of your cwl file:\n$namespaces:\n  sbg: https://sevenbridges.com")
    if 'steps' in file_input:
        for i in file_input['steps']:
            list=[step.index(j) for j in file_input['steps'][i] if j in step]
            li=[step[k] for k in sorted(list)]
            if sorted(list) != list :
              print ("\nWARNING: your steps for: ",i,"\nThe recommended steps order:\n","\n".join(li),sep="")
    else:
        print ("\nERROR: CWL Workflow does not contain the field: 'steps'")  
#def error(message): 
#    print("ERROR:", message)
#def warn(message):
#   print("WARNING:", message)


# with open(ff, 'w') as g:
#    print(yaml.dump(file_input, Dumper=yaml.RoundTripDumper), file=g)
