import argparse
import os
import requests
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("-sid", required=True)
args = parser.parse_args()

base = 'https://kf-api-dataservice.kidsfirstdrc.org/'
sam_id = args.sid     
sd_link = base + 'families?study_id=' + sam_id

file = open(sam_id + ".fam", 'w')
print("#Family_id\tFather_participant_id\tFather_biospecimen_id\tMother_participant_id\tMother_biospecimen_id\tChild_participant_id\tChild_biospecimen_id\tChild_tissue_type",file=file)
while sd_link:
  response = requests.get(sd_link).json()
  results = response['results']
  for result in results:
 #   fam_id=Fa_pt_id=Fa_bs_id=Ma_pt_id=Ma_bs_id=Pa_pt_id=Pa_bs_id="-";
    fam_id=result['kf_id']
    print (fam_id)
    pt=base + result['_links']['participants']
    res=requests.get(pt).json()['results'][0]
    fam_re=base + res['_links']['family_relationships']
    fam_re_re=requests.get(fam_re).json()['results']
    new_dict = defaultdict(dict)
    for re in fam_re_re:
      p1=requests.get(base + re['_links']['participant1']).json()
      p1_pt=os.path.basename(re['_links']['participant1'])
      p2=requests.get(base + re['_links']['participant2']).json()
      p2_pt=os.path.basename(re['_links']['participant2'])
      p1_bs=p2_bs=p2_type='-'
      if requests.get(base + p1['_links']['biospecimens']).json()['results']:
          if len(requests.get(base + p1['_links']['biospecimens']).json()['results'])==1:
             p1_bs=requests.get(base + p1['_links']['biospecimens']).json()['results'][0]['kf_id']
             p1_type=requests.get(base + p1['_links']['biospecimens']).json()['results'][0]['source_text_tissue_type']
          else:
             for F in (requests.get(base + p1['_links']['biospecimens']).json())['results']:
                if "Normal" in F['source_text_tissue_type']:
                  p1_bs=F['kf_id']
                  p1_type=F['source_text_tissue_type']
      if requests.get(base + p2['_links']['biospecimens']).json()['results']:
          if len(requests.get(base + p2['_links']['biospecimens']).json()['results'])==1:
             p2_bs=requests.get(base + p2['_links']['biospecimens']).json()['results'][0]['kf_id']
             p2_type=requests.get(base + p2['_links']['biospecimens']).json()['results'][0]['source_text_tissue_type']
          else:
             for M in (requests.get(base + p2['_links']['biospecimens']).json())['results']:
                if "Normal" in M['source_text_tissue_type']:
                  p2_bs=M['kf_id']
                  p2_type=M['source_text_tissue_type']
      new_dict[p2_pt]['bs']=p2_bs
      new_dict[p2_pt]['type']=p2_type
      if "Father" in re['participant1_to_participant2_relation']:
          new_dict[p2_pt]['F_pt']=p1_pt
          new_dict[p2_pt]['F_bs']=p1_bs
      if "Mother" in re['participant1_to_participant2_relation']:
          new_dict[p2_pt]['M_pt']=p1_pt
          new_dict[p2_pt]['M_bs']=p1_bs
    for key,value in new_dict.items():
      if 'F_pt' not in value.keys():
        new_dict[key]['F_pt']='-'
      if 'F_bs' not in value.keys():
        new_dict[key]['F_bs']='-'
      if 'M_pt' not in value.keys():
        new_dict[key]['M_pt']='-'
      if 'M_bs' not in value.keys():
        new_dict[key]['M_bs']='-'
      print(fam_id,new_dict[key]['F_pt'],new_dict[key]['F_bs'],new_dict[key]['M_pt'],new_dict[key]['M_bs'],key,new_dict[key]['bs'],new_dict[key]['type'],sep='\t',file=file)
  try:
    sd_link = base + response['_links']['next']
  except:
    break
