# Deep Narrative Analysis (DNA)
Updated September 16 2021

## License
Creative Commons 

Attribution 4.0 International 

CC BY 4.0

## Overview 

Deep Narrative Analysis (DNA) is a toolset for analyzing narratives. It combines semantic and natural language technologies with machine learning to 1) create knowledge graphs encoding the details of the narratives and any background/contextual knowledge from online and structured data sources, and 2) perform inference, reasoning and statistical analyses. 

## File Structure

The semantics (ontologies) and processing (initially, Jupyter notebooks) are captured in the directories of this project. The following folder structure is used:

* _dna_ contains the (evolving) Deep Narrative Analysis application executed through a simple GUI
  * The GUI was developed using PySimpleGUI (documented at https://pysimplegui.readthedocs.io/en/latest/)
  * No changes were made to the imported PySimpleGUI modules
  * The import structure of the DNA Python modules is visualized at https://github.com/ontoinsights/deep_narrative_analysis/blob/master/python_modules_overview.png
  * The _dna/resources_ dirctory contains pickle files, narrative texts used for testing, a dna.config file, etc.
    * Note that the .config file would have to be modified for a local environment
* _tests_ holds pytest validation code for the dna application
  * This code is NOT executed when pushing new code (as part of a github workflow) since a Stardog server would have to be deployed 
  * However, the code is run locally and the htmlcov sub-directory is included with the results
* _ontologies_ holds the definitions of the concepts and relationships that will be extracted from the narratives and online/structured data
  * All of the posted ontology files are written in Turtle (OWL2)
  * Domain-specific concepts and events are defined in the _domain-specific_ subdirectory of _ontologies_
    * At this time, these are all related to WWI, WWII and the Holocaust, and have been extracted from the reference pages of the U.S. Holocaust Museum website
    * Domain ontologies are not required for DNA to execute, but if available, improve the parse and semantic understanding
  * In addition, a Protege-ready merges of all general and domain-specific component files are available in the top-level directory. The files are named:
    * dna-ontology.ttl for the general concepts and events
    * domain-ontology.ttl for the domain-specific concepts and events
* _ontol-docs_ contains documentation explaining the ontologies and their usage
  * The _graphs_ sub-directory contains PNGs of the ontology concepts, where the graph local names correspond to the Turtle file modules' local names
  * The file, dna-ontology-tree.html, holds a searchable tree view of the generic concepts and relationships
  * The file, domain-ontology-tree.html, holds a searchable tree view of the domain-specific concepts and relationships
* _tools_ contains scripts used to generate the DNA ontology artifacts (the Protege-ready merge and tree output)
  * The create_merged_ontol_and_tree script uses a branched version of the robot.jar from the OBO ROBOT GitHub repository (https://github.com/ontodev/robot/tree/tree-view)
* _notebooks_ holds the Jupyter notebooks used to scrape/parse web pages, create necessary pickle files for processing, and perform initial parsing and analysis experiments on the narratives

## Environment

The Stardog triple store (downloadable from https://www.stardog.com/get-started/) must be installed and the following databases created:

* "ontologies" with the files from the _ontologies_ directory
* "domain-specific" with the files from the _ontologies/domain-specific_ subdirectory

In addition to downloading the spaCy library (which is addressed in requirements.txt), spaCy's transformer language model also needs to be installed. This is accomplished by executing "python3 -m spacy download en_core_web_trf".

These environment variables need to be set for the DNA application:

* PATH needs to specifically include the GitHub project's dna directory (for testing)
* TOKENIZERS_PARALLELISM = false (to resolve warning from HuggingFace transformers and their use in spaCy)

Furthermore, the dna.config file in the dna/resources directory should be updated to supply your Stardog username/password and GeoNames user name.

To run the application, cd to the dna directory and execute python3 app.py (making sure to have installed the Python libraries specified in the requirements.txt file).

### Execution Errors

When executing the application on a Mac, the following error may occur ... "Error loading wordnet: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:unable to get local issuer certificate (_ssl.c:1108)>". NLTK is the culprit (that is how WordNet is accessed) along with changes in Python. Python 3.6+ does not rely on/have access to MacOS' root certificates, and so certificate verification fails. To correct this:

* Follow the instructions at https://stackoverflow.com/questions/38916452/nltk-download-ssl-certificate-verify-failed - OR -
* Execute the _Install Certificates.command_ in the /Applications/Python 3.x directory
