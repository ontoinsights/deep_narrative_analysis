# Deep Narrative Analysis (DNA)
Updated 5 July 2022

## License
Creative Commons 

Attribution 4.0 International 

CC BY 4.0

## Overview 

Deep Narrative Analysis (DNA) is a toolset for analyzing narratives (biographical/autobiographical text, news articles, posts in Facebook and public online forums, etc.). It combines semantic, ontological and natural language technologies with machine learning to 1) create knowledge graphs encoding the details of the narratives and any background/contextual knowledge from online and structured data sources, and 2) perform inference, reasoning and statistical analyses. 

## File Structure

The semantics (ontologies) and processing are captured in the directories of this project. The following folder structure is used:

* _dna_ contains the (evolving) Deep Narrative Analysis application
  * The import structure of the DNA Python modules is visualized at https://github.com/ontoinsights/deep_narrative_analysis/blob/master/python_modules_overview.png
  * The _dna/resources_ dirctory contains narrative texts to be parsed, WordNet lexical details, etc.
* _tests_ holds pytest validation code for the dna application
  * This code is NOT executed when pushing new code (as part of a github workflow) since a Stardog server would have to be deployed 
  * However, the code is run locally and the htmlcov sub-directory is included with the results
* _ontologies_ holds the definitions of the concepts and relationships that are extracted from the narratives and online/structured data
  * All of the posted ontology files are written in Turtle (OWL2)
  * In addition, a Protege-ready merge of the ontology files (dna-ontology.ttl) is available in the top-level directory
* _ontol-docs_ contains documentation explaining the ontologies and their usage
  * The _graphs_ sub-directory contains PNGs of the ontology concepts, where the graph local names correspond to the Turtle file modules' local names
  * The file, dna-ontology-tree.html, holds a searchable tree view of the generic concepts and relationships
* _tools_ contains scripts used to generate the DNA ontology artifacts (the Protege-ready merge and tree output)
  * The create_merged_ontol_and_tree script uses a branched version of the robot.jar from the OBO ROBOT GitHub repository (https://github.com/ontodev/robot/tree/tree-view)
* _notebooks_ holds the Jupyter notebooks used to scrape/parse web pages, create necessary pickle files for processing, perform initial parsing and analysis experiments on the narratives, etc.

The original, "proof-of-concept" DNA codebase was _archived with the tag, v0.1.0-poc_, in July 2022. The code is being refactored to enable a more automated NL and ML analysis. A majority of the _dna_ python files are removed, as well as the domain-specific ontologies, in order to move to a new GUI and processing flow. 

## Environment and Execution

Necessary libraries are specified in the _requirements.txt_ file in the main directory. Please download all the necessary libraries before doing any testing.

In addition to downloading the required libraries, the following must also be installed:

* Stardog triple store, downloadable from https://www.stardog.com/get-started/
  * And, after installation, the database, "ontologies", should be created with the files from the _ontologies_ directory
* spaCy transformer language model 
  * Accomplished by executing "python3 -m spacy download en_core_web_trf"
* NLTK corpora data 
  * Accomplished by starting a Python session and executing:

```python
import nltk
nltk.download()
```

The download instruction opens a window showing the NLTK Data Collections. Select "all-corpora" and then press the "Download" button in the lower left corner.

Lastly, these environment variables need to be set for the DNA application:

* `PATH` needs to specifically include the GitHub project's dna directory (for testing)
* `TOKENIZERS_PARALLELISM = false` (to resolve warning from HuggingFace transformers and their use in spaCy)
* `STARDOG_ENDPOINT`, `STARDOG_USER` and `STARDOG_PASSWORD` should be set as appropriate

To run the application, cd to the dna directory and execute "python3 app.py -h". This will provide details on how to ingest, edit and display narrative details.
