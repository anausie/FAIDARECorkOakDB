# FAIDARECorkOakDB

This repository contains 2 scripts used to index [CorkOakDB](https://corkoakdb.org/) to [FAIDARE](https://urgi.versailles.inra.fr/faidare/).

CorkOakDB is a Tripal based web portal, hosting the cork oak genome.

### parsingGenesFromWSCorkOakDB.py
**parsingGenesFromWSCorkOakDB.py** uses the portal API to retrieve information about the genes, including gene IDs, available description and IPR and GO annotations. The script outputs multiple files (depending on the number of pages parsed) name.d CorkOakDB_geneSetX.json.
json file is built according with the fields required by FAIDARE  


usage: parsingGenesFromWSCorkOakDB.py [-h] [-page NPAGE] [-sleep NSLEEP]
                                      [-items NITEMS][-folder FOLDER]

optional arguments:
  -h, --help       show this help message and exit
  -page NPAGE      The page number to start quering.
  -sleep NSLEEP    The number of seconds to wait between pages retrieval.
  -items NITEMS    The number of items per page to retrieve.
  -folder FOLDER   The path of the folder where the JSON files will be stored. if none is provided the default folder name will be created in the current directory.


### mergeJSONs.py
**mergeJSONs.py** gets a folder containing a set of json output files and merges them into a single json file.  

usage: mergeJSONs.py [-h] folder output

positional arguments:
  folder      The full path to the folder that contains the JSON files to
              merge.
  output      The output file name

optional arguments:
  -h, --help  show this help message and exit
