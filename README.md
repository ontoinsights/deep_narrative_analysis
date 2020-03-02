# Deep Narrative Analysis (DNA)

## Overview 

Deep Narrative Analysis (DNA) is a toolset for analyzing narratives. It combines semantic and Python technologies with machine learning to 1) create knowledge graphs encoding the details of the narratives, 2) create knowledge graphs encoding background/contextual knowledge from online and structured data sources, and 3) perform inference, reasoning and statistical analyses. 

## File Structure

The semantics (ontologies) and processing (initially, Jupyter notebooks) are captured in the directories of this project. The following folder structure is used:

* _ontologies_ holds the definitions of the concepts that will be extracted from the narratives and online/structured data, and encoded as knowledge graphs
* _ontol-docs_ contains documentation explaining the ontologies and their usage
  * The _graphs_ sub-directory contains PNGs of the main ontology concepts
* _narrative-parse_ holds the notebooks used to scrape/parse the web pages, and parse/analyze the narratives
  * Note that various .config files are also defined to customize the processing
