'''
@component: Metadata Extraction & Loader (MEL) / DoEE_Species.
@author: Sergio.
@summary: Extraction of the associated metadata about DoEE endangered species documents.
@project: AGRIF.
# History Update:
#    2020-01-18: internal release of version 0.1.0.
#    2020-02-06: retrieving WikiData *species* entity URI (information) for rows with scientific name.
#    2020-02-14: modifying *CA_ps* search to support 91 entries that don't match their filename prefix with the listed_ID field.
#    2020-03-02: retrieving WikiData *conservation status* entity URI (information).
#    2020-03-26: check species (Sci_Names) in Assessments docs.
'''


# ==================================================================================================
import json
import re
import datetime
from SPARQLWrapper import SPARQLWrapper, JSON # https://rdflib.github.io/sparqlwrapper/
# //from wikidata.client import Client
import MEL


# ==================================================================================================
class CAsAndRPs:
    '''
    classdocs
    '''
    BASE = {
        "NONE": "~None",
        "CA_ps": {
            "wb": "PS - Conservation Advice",
            "dir": "conservation_advices\\\ps",
            "upper-bound": 0
        },
        "CA_tc": {
            "wb": "TC - Conservation Advice",
            "dir": "conservation_advices\\\\tc",
            "upper-bound": 0
        },
        "RP_ps": {
            "wb": "PS - Recovery Plans",
            "dir": "recovery_plans\\\ps",
            "upper-bound": 0
        },
        "RP_tc": {
            "wb": "TC - Recovery Plans",
            "dir": "recovery_plans\\\\tc",
            "upper-bound": 0
        }
    }
    LOADED = False
    DATA = {} # dictionary of the associated metadata
    RESULT = [] # a list of associated data (possible multiple rows)


    # load(): Loads (only once) the *conservation_advices.xlsx* file with the associated metadata.
    @staticmethod
    def load():
        '''
        OBSERVATIONS:
        1) It seems that the lexicographic sorting in Excel works differently as in Python.
        Excel:
            1378-conservation-advice.pdf
            13792-conservation-advice-16122016.pdf
            137-conservation-advice.pdf
        Python:
            137-conservation-advice.pdf
            1378-conservation-advice.pdf
            13792-conservation-advice-16122016.pdf
        2) Due that the lexicographic comparison between strings is not giving correct results,
        the "CA" data sets were sorted based on the second field and not based on the filename.
        3) The upper bound list calculation applies only to the "RP_ps" data set.
        '''
        # Set the upper bound for a data set:
        def setUpperBoundFor(key):
            a = CAsAndRPs.DATA["Specific-Metadata"]["workbooks"][CAsAndRPs.BASE[key]["wb"]]
            p = -1
            if (key == "RP_ps"):
                # Looks for '~None' in the LAST FIELD of the data set:
                p = MEL.AssociatedMetadata.binarySearch(a, CAsAndRPs.BASE["NONE"], "str", len(a[0])-1, 1, len(a)-1)
                MEL.Utils.output(f"key={key}; upper-bound={p}", _print=False)
            # if found: sets the proper upper bound (ignore all "Blank" values)
            # default value: the length of the list.
            CAsAndRPs.BASE[key]["upper-bound"] = (p-1) if (p != -1) else (len(a)-1)

        CAsAndRPs.RESULT = [] # The RESULT array is cleared (reset).
        if (not CAsAndRPs.LOADED): # checks if the file is already loaded.
            CAsAndRPs.DATA = MEL.AssociatedMetadata.load("DoEE_Species_CAsAndRPs")
            setUpperBoundFor("CA_ps")
            setUpperBoundFor("CA_tc")
            setUpperBoundFor("RP_ps")
            setUpperBoundFor("RP_tc")
            MEL.Utils.output(json.dumps(CAsAndRPs.BASE, indent=4), _print=False)
            CAsAndRPs.LOADED = True


    # find(dataset, x): Looks for the value "x" in "dataset".
    @staticmethod
    def find(dataset, x, else_x=""):
        a = CAsAndRPs.DATA["Specific-Metadata"]["workbooks"][CAsAndRPs.BASE[dataset]["wb"]]
        # Sorting field: CA=(second)|(int), RP=(last)|(str)
        i = (len(a[0])-1) if (dataset[:2] == "RP") else 1 # index
        d = "str"         if (dataset[:2] == "RP") else "int" # data type
        u = CAsAndRPs.BASE[dataset]["upper-bound"]
        p =  MEL.AssociatedMetadata.binarySearch(a, x, d, i, 1, u) if (dataset != "RP_ps")\
        else MEL.AssociatedMetadata.simpleSearch(a, x, d, i, 1, u, "++")
        if ((dataset == "CA_ps") and (p == -1)):
            ''' For 91 entries in *CA_ps*, the filename ID prefix doesn't match with the *listed_id* field.
            Therefore, we proceed to perform a simple search based on the filename field (d="str", i=5),
            in order to retrieve the entries from the spreadsheet. '''
            p = MEL.AssociatedMetadata.simpleSearch(a, else_x, "str", 5, 1, u, "++")
            MEL.Utils.output(f"dataset={dataset}; value={else_x}; position={p}", _print=False)
        MEL.Utils.output(f"dataset={dataset}; value={x}; position={p}", _print=False)
        return (a, p) if (p != -1) else ([], p)


    # getCA(dataset, x): Looks for the "Conservation Advice" associated data.
    @staticmethod
    def getCA(dataset, x):
        listed_id = int(x.split("-")[0]) # gets the "listed_id" number from the filename.
        a, p = CAsAndRPs.find(dataset, listed_id, x) # For *CA_ps*, if not found then tries to search with the filename.
        if (p != -1):
            # traverse the list of associated data: multiple rows.
            field_3_name = "Sci_Name" if (dataset[3:] == "ps") else "Status"
            asset_type = ""
            field_3_value = ""
            ref_type = ""
            data = {}
            while True:
                if ((asset_type    != a[p][0].strip()) or\
                    (field_3_value != a[p][2].strip()) or\
                    (ref_type      != a[p][3].strip())): # only when at least one value is different
                    data = {
                        "asset_type": a[p][0].strip(),
                        "listed_id":  a[p][1],
                        field_3_name: a[p][2].strip(),
                        "ref_type":   a[p][3].strip(),
                        "url":        a[p][4].strip(),
                        "file_name":  a[p][5].strip(),
                        "Row_Number_in_Spreadsheet": (p+1)
                    }
                    if (field_3_name == "Sci_Name"):
                        data["Species_WikiData_Entity_URI"] = CAsAndRPs.WikiData_getSpeciesEntityURI(a[p][2].strip())
                    if (field_3_name == "Status"):
                        data["ConservationStatus_WikiData_Entity_URI"] = CAsAndRPs.WikiData_getConservationStatusEntityURI(a[p][2].strip())
                    CAsAndRPs.RESULT.append(data)
                asset_type    = a[p][0].strip()
                field_3_value = a[p][2].strip()
                ref_type      = a[p][3].strip()
                p += 1
                if (p == len(a)) or not(a[p][1] == listed_id): # short-circuit evaluation
                    break
            MEL.Utils.output(json.dumps(CAsAndRPs.RESULT, indent=4), _print=False)
        # if not found (p == -1): return an empty JSON structure (initial).
        return CAsAndRPs.RESULT


    # getRP(dataset, x): Looks for the "Recovery Plans" associated data.
    @staticmethod
    def getRP(dataset, x):
        a, p = CAsAndRPs.find(dataset, x)
        if (p != -1):
            # traverse the list of associated data: multiple rows.
            field_3_name = "Sci_Name" if (dataset[3:] == "ps") else "Description"
            asset_type = ""
            listed_id = 0
            field_3_value = ""
            ref_type = ""
            data = {}
            while True:
                if ((asset_type    != a[p][0].strip()) or\
                    (listed_id     != a[p][1]) or\
                    (field_3_value != a[p][2].strip()) or\
                    (ref_type      != a[p][3].strip())): # only when at least one value is different
                    data = {
                        "asset_type": a[p][0].strip(),
                        "listed_id":  a[p][1],
                        field_3_name: a[p][2].strip(),
                        "ref_type":   a[p][3].strip(),
                        "url":        a[p][4].strip(),
                      "Web_location": a[p][5].strip(),
                        "file_name":  a[p][6].strip(),
                        "Row_Number_in_Spreadsheet": (p+1)
                    }
                    if (field_3_name == "Sci_Name"):
                        data["Species_WikiData_Entity_URI"] = CAsAndRPs.WikiData_getSpeciesEntityURI(a[p][2].strip())
                    CAsAndRPs.RESULT.append(data)
                asset_type    = a[p][0].strip()
                listed_id     = a[p][1]
                field_3_value = a[p][2].strip()
                ref_type      = a[p][3].strip()
                p += 1
                if (p == len(a)) or not(a[p][6].strip() == x): # short-circuit evaluation
                    break
            MEL.Utils.output(json.dumps(CAsAndRPs.RESULT, indent=4), _print=False)
        # if not found (p == -1): return an empty JSON structure (initial).
        return CAsAndRPs.RESULT


    # get(_path, _filename): Looks for the data associated given the file location (path and filename).
    @staticmethod
    def get(_path, _filename):

        def match_in(key):
            # matches the file location to the specific workbook:
            match = re.search(CAsAndRPs.BASE[key]["dir"], _path)
            MEL.Utils.output(f"match: {match}", _print=False)
            if (match):
                method = getattr(globals()["CAsAndRPs"], ("get" + key[:2]), lambda key, _filename: {})
                CAsAndRPs.RESULT = method(key, _filename)
                return True
            return False
        
        CAsAndRPs.load()
        # short-circuit evaluation:
        if (match_in("CA_ps")) or (match_in("CA_tc")) or\
           (match_in("RP_ps")) or (match_in("RP_tc")):
            return CAsAndRPs.RESULT
        return {}


    # WikiData_execSPARQLquery(query): Executes a query on the WikiData SPARQL endpoint.
    @staticmethod
    def WikiData_execSPARQLquery(query):
        C_ENDPOINT_URL = "https://query.wikidata.org/sparql"
        # <https://www.mediawiki.org/wiki/Wikidata_Query_Service/User_Manual#Basics_-_Understanding_Prefixes>
        # // C_WIKIDATA_ENTITY_URL_PREFIX = "http://www.wikidata.org/entity/"

        sparql = SPARQLWrapper(C_ENDPOINT_URL)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        # // client = Client()
        for result in results["results"]["bindings"]:
            # // entity_id = str(result["item"]["value"]).split(C_WIKIDATA_ENTITY_URL_PREFIX, 1)[1]
            # // entity = client.get(entity_id, load=True)
            MEL.Utils.output(f"{result}\n{{entity.id}}\n{{entity.label}}\n{{json.dumps(entity.attributes, indent=4)}}", _print=False)
            return result["item"]["value"] # // entity.attributes # returns only the first result.
        return "" # // {}


    # WikiData_getEntityURI(sci_name): Retrieves the WikiData Entity URI of a species given its scientific name.
    @staticmethod
    def WikiData_getSpeciesEntityURI(sci_name):
        query = f"""# Specie by taxonname (scientific name).
        SELECT ?item ?taxonname WHERE {{
          ?item wdt:P225 "{sci_name.strip()}" .
        }}""" # it's expected only one result.
        return CAsAndRPs.WikiData_execSPARQLquery(query)


    # WikiData_getConservationStatusEntityURI(cs_name): Retrieves the WikiData Entity URI of a conservation status (as defined by IUCN) given its label.
    @staticmethod
    def WikiData_getConservationStatusEntityURI(cs_name):
        '''
        <https://www.wikidata.org/wiki/Property:P31> <instance of>.
        <https://www.wikidata.org/wiki/Q82673>    "conservation status".  Instances:
        * <https://www.wikidata.org/wiki/Q278113> "vulnerable".
        * <https://www.wikidata.org/wiki/Q219127> "critically endangered".
        * <https://www.wikidata.org/wiki/Q11394>  "endangered species".
        '''
        cs_name = cs_name.lower()
        cs_name += " species" if (cs_name == "endangered") else ""
        query = f"""# conservation status as defined by IUCN.
        SELECT ?item ?desc
        WHERE {{
          ?item wdt:P31 wd:Q82673 ;
            rdfs:label "{cs_name}"@en ;
            schema:description ?desc .
          FILTER (lang(?desc) = "en") .
          FILTER regex(?desc, "(.*)(IUCN)(.*)", "i") .
        }}""" # it's expected only one result.
        return CAsAndRPs.WikiData_execSPARQLquery(query)


