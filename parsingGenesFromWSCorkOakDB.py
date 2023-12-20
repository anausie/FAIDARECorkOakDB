import requests
import json
import os
import time
import argparse
import logging



parser = argparse.ArgumentParser()
parser.add_argument("-page", dest='nPage', default=1, help="The page number to start quering.")
parser.add_argument("-sleep", dest='nSleep', default=90, help="The number of seconds to wait between pages retrieval")
parser.add_argument("-items", dest='nItems', default=100, help="The number of items per page to retrieve")
parser.add_argument("-folder", dest='folder', default='Pages-CorkOakDB-JSON', help="The path of the folder where the JSON files will be stored. If none is provided the default folder name will be created in the current directory")

logging.basicConfig(filename='CorkOakDB-JSON.log', level=logging.DEBUG)

#Global variables
processPage = True
lastPage = str()
last = False
nPage = None
nSleep = None
nItems = None
URL_basejson = None
foder=None
# URL_basejson="https://corkoakdb.org/web-services/content/v0.1/Gene?page=1&limit=200"

# Functions
def fetch(url, max_retries):
    # print("Fetch ", url, max_retries)
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url)
            geneListJson = response.json()
            return geneListJson
        except requests.exceptions.ReadTimeout as error1:
            logging.warning("Attempt {attempt} failed. Error: {error1}")
            if attempt < max_retries:
                print("Retrying...")
            else:
                raise
        except:
            logging.error('Connection troubles. Waiting before trying again: ')
            time.sleep(300)

def convertItem2Json(name, product, url, annotation):
    if annotation != "":
          description=name+" is a "+product+". Annotation:" + annotation
    else:
      description = name + " is a " + product + "."

    value = {
        "entryType" : "Gene",
        "node" : "Biodata.pt",
        "databaseName" : "CorkOakDB",
        "description" : description,
        "url" : url,
        "species": ["Quercus suber L."],
        "name" : name
    }
    return json.loads(json.dumps(value, indent=2))

def savePage2jsonFile(allGenesJson, file):
    with open(file, 'a+') as json_file:
        json.dump(allGenesJson, json_file, indent=2, separators=(',',': '))

def parsingGenePage():
    global URL_basejson, lastPage, last, processPage, nGene, nPseudoGene, folder
    allGenesJson=[]
    logging.info("Reading page (%i): %s", nPage, URL_basejson)
    geneListJson=fetch(URL_basejson, 5)
    if not lastPage:
        lastPage=geneListJson['view']['last']
    # Iterating over the list of Genes
    for i in range(len(geneListJson['member'])):
        entryGeneList = geneListJson['member'][i]
        geneJson = entryGeneList['@id']
        # Obtaining the gene information
        logging.info("Reading gene information: %s", geneJson)
        geneContentJson = fetch(geneJson, 5)
        # The pseudogenes will be not included in the final JSON. This type of genes
        # have not the product field included, so it is necessary to first check for the presence of
        # this field in order to process the gene of interest.
        if 'product' in geneContentJson:
            geneName = geneContentJson['name']
            geneProduct = geneContentJson['product']
            geneURL = geneContentJson['ItemPage']
            geneAnnotation = ""
            # open annotation JSON information
            logging.info("Reading gene %s information: %s", geneName, geneContentJson['annotation'])
            annotationContentJson = fetch(geneContentJson['annotation'], 5)
            # Checking if there is any annotation associated to the gene
            if 'member' in annotationContentJson:
                for j in range(len(annotationContentJson['member'])):
                    entryAnnotation = annotationContentJson['member'][j]
                    if entryAnnotation['vocabulary'] == "GO":
                        geneAnnotation += " GO:" + entryAnnotation['accession'] + " " + entryAnnotation['name'] + ";"
                    else:
                        geneAnnotation += " " + entryAnnotation['accession'] + " " + entryAnnotation['name'] + ";"
            else:
                logging.warning("No annotation found for this gene.")
            # Add the gene information to the list
            geneJsonInformation = convertItem2Json(geneName, geneProduct, geneURL, geneAnnotation)
            allGenesJson.append(geneJsonInformation)
        else:
            logging.warning("Pseudogene: %s. This gene will be discarded", geneContentJson['name'])
    # Save the results page into a file
    if not allGenesJson:
        logging.warning("No genes to save from this page")
    else:
        file=os.path.notmpath(folder)+"/CorkOakDB_geneSet"+str(nPage)+".json"
        logging.info("Saving genes into file: %s", file)
        savePage2jsonFile(allGenesJson,file)
    # Saving the all compiled genes into a JSON file
    # Proceed to check if there is more pages to read
    if not last:
        if not 'next' in geneListJson['view']:
            URL_basejson=lastPage
            last=True
            # print("Next page is the last: "+URL_basejson)
        else:
            URL_basejson=geneListJson['view']['next']
            # print("Next page is: " + URL_basejson)
    else:
        processPage=False
        logging.info("No more pages to read.")


args = parser.parse_args()
nPage = int(args.nPage)
nSleep = int(args.nSleep)
nItems = int(args.nItems)
folder=args.folder
URL_basejson = "https://corkoakdb.org/web-services/content/v0.1/Gene?page="+str(nPage)+"&limit="+str(nItems)

if not os.path.exists(folder):
    os.makedirs(folder)

while processPage:
    parsingGenePage()
    if processPage:
        time.sleep(nSleep)
        nPage += 1
    else:
        logging.info("DONE! :)")

