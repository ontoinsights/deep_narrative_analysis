# Deep Narrative Analysis (DNA)
Updated September 16 2021

## License
Creative Commons 
Atribution 4.0 International 
CC BY 4.0

## Overview 

Deep Narrative Analysis (DNA) is a toolset for analyzing narratives. It combines semantic and natural language technologies with machine learning to 1) create knowledge graphs encoding the details of the narratives, 2) create knowledge graphs encoding background/contextual knowledge from online and structured data sources, and 3) perform inference, reasoning and statistical analyses. 

## File Structure

The semantics (ontologies) and processing (initially, Jupyter notebooks) are captured in the directories of this project. The following folder structure is used:

* _dna_ contains the (evolving) Deep Narrative Analysis application executed through a simple GUI
  * The GUI was developed using PySimpleGUI (documented at https://pysimplegui.readthedocs.io/en/latest/)
  * No changes were made to the imported PySimpleGUI module
  * The import structure of the DNA Python modules is visualized at https://github.com/ontoinsights/deep_narrative_analysis/blob/master/ontol-docs/graphs/python_modules_overview.png
* _tests_ holds pytest validation code for the dna application
  * This code is NOT executed when pushing new code (as a github workflow) since a Stardog server would have to be deployed 
  * However, the code is run locally and the htmlcov sub-directory is included to show results
* _ontologies_ holds the definitions of the concepts and relationships that will be extracted from the narratives and online/structured data
  * All of the posted ontology files are written in Turtle (OWL2) and have been updated to align with the March 2021 redesign
  * In addition, a Protege-ready merge of all the component files is available in the file, dna-ontology.ttl, in the top-level directory
* _ontol-docs_ contains documentation explaining the ontologies and their usage
  * The _graphs_ sub-directory contains PNGs of the main ontology concepts
  * The file, dna-ontology-tree.html, holds a searchable tree view of the complete set of concepts and relationships
* _tools_ contains scripts used to generate the DNA ontology artifacts (the Protege-ready merge and tree output)
  * The create_merged_ontol_and_tree script uses a branched version of the robot.jar from the OBO ROBOT GitHub repository (https://github.com/ontodev/robot/tree/tree-view)
* _notebooks_ holds the Jupyter notebooks used to scrape/parse web pages, create necessary pickle files for processing, and perform initial parsing and analysis experiments on the narratives
  * Note that various .config files are also defined to customize the processing (and should be modified if used in your personal environments)

## Environment

The Stardog triple store must be installed and the following environment variables need to be set for the DNA application:

* PATH needs to specifically include the GitHub project's dna directory (for testing)
* TOKENIZERS_PARALLELISM = false (to resolve warning from HuggingFace transformers and their use in spaCy)

In addition, the dna.config file in the dna/resources directory should be updated to supply your Stardog username/password and GeoNames user name.

To run the application, cd to the dna directory and execute python3 app.py.