# ==================================================================================================
# Find Species Sci_Names in the content of Assessment documents:
def DoEE_Species_Sci_Names_In_Assessments(startsFromSpeciesNum):

    def existsInArray(arr, key):
        for e in arr:
            if (e["Sci_Name"] == key):
                return True
        return False

    def checkSciNameInText(s_json, x, label, _num, _len):
        found = False
        indent = ">> " if ((label == "attachment") or (label == "file-in-zip")) else ""
        if ("text-analysis" in x["Specific-Metadata"]):
            text = x["Specific-Metadata"]["text-analysis"]["ascii-text"].lower()
            if (s_json["Sci_Name"] in text): # adds the information about the species in the assessments doc.
                if not("about-DoEE-Species" in x["Associated-Metadata"]): # creates an array.
                    x["Associated-Metadata"]["about-DoEE-Species"] = []
                if not(existsInArray(x["Associated-Metadata"]["about-DoEE-Species"], s_json["Sci_Name"])):
                    x["Associated-Metadata"]["about-DoEE-Species"].append({ # multiple species referenced in a document.
                        "Sci_Name"           : s_json["Sci_Name"], 
                        "WikiData_Entity_URI": s_json["Species_WikiData_Entity_URI"]
                        })
                print(f"""|... {indent}{label} #{_num}/{_len}: {x["General-Metadata"]["FILENAME"]}; id=({_id})""")
                found = True
        _num += 1
        return _num, found

    def lookInContent(extension, l):
        foundAtLeastOne = False
        if ((extension == "msg") or (extension == "zip")):
            num, found = 1, False
            l = l["attachments"] if (extension == "msg") else l
            for a in l:
                num, found = checkSciNameInText(s_json, l[a]["metadata"],
                            "attachment" if (extension == "msg") else "file-in-zip",
                            num, len(l))
                foundAtLeastOne = True if (found) else foundAtLeastOne
            if (foundAtLeastOne):
                desc = "attachments above are found in file" if (extension == "msg") else "files above are found in zip"
                print(f"""|... ({desc}) #{num_files}/{len_docs}: {x["General-Metadata"]["FILENAME"]}; id=({_id})""")
        return foundAtLeastOne

    dt_begin = datetime.datetime.now()
    print("Project AGRIF | MEL: Metadata Extractor & Loader | DoEE: Species references in Assessment docs.")
    MEL.Utils.printStartTimeStamp(dt_begin)
    DB = "/doee-species"
    selector = {
      "General-Metadata": {
         "ABSOLUTEPATH": {
            "$regex": "(.*)(\\\\ps\\\\)(.*)"
         }
      }
    }
    fields = ["Associated-Metadata"]
    r = MEL.CouchDB.queryDocs(DB, selector, False, fields)
    speciesSet = set()
    for x in r["docs"]:
        if (len(x["Associated-Metadata"]) == 1):
            speciesSet.add(x["Associated-Metadata"][0]["Sci_Name"].lower() + "|" + x["Associated-Metadata"][0]["Species_WikiData_Entity_URI"])
    len_speciesSet = len(speciesSet)
    print(f"\nSet of species scientific names @{{{DB}}} | Length={len_speciesSet}:")
    #print(f"{speciesSet}")
    DB = "/doee-assessments"
    '''
    "ABSOLUTEPATH": {
        "$regex": "(.*)(\\\\DoEE_assessments\\\\)(.*)" # only the last version of the documents
    },
    '''
    selector = {
        "General-Metadata": { # retrieve _all_ documents (latest version and history):
            "$or": [ # only the following file formats:
                { "EXTENSION": "docx" },
                { "EXTENSION": "docm" },
                { "EXTENSION": "doc" },
                { "EXTENSION": "pdf" },
                { "EXTENSION": "msg" }
            ]
        }
    }
    # retrieve all the JSON structure.
    fields = ["_id", "_rev", "General-Metadata", "Use-Case$Folder", "Specific-Metadata", "Associated-Metadata", "_attachments"]
    r = MEL.CouchDB.queryDocs(DB, selector, False, fields)
    len_docs = len(r["docs"])
    print(f"Analysis in documents' text @{{{DB}}} | Length={len_docs} | (only displaying found occurrences)")
    print(f"MANGO Query for retrieval: {json.dumps(selector, indent=4)}")
    print(f"Starting processing from species number: {startsFromSpeciesNum}\n")
    num_sci_names = 1
    s_json = {}
    for s in speciesSet:
        if (num_sci_names >= startsFromSpeciesNum):
            num_files, foundInFile, display = 1, False, False
            s_json = {
                    "Sci_Name":                    s.split("|")[0],
                    "Species_WikiData_Entity_URI": s.split("|")[1]
                }
            #MEL.Utils.output(json.dumps(s_json, indent=4), _print=True)
            for x in r["docs"]:
                _id = x["_id"]
                num_files, foundInFile = checkSciNameInText(s_json, x, "filename", num_files, len_docs)
                if (foundInFile):
                    num_files -= 1 # for displaying purposes in next function
                foundInComponent = lookInContent(x["General-Metadata"]["EXTENSION"], x["Specific-Metadata"])
                if (foundInFile) or (foundInComponent):
                    MEL.CouchDB.updateDocument(_id, x) # update the JSON object on CouchDB.
                    print(f"""| (document updated)""")
                    display = True
                if (foundInFile):
                    num_files += 1 # restores the correct value
            if (display):
                print(f"|__ Sci_Name #{num_sci_names}/{len_speciesSet}: {s}\n\n")
        else:
            print(f"|__ ... skipping processing of: Sci_Name #{num_sci_names}/{len_speciesSet}: {s}\n\n")
        num_sci_names += 1
    dt_end = datetime.datetime.now()
    delta = (dt_end - dt_begin).total_seconds()
    MEL.Utils.printEndTimeStamp(dt_end, delta)


# ==================================================================================================
# main
if __name__== "__main__":
    MEL.Utils.initLogging("DoEE_Species")
    
    ROOT = "E:\\_temp\\DepFin-Project\\DoEE_endangered-species\\CAsAndRPs\\"
    
    FOLDER = "conservation_advices\\tc\\"
    #"recovery_plans\\tc\\"
    
    FILE  = "031-conservation-advice.pdf"
    #"alpine-sphagnum-bogs-associated-fens-recovery-plan.pdf"
    
    data = CAsAndRPs.get(ROOT + FOLDER, FILE)
    #data = CAsAndRPs.WikiData_getInfo("Megaptera novaeangliae")
    
    MEL.Utils.output(json.dumps(data, indent=4), _print=True)
    '''
    # ===
    DoEE_Species_Sci_Names_In_Assessments()
    '''