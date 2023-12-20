import urllib.request, json
import time
import urllib3
import requests
import re
from urllib.error import URLError
from socket import timeout as TimeoutError
import sys

def fetch_url_with_retry(url, max_retries, timeout):
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as url_response:
                return json.loads(url_response.read().decode())
        except (URLError, TimeoutError) as e:
            print(f"Attempt {attempt} failed. Error: {e}")
            if attempt < max_retries:
                print("Retrying...")
            else:
                raise  # If all attempts fail, raise the last encountered exception


def member_parser(current_page,output_json,page_counter):        # e.g page : https://corkoakdb.org/web-services/content/v0.1/Gene?page=1&limit=100
    page_json = fetch_url_with_retry(current_page, max_retries=5, timeout=60)
    print('Retrieving Genes')
    members = page_json['member']
    for i in members:
        gene_url = i['@id']                             # n x '@id': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211'
        with urllib.request.urlopen(gene_url) as url:   # Open the Gene JSON file from gene_url
            data = json.loads(url.read().decode())      # n x {'@context': 'https://corkoakdb.org/sites/default/files/tripal/ws/context/content.v0_1.gene.35211.json', '@id': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211', '@type': 'gene', 'label': 'LOC111982896', 'ItemPage': 'https://corkoakdb.org/bio_data/35211', 'type': ['Gene', 'gene'], 'name': 'LOC111982896', 'identifier': 'gene-LOC111982896', 'transcript': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211/transcript', 'database_cross_reference': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211/database+cross+reference', 'sequence_coordinates': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211/Sequence+coordinates', 'location_on_map': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211/location+on+map', 'annotation': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211/annotation', 'publication': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211/publication', 'relationship': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211/relationship', 'gene_expression_data': '190326', 'product': 'uncharacterized LOC111982896', 'sequence_record': 'https://corkoakdb.org/web-services/content/v0.1/Gene/35211/Sequence+record'}
            GENE_ID = data['name']
            URL = data['ItemPage']
            if 'pseudogene' not in data['type']:
                try:
                    PRODUCT = data['product']
                except:
                    PRODUCT = data['type'][1]
                ANNOTATION = ''
                annotation_url = data['annotation']         # https://corkoakdb.org/web-services/content/v0.1/Gene/35211/annotation
                with urllib.request.urlopen(annotation_url) as url:  # Open the Gene JSON file from annotation_url
                    annotation_data = json.loads(url.read().decode())
                    # INTERPRO + GO RETRIEVAL
                    try:
                        for i in annotation_data['member']:
                            if annotation_data['member'][0]['vocabulary'] == 'GO':
                                ANNOTATION += f"GO: {annotation_data['member'][0]['accession']} {annotation_data['member'][0]['name']};"
                            else:
                                ANNOTATION += f"{annotation_data['member'][0]['accession']} {annotation_data['member'][0]['name']};"
                        output_string = f'{GENE_ID} is a {PRODUCT}. Annotation: {ANNOTATION}'
                    except:
                        output_string = f'{GENE_ID} is a {PRODUCT}.'
                print(output_string)
                json_part = saveItem2Json(GENE_ID, URL, ANNOTATION)  # Save the json part to main json file
                output_json.append(json_part)
            else:
                pass

    # Update last page
    f = open("lastpage.txt", "w")
    f.write(str(page_counter))

    # Change page counter
    if 'next' in page_json['view']:
        current_page = page_json['view']['next']
    else:
        current_page = ''       # Breaking the while loop in main
    print(f'next current page:\n{current_page}\n')
    time.sleep(30)
    next = current_page
    return output_string, output_json, next


def saveItem2Json(name, url, annotation):
    value = {
        "entryType" : "Gene",
        "node" : "Biodata.pt",
        "databaseName" : "CorkOakDB",
        "description" : annotation,
        "url" : url,
        "species": ["Quercus suber L."],
        "name" : name
    }
    return json.loads(json.dumps(value, indent=2))


def start():
    # Build query

    try:
        f = open("lastpage.txt", "r")           # Checking last page if interruption
        page_counter = int(f.readline())+1
    except:
        page_counter = 1

    base_url    = 'https://corkoakdb.org'
    name        = 'Gene'
    limit       = 25
    page_url    = f'{base_url}/web-services/content/v0.1/{name}?page={page_counter}&limit={limit}'
    results     = 'corkoakdb.json'


    # Open json - entry
    print(page_url)
    page_data = fetch_url_with_retry(page_url, max_retries=10, timeout=60)  # # https://corkoakdb.org/web-services/content/v0.1/Gene?page=1&limit=25


    # Browsing Pages
    current_page = page_data['view']['@id']      # e.g page : https://corkoakdb.org/web-services/content/v0.1/Gene?page=1&limit=25
    last_page = page_data['view']['last']
    while current_page:
        output_json = []
        print(f'current page:\t{page_counter}\n{current_page}')
        output_string,output_json,current_page = member_parser(current_page,output_json,page_counter)
        print(output_json)
        # Dump json list for this page
        print("******** ", len(output_json))
        with open(results, 'a+') as f:
            text = json.dump(output_json, f, indent=2, separators=(',',': '))
        page_counter +=1

    # Last page actions
    with urllib.request.urlopen(last_page) as url:
        output_json = []
        page = json.loads(url.read().decode())
        print('Retrieving Genes')
        output_string,output_json,current_page = member_parser(page,output_json)

if __name__ == '__main__':
    # Save log
    sys.stdout = open('parser.log', 'w')
    # Start
    start()
