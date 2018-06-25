import argparse
import os
import requests
from collections import defaultdict
new_dict = defaultdict(dict)

parser = argparse.ArgumentParser()
parser.add_argument("-fid", required=True)
args = parser.parse_args()

base = 'http://localhost:1080/'
fam_id = args.fid     
sd_link = base + 'participants?family_id=' + fam_id

response = requests.get(sd_link).json()
results = response['results']
for result in results:
  biospecimens=(requests.get(base + result['_links']['biospecimens']).json())['results'][0]['kf_id']
  new_dict[result['kf_id']]['FID']=fam_id
  new_dict[result['kf_id']]['ID']=biospecimens
  relation=(requests.get(base + result['_links']['family_relationships']).json())['results']
  if relation:
    if relation[0]['participant_to_relative_relation'] == 'Father':
      new_dict[os.path.basename(relation[0]['_links']['relative'])]['Father']=biospecimens
    elif relation[0]['participant_to_relative_relation'] == 'Mother':
      new_dict[os.path.basename(relation[0]['_links']['relative'])]['Mother']=biospecimens
  if result['gender'] == 'Male':
    new_dict[result['kf_id']]['sex']=1
  elif result['gender'] == 'Female':
    new_dict[result['kf_id']]['sex']=2
  else:
    new_dict[result['kf_id']]['sex']=0
  phe=(requests.get(base + result['_links']['phenotypes']).json())['results'][0]['observed']
  if phe == 'Negative':
    new_dict[result['kf_id']]['phe']=1
  elif phe == 'Positive':
    new_dict[result['kf_id']]['phe']=2
  else:
    new_dict[result['kf_id']]['phe']=0

file = open(fam_id + ".fam", 'w')
for key,value in new_dict.items():
    if 'Father' not in value.keys():
        new_dict[key]['Father']=0
    if 'Mother' not in value.keys():
        new_dict[key]['Mother']=0
    print(new_dict[key]['FID'],new_dict[key]['ID'],new_dict[key]['Father'],new_dict[key]['Mother'],new_dict[key]['sex'],new_dict[key]['phe'],sep='\t',file=file)
