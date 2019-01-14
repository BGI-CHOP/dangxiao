import requests
import os
import sevenbridges as sbg
import argparse
import re
new_dict = {}

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--projectid", help = "Required. Cavatica project id. (Example: kids-first-drc/sd-bhjxbdqk-har)", type = str, required = True)
parser.add_argument("-f", "--projectfile", type = str, required = True)
args = parser.parse_args()

#base_url = 'https://cavatica-api.sbgenomics.com/v2/'
#api = sbg.Api(url = base_url, token = os.environ['cavatiac'])

c = sbg.Config(profile='cavatica')
api = sbg.Api(config=c)
project_id = args.projectid
project_file = args.projectfile
for line in open(project_file): 
    if line == '':
         break
    f = line.strip('\n').split('\t')[1]
    ff= line.strip('\n').split('\t')[0]
    file=api.files.query(project=project_id,names=[f])[0]
    print (file.name)

    biospecimens=experiment_strategy=platform=Library_ID=reference_genome=external_id=gender=race=ethnicity=external_sample_id=external_aliquot_id=sample_type=Primary_site=Age_at_diagnosis=Disease_type=participant=age_at_event_days=source_text_tumor_descriptor=composition=''
 #   file=api.files.get(f)
#    task=api.tasks.get(file.origin.task)
#    if (task.inputs['biospecimen_name']):
#        biospecimens=task.inputs['biospecimen_name']
#    else:
#        biospecimens=f
    if file.origin.task:
      task=api.tasks.get(file.origin.task)
    else:
      task=api.tasks.get(f.split('.')[0])
    if file.metadata['Kids First Biospecimen ID']:
      biospecimens=file.metadata['Kids First Biospecimen ID']
    else:
      if 'cbttc' in task.name or 'PNOC' in task.name:
        lii=re.split('-|_',task.name)
        ll=[lii[3],lii[4]]
        biospecimens="_".join(ll)
      elif 'alignment' in task.name or 'WES' in task.name:
        biospecimens=task.name.split('-')[1]
      else:
        print ("check:",task.name)
    base = 'https://kf-api-dataservice.kidsfirstdrc.org'
#    base = 'http://localhost:1080/'     #ssh -L 1080:kf-api-dataservice-qa.kidsfirstdrc.org:80 bastion-qa.kids-first.io -p 2222 -N
    bi_link = base + '/biospecimens/' + biospecimens
    response = requests.get(bi_link).json()
    participant=os.path.basename(response['_links']['participant'])
    external_aliquot_id=response['results']['external_aliquot_id']
    external_sample_id=response['results']['external_sample_id']
 #   external_sample_id=external_sample_id.replace(' ','-')
 #   li=external_sample_id.split('-')
 #   l=[li[0],li[1]]
 #   external_sample_id="-".join(l)
    sample_type=response['results']['source_text_tissue_type']
    age_at_event_days=response['results']['age_at_event_days']
    source_text_tumor_descriptor=response['results']['source_text_tumor_descriptor']
    composition=response['results']['composition']
    pi_link=base + response['_links']['participant']
    race=requests.get(pi_link).json()['results']['race']
    gender=requests.get(pi_link).json()['results']['gender']
    ethnicity=requests.get(pi_link).json()['results']['ethnicity']
    external_id=requests.get(pi_link).json()['results']['external_id']
    di_link=base + response['_links']['diagnoses']
    if requests.get(di_link).json()['results']:
        new_pr = []
        new_ty = []
        res=requests.get(di_link).json()['results']
        for ref in res:
     #     Age_at_diagnosis=requests.get(di_link).json()['results'][0]['age_at_event_days']
          Pri=ref['source_text_tumor_location']
          Dis=ref['source_text_diagnosis']
          if Pri:
             Pri=Pri.replace(',',';')
             if Pri not in new_pr:
               new_pr.append(Pri)
          Dis=Dis.replace(',',';').replace('\'','')
          if Dis not in new_ty:
               new_ty.append(Dis)
        Primary_site=";".join(new_pr)
        Disease_type=";".join(new_ty)
     #   print (Age_at_diagnosis,Primary_site,Disease_type)
    see_link=base + response['_links']['biospecimen_genomic_files']
    gf_link=base + requests.get(see_link).json()['results'][0]['_links']['genomic_file']
    #reference_genome=requests.get(gf_link).json()['results']['reference_genome']
    reference_genome='GRCh38'
    if requests.get(gf_link).json()['_links']['sequencing_experiment']:
      se_link=base + requests.get(gf_link).json()['_links']['sequencing_experiment']
      experiment_strategy=requests.get(se_link).json()['results']['experiment_strategy']
 #     Library_ID=requests.get(se_link).json()['results']['library_name']
      platform=requests.get(se_link).json()['results']['platform']

    file.metadata['Kids First Biospecimen ID'] = biospecimens
    file.metadata['experimental_strategy'] = experiment_strategy
    file.metadata['platform'] = platform
  #  file.metadata['library_id'] = Library_ID
    file.metadata['reference_genome'] = reference_genome
    file.metadata['case_id'] = external_id
    file.metadata['gender'] = gender
    file.metadata['race'] = race
    file.metadata['ethnicity'] = ethnicity
    file.metadata['sample_id'] = external_sample_id
    file.metadata['aliquot_id'] = external_aliquot_id
    file.metadata['sample_type'] = sample_type
    file.metadata['primary_site'] = Primary_site
#    file.metadata['age_at_diagnosis'] = Age_at_diagnosis
    file.metadata['disease_type'] = Disease_type
    file.metadata['Kids First Participant ID'] = participant
    file.metadata['age_at_diagnosis'] = age_at_event_days
    file.metadata['Tumor Descriptor'] = source_text_tumor_descriptor
    file.metadata['Composition'] = composition

 #   file.metadata = {'Kids First Biospecimen ID' : biospecimens,
 #                    'experimental_strategy' : experiment_strategy,
 #                    'platform' : platform,
  #                   'library_id' : Library_ID,
 #                    'reference_genome' : reference_genome,
 #                    'case_id' : external_id,
 #                    'gender' : gender,
 #                    'race' : race,
 #                    'ethnicity' : ethnicity,
 #                    'sample_id' : external_sample_id,
 #                    'aliquot_id' : external_aliquot_id,
 #                    'sample_type' : sample_type,
 #                    'primary_site' : Primary_site,
 #                    'disease_type' : Disease_type,
 #                    'Kids First Participant ID' : participant,
 #                    'age_at_diagnosis' : age_at_event_days,
 #                    'Tumor Descriptor' : source_text_tumor_descriptor
 #                 }
    
    file.save()
