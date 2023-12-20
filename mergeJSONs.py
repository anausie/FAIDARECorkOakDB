import os
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("folder", help="The full path to the folder that contains the JSON files to merge.")
parser.add_argument("output", help="The output file name")
args = parser.parse_args()

json_files = os.listdir(args.folder)
json_merged_file=args.output

allJSON=[]
baseName=os.path.basename(args.folder)
print(baseName)

# Load each JSON file into a Python object.
for json_file in json_files:
    # print("opening json file: ",json_file)
    with open(baseName+"/"+json_file, "r") as f:
        listjson = json.load(f)
        for item in listjson:
            #print(item)
            allJSON.append(item)

# Dump all the Python objects into a single JSON file.
with open(json_merged_file, "w") as f:
    json.dump(allJSON, f, indent=2)
