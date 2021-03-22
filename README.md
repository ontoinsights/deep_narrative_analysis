# Deep Narrative Analysis (DNA)

## License
Creative Commons 
Atribution 4.0 International 
CC BY 4.0

## Overview 

Deep Narrative Analysis (DNA) is a toolset for analyzing narratives. It combines semantic and natural language technologies with machine learning to 1) create knowledge graphs encoding the details of the narratives, 2) create knowledge graphs encoding background/contextual knowledge from online and structured data sources, and 3) perform inference, reasoning and statistical analyses. 

## File Structure

The semantics (ontologies) and processing (initially, Jupyter notebooks) are captured in the directories of this project. The following folder structure is used:

* _ontologies_ holds the definitions of the concepts and relationships that will be extracted from the narratives and online/structured data
  * All of the posted ontology files are written in Turtle (OWL2) and have been updated to align with March 2021 redesign
  * In addition, a Protege-ready merge of all the component files is available in the file, dna-ontology.ttl, in the top-level directory
* _ontol-docs_ contains documentation explaining the ontologies and their usage
  * The _graphs_ sub-directory contains PNGs of the main ontology concepts
  * The file, dna-ontology-tree.html, holds a searchable tree view of the complete set of concepts and relationships
* _notebooks_ holds the Jupyter notebooks used to scrape/parse web pages, and perform initial parsing and analysis experiments on the narratives
  * Note that various .config files are also defined to customize the processing (and should be modified if used in your personal environments)
* _tools_ contains scripts used to generate the DNA ontology artifacts (the Protege-ready merge and tree output)
  * The create_merged_ontol_and_tree script uses a branched version of the robot.jar from the OBO ROBOT GitHub repository (https://github.com/ontodev/robot/tree/tree-view)
