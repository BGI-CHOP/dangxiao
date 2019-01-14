import argparse
import os
import requests
from collections import defaultdict
#new_dict = defaultdict(dict)

parser = argparse.ArgumentParser()
parser.add_argument("-sid", required=True)
args = parser.parse_args()

base = 'https://kf-api-dataservice.kidsfirstdrc.org/'
sam_id = args.sid     
sd_link = base + 'families?study_id=' + sam_id

file = open(sam_id + ".ped", 'w')
print("#Family_ID\tIndividual_ID\tPaternal_ID\tMaternal_ID\tSex\tPhenotype",file=file)

while sd_link:
  response = requests.get(sd_link).json()
  results = response['results']
  for result in results:
    fam_id=result['kf_id']
    print (fam_id)
    pt=base + result['_links']['participants']
    res=requests.get(pt).json()['results'][0]
    fam_re=base + res['_links']['family_relationships']
    fam_re_re=requests.get(fam_re).json()['results']
    new_dict = defaultdict(dict)
    for re in fam_re_re:
      p1=requests.get(base + re['_links']['participant1']).json()
      p2=requests.get(base + re['_links']['participant2']).json()
      p1_bs=p2_bs=''
      if requests.get(base + p1['_links']['biospecimens']).json()['results']:
        for F in (requests.get(base + p1['_links']['biospecimens']).json())['results']:
                if "Normal" in F['source_text_tissue_type']:
                  p1_bs=F['kf_id']
      if requests.get(base + p2['_links']['biospecimens']).json()['results']:
        for M in (requests.get(base + p2['_links']['biospecimens']).json())['results']:
                if "Normal" in M['source_text_tissue_type']:
                  p2_bs=M['kf_id']
      p1_dig=requests.get(base + p1['_links']['diagnoses']).json()
      p2_dig=requests.get(base + p2['_links']['diagnoses']).json()
      if p1_bs:
        if p1_dig['results'] and p1_dig['results'][0]['source_text_diagnosis']:
          new_dict[p1_bs]['phe']=2
   #     elif p1['results']['affected_status'] is not None:
   #       new_dict[p1_bs]['phe']=1
        else:
          new_dict[p1_bs]['phe']=1

        if "Male" in p1['results']['gender']:
          new_dict[p1_bs]['sex']=1
        elif "Female" in p1['results']['gender']:
          new_dict[p1_bs]['sex']=2
        else:
          new_dict[p1_bs]['sex']=0
      if p2_bs:
        if p2_dig['results'] and p2_dig['results'][0]['source_text_diagnosis']:
          new_dict[p2_bs]['phe']=2
   #     elif p2['results']['affected_status'] is not None:
   #       new_dict[p2_bs]['phe']=1
        else:
          new_dict[p2_bs]['phe']=1

        if "Male" in p2['results']['gender']:
          new_dict[p2_bs]['sex']=1
        elif "Female" in p2['results']['gender']:
          new_dict[p2_bs]['sex']=2
        else:
          new_dict[p2_bs]['sex']=0
      if p1_bs and p2_bs:
        if "Father" in re['participant1_to_participant2_relation']:
          new_dict[p2_bs]['F']=p1_bs
          new_dict[p1_bs]['sex']=1
        elif "Mother" in re['participant1_to_participant2_relation']:
          new_dict[p2_bs]['M']=p1_bs
          new_dict[p1_bs]['sex']=2
    for key,value in new_dict.items():
      if 'F' not in value.keys():
        new_dict[key]['F']=0
      if 'M' not in value.keys():
        new_dict[key]['M']=0
      print(fam_id,key,new_dict[key]['F'],new_dict[key]['M'],new_dict[key]['sex'],new_dict[key]['phe'],sep='\t',file=file)
  try:
    sd_link = base + response['_links']['next']
  except:
    break
