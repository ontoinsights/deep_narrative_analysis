# Deep Narrative Analysis (DNA)
Updated 12 November 2022

## License
Creative Commons 

Attribution 4.0 International 

CC BY 4.0

## Overview 

Deep Narrative Analysis (DNA) is a toolset for analyzing narratives (biographical/autobiographical text, news articles, posts in Facebook and public online forums, etc.). It combines semantic, ontological and natural language technologies with machine learning to 1) create knowledge graphs encoding the details of the narratives and any background/contextual knowledge from online and structured data sources, and 2) perform inference, reasoning and statistical and network analyses. 

For more detailed information on DNA, see the paper, [_Translating Narratives to Knowledge Graphs_](./Translating%20Narratives%20to%20Knowledge%20Graphs.pdf).

## File Structure

The semantics (ontologies) and processing are captured in the directories of this project. The following folder structure is used:

* _dna_ contains the (evolving) Deep Narrative Analysis application
  * The import structure of the DNA Python modules is visualized at https://github.com/ontoinsights/deep_narrative_analysis/blob/master/python_modules_overview.png
  * The _dna/resources_ dirctory contains background data, WordNet lexical details, etc. in pickle and text files
* _tests_ holds pytest validation code for the dna RESTful services and underlying processing
  * This code is NOT executed when pushing new code (as part of a GitHub workflow) since a Stardog server would have to be deployed 
  * However, the code is run locally and the htmlcov subdirectory is included with the results
* _ontologies_ holds the definitions of the concepts and relationships that are extracted from the narratives and background data
  * All the posted ontology files are written in Turtle (OWL2)
  * In addition, a Protege-ready merge of the ontology files (dna-ontology.ttl) is available in the top-level directory
* _ontol-docs_ contains documentation explaining the DNA ontologies and their usage
  * The _graphs_ subdirectory contains PNGs of the ontology concepts, where the graph local names correspond to the Turtle file modules' local names
  * The file, dna-ontology-tree.html, holds a searchable tree view of the generic concepts and relationships
* _tools_ contains scripts used to generate the DNA ontology artifacts (the Protege-ready merge and tree output)
  * The create_merged_ontol_and_tree script uses a branched version of the robot.jar from the OBO ROBOT GitHub repository (https://github.com/ontodev/robot/tree/tree-view)
* _notebooks_ holds the Jupyter notebooks used to scrape/parse web pages, create necessary pickle files for processing, perform initial parsing and analysis experiments on the narratives, etc.
* _yaml_ contains a file with the DNA Repositories RESTful API definintions
  * The APIs are also viewable, in a more human-friendly manner, at https://ontoinsights.github.io/dna-swagger/

The original, "proof-of-concept" DNA codebase was _archived with the tag, v0.1.0-poc_, in July 2022. The code is refactored to improve the parse of news articles, and enable more automated NL and ML analyses. A majority of the _dna_ python files are removed, as well as the domain-specific ontologies, in order to move to a new set of RESTful APIs and processing flow. 

## Environment and Execution

Necessary libraries are specified in the _requirements.txt_ file in the main directory. Please download all the libraries, create the default databases in Stardog AND set the environment variables BEFORE doing any testing.

After downloading the required libraries, the following must also be installed:

* Stardog triple store, downloadable from https://www.stardog.com/get-started/
  * Make sure to have added Stardog's installation location to your PATH environment variable
  * After installation, the database, "ontologies", should be created with the files from the _ontologies_ directory 
    * The following command line instruction (executed from DNA's _ontologies_ directory) will create the database: `stardog-admin db create -n ontologies *.ttl` 
  * Also, the empty database, "meta-db", should be created (from any directory, execute `stardog-admin db create -n meta-dna` )
* spaCy transformer language model 
  * Accomplished by executing "python3 -m spacy download en_core_web_trf"
  
Make sure that you always upgrade the spacy model ("en_core_web_trf") when upgrading spacy itself. Also, when updating the model, if you run into the error, "cannot import name 'get_terminal_size' from 'click.termui'", make sure that you have upgraded the _typer_ package to the latest version (at least >= 0.4.1). 

Lastly, these environment variables need to be set for the DNA application:

* `PATH` needs to specifically include the GitHub project's dna directory (for testing)
* `TOKENIZERS_PARALLELISM = false` (to resolve warning from HuggingFace transformers and their use in spaCy)
* `STARDOG_ENDPOINT`, `STARDOG_USER`, `STARDOG_PASSWORD` MUST be set 
* GEONAMES_ID MUST be set if using 'external sources' for additional information (as specified by the DNA RESTful API, dna/v1/repositories/narratives POST)

To run the DNA services, cd to the _dna_ directory and execute "flask run". The RESTful DNA APIs will be accessible at http://127.0.0.1:5000/dna/v1/repositories (local only).

## Multilingual Support

DNA is designated to extend to languages beyond English, although English is the only language that has been tested to-date. The underlying language resources (spaCy, WordNet, etc.) support a variety of languages. Currently, both the Finnish and German languages are being investigated.

To this end, the following details are relevant for multi-lingual research:

* To update the spaCy language model, download spaCy's '-trf' (if available) or '-lg' models for the desired language and update the model reference in nlp.py (line 59)
* Translate the prepositions, days/months, etc. English strings in the utilities_and_language_specific.py file
* Pronouns are also directly referenced in the coreference_resolution.py code (see the function, _check_pronouns)
* Verify that the WordNet synonyms referenced in the _ontologies_ (.ttl) files are also used in the WordNet reference for the desired language
  * If so, the language-specific noun and verb synonyms can be pulled and directly inserted into the ontology files
  * If not, a manual + programmatic/translation mapping from the language-specific synsets to the DNA ontology concepts will be required
* DNA sentiment analysis (in the create_narrative_turtle.py file) uses NLTK's VADER (https://www.nltk.org/howto/sentiment.html), which is English only
  * This library was chosen since it is accurate for short texts and runs on all platforms
  * PolyGlot was assessed but had library compatibility issues when running on Mac platforms (OntoInsights' current development environment)
    * Resolving these issues is a future work-item
* The test details in the _tests_ directory should be modified for the desired language
