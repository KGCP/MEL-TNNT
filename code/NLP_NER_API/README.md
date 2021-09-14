# TNNT RESTful API: NLP Enhancements

---
## Architecture
![Architecture Diagram](https://github.com/KGCP/MEL-TNNT/blob/master/docs/TNNT/TNNT-RESTful-API-Architecture.png)

---
## Current packages
1. `python` (`3.8.4`)
2. `flask` (`2.0.1`)
3. `flask_restful` (`0.3.9`)
4. `numpy` (`1.21.0`)
5. `spaCy` (`3.0.6`)
6. `stanza` (`1.2.1`)

---
## Usage

1. The index website: `server_name:5000/`  

2. Normal browsing: `server_name:5000/USECASE/DATASET/FILENAME(or HASHEDFILENAME)/METHOD/_output/CATERGORY/ENTITY`  

3. To get the _stats of particular jsonfile:  
   `server_name:5000/USECASE/DATASET/FILENAME (or HASHEDFILENAME)/METHOD/`

4. Enables to Search using ?search in the below path:  
   `server_name:5000/USECASE/DATASET/FILENAME(or HASHEDFILENAME)`

5. To match search for an entity (startswith/endswith/substring)  
    `~/_output/CATEGORY?*Entity`  
    `~/_output/CATEGORY?Entity*`  
    `~/_output/CATEGORY?*Entity*`  
Note that: `~/_output/CATEGORY?Entity` is not accepted  

6. Search the entity:  
    `server_name:5000/USECASE/DATASET/FILENAME(or HASHEDFILENAME)/METHOD/_output/CATERGORY/ENTITY?QUERY`  
    `QUERY := (indexes | start_index | end_index | sentence | model | category | count)`

7. aggregate groups of files to summary:  
    `server_name:5000/USECASE/DATASET/FILENAME?aggr`  
    If the file is aggregated before, will raise an error.

8. Use filter function in summary file:  
    `server_name:5000/USECASE/DATASET/FILENAME/summary?fnum` (or `f*num` or `f*str` or `furl`)

9. POS-tagging and dependency parser
    `server_name:5000/USECASE/DATASET/FILENAME/MODEL?PT_DP_tasks&tool=(stanza | spacy | * | all)&replace=(0 | 1)`

10. Predict the elapsed time in PT-DP
    `server_name:5000/USECASE/DATASET/FILENAME/MODEL?predict&tool=(stanza | spacy | * | all)`

11. Coreference Task
    `~/FILENAME?CoRef_task&replace=(0 | 1)&retrieve=(full | corefs | sentences)` [MEL+NER_output]
    OR `~/FILENAME/MODEL?CoRef_task&replace=(0 | 1)&retrieve=(full | corefs | sentences)` [regular outputs]
