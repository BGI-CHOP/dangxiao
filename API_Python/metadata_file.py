import requests
import os
import sevenbridges as sbg
import argparse
new_dict = {}

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--projectid", help = "Required. Cavatica project id. (Example: kfdrc-harmonization/sd-bhjxbdqk-03)", type = str, required = True)
parser.add_argument("-s", "--studyid", help = "Required. kids first study id. (Example: SD_46SK55A3)", type = str, required = True)
args = parser.parse_args()

#base_url = 'https://cavatica-api.sbgenomics.com/v2/'
#api = sbg.Api(url = base_url, token = os.environ['cavatiac'])

c = sbg.Config(profile='cavatica')
api = sbg.Api(config=c)

base = 'http://localhost:1080/'
#sd_id = 'SD_BHJXBDQK'
sd_id = args.studyid
sd_link = base + '/genomic-files?study_id=' + sd_id

while sd_link:
    response = requests.get(sd_link).json()
    results = response['results']
    for result in results:
      if ('cram' in result['file_name'] or 'vcf' in result['file_name']):
        biospecimens=os.path.basename(result['_links']['biospecimen'])
        reference_genome=result['reference_genome']
        bi_link=base + result['_links']['biospecimen']
        participant=os.path.basename(requests.get(bi_link).json()['_links']['participant'])
        external_aliquot_id=requests.get(bi_link).json()['results']['external_aliquot_id']
        external_sample_id=requests.get(bi_link).json()['results']['external_sample_id']
        pi_link=base + requests.get(bi_link).json()['_links']['participant']
        race=requests.get(pi_link).json()['results']['race']
        gender=requests.get(pi_link).json()['results']['gender']
        ethnicity=requests.get(pi_link).json()['results']['ethnicity']
        external_id=requests.get(pi_link).json()['results']['external_id']
        see_link=base + requests.get(bi_link).json()['_links']['genomic_files']
        for re in requests.get(see_link).json()['results']:
            if 'bam' in re['file_format']:
               se_link=base + re['_links']['sequencing_experiment']
        experiment_strategy=requests.get(se_link).json()['results']['experiment_strategy']
 #       new_dict[result['file_name']]['is_paired_end']=requests.get(se_link).json()['results']['is_paired_end']
        Library_ID=requests.get(se_link).json()['results']['library_name']
        platform=requests.get(se_link).json()['results']['instrument_model']
        new_dict[result['file_name']] = {
                    'biospecimens': biospecimens,
                    'reference_genome': reference_genome,
                    'participant': participant,
                    'external_aliquot_id': external_aliquot_id,
                    'external_sample_id': external_sample_id,
                    'race': race,
                    'gender': gender,
                    'ethnicity': ethnicity,
                    'external_id': external_id,
                    'experiment_strategy': experiment_strategy,
                    'Library_ID': Library_ID,
                    'platform': platform
                }
    try:
        sd_link = base + response['_links']['next']
    except:
        break

project_id = args.projectid
files = api.files.query(project=project_id).all()
my_files= [file for file in files if 'cram' in file.name or 'vcf' in file.name]
for my_file in my_files:
# Edit a file's metadata
    if my_file.name in new_dict.keys():
        my_file.metadata['experimental_strategy'] = new_dict[my_file.name]['experiment_strategy']
        my_file.metadata['platform'] = new_dict[my_file.name]['platform']
        my_file.metadata['library_id'] = new_dict[my_file.name]['Library_ID']
        my_file.metadata['reference_genome'] = new_dict[my_file.name]['reference_genome']
        my_file.metadata['case_id'] = new_dict[my_file.name]['external_id']
        my_file.metadata['gender'] = new_dict[my_file.name]['gender']
        my_file.metadata['race'] = new_dict[my_file.name]['race']
        my_file.metadata['ethnicity'] = new_dict[my_file.name]['ethnicity']
        my_file.metadata['sample_id'] = new_dict[my_file.name]['external_sample_id']
        my_file.metadata['aliquot_id'] = new_dict[my_file.name]['external_aliquot_id']
        my_file.metadata['Biospecimens ID'] = new_dict[my_file.name]['biospecimens']
        my_file.metadata['Participant ID'] = new_dict[my_file.name]['participant']

        my_file.save()
    else:
        print (my_file.name)
