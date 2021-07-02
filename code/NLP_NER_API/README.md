# TNNT RESTful API + Enhancements

---
## Current packages
1. `flask`
2. `flask_restful`
3. `nltk`
4. `numpy`
5. `neuralcoref` (require c++ 14.0 version or greater)

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
