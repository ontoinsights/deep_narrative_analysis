# Deep Narrative Analysis (DNA)
Updated 4 November 2023

## License
Creative Commons 

Attribution 4.0 International 

CC BY 4.0

## Overview 

Deep Narrative Analysis (DNA) is a toolset for analyzing narratives (biographical/autobiographical text, news articles, posts in Facebook and public online forums, etc.). Currently, it is focused on analyzing news articles to aid readers of news (in understanding how the reporting is "tuned") and to investigate/discover potential mis- and dis-information “flags” across texts. DNA combines semantic, ontological, and natural language and AI/ML technologies to 1) create knowledge graphs encoding the details of the news articles with background/contextual knowledge from online and structured data sources, and 2) perform inference, reasoning and statistical and network analyses. 

For more detailed information on DNA, see the present, [_Populating Knowledge Graphs_](./Populating%20KGs.pdf).

To view the DNA ontology, see the [dna-ontologies web page](https://ontoinsights.github.io/dna-ontologies/).

## File Structure

The semantics (ontologies) and processing are captured in the directories of this project. The following folder structure is used:

* _dna_ contains the (evolving) Deep Narrative Analysis application
  * At present, only the article ingest and processing, and KG creation portions are open-sourced in this repository
  * The import structure of the DNA Python modules is visualized at https://github.com/ontoinsights/deep_narrative_analysis/blob/master/python_modules_overview.png
  * The _dna/resources_ dirctory contains background data in pickle and text files
* _tests_ holds pytest validation code for the DNA RESTful services and underlying processing
  * This code is NOT executed when pushing new code (as part of a GitHub workflow) - but will be tested in the future, since a Stardog Cloud instance can be used
  * At present, the code is run locally and the htmlcov subdirectory is updated with the results
    * To see code coverage data, open the index.html in tests/htmlcov
* _ontologies_ holds the definitions of the concepts and relationships that are extracted from the narratives and background data
  * All the posted ontology files are written in Turtle (OWL2)
  * In addition, a Protege-ready merge of the ontology files (dna-ontology.ttl) is available in the top-level directory
  * A human-friendly, searchable tree view is available at https://ontoinsights.github.io/dna-ontologies/
  * Note that there is a 'archive' sub-directory, holding WordNet synonym and emotion, ethnicity and religion details which have been superceded by the use of Wikidata information 
  * Note also that there is a 'synonyms' directory that was used in a previous version of DNA, before the move to using LLMs for this purpose
* _ontol-docs_ contains documentation explaining the DNA ontologies and their usage
  * The _graphs_ subdirectory contains PNGs of the ontology concepts, where the graph local names correspond to the Turtle file modules' local names
  * The file, dna-ontology-tree.html, holds a downloadable version of the searchable tree view
* _papers-presentations_ contains documentation related to what has been publicly presented
* _tools_ contains scripts used to generate the DNA ontology artifacts (the Protege-ready merge and tree output)
  * The create_merged_ontol_and_tree script uses a branched version of the robot.jar from the OBO ROBOT GitHub repository (https://github.com/ontodev/robot/tree/tree-view)
* _notebooks_ holds the Jupyter notebooks used to scrape/parse web pages, perform input and analysis experiments on the narratives, etc.
  * Subdirectories store aspects of previous experimentation
* _yaml_ contains a file with the DNA Repositories RESTful API definintions
  * The APIs are also viewable, in a more human-friendly manner, at https://ontoinsights.github.io/dna-swagger/

The original, "proof-of-concept" DNA codebase (based on analyzing Holocaust narratives) was _archived with the tag, v0.1.0-poc_, in July 2022. The second version (using WordNet to include synonyms and do multi-language processing) was _archived with the tag, v0.5.0-preChat, in March 2023. The current code is refactored to obtain news articles using the news.org API, better capture semantics using OpenAI APIs, and enable more automated NL and ML analyses. In addition, the ontologies have been simplified and updated. Note that the ontology definitions still include WordNet noun and verb synset ids.

## Environment and Execution

DNA has been developed and tested in a Python 3.11 environment.

Necessary libraries are specified in the _requirements.txt_ file in the main directory. Please download (e.g. via pip install) all the requirements, and follow the remainder of the instructions in this section to get other, necessary components. (Note that you may need to update Xcode on Mac, install a Rust compiler, etc., if errors occur while doing the pip installs. If errors are reported, pip typically explains how to address them.) Lastly, set the environment variables  BEFORE starting the DNA application or doing any testing.

These environment variables need to be set for the DNA application:

* `PATH` needs to specifically include the GitHub project's dna directory (for ease of testing) 
* `OPENAI_API_KEY`(openai.com) MUST be set and reference a billable account 
* `STARDOG_ENDPOINT`, `STARDOG_USER`, `STARDOG_PASSWORD` MUST be set (where STARDOG_ENDPOINT is the address of a Stardog Cloud instance - usage of the free tier is acceptable)
* `GEONAMES_ID` (geonames.org) MUST be set for background information retrieval
* `NEWS_API_KEY` (newsapi.org) MUST be set if the dna/v1/news API is used

Other components that must be installed or set up are:

* spaCy language model 
  * Accomplished by executing "python3 -m spacy download en_core_web_trf"
* Stardog Cloud
  * The database, "ontologies", should be created and the files from the DNA _ontologies_ directory uploaded to it
    * Do not load any of the files in the sub-directories. They are provided for reference.
    * As regards the database configuration, the following settings should be used as DNA 'defaults':
      * edge.properties=true
      * query.all.graphs=false
      * query.timeout=5m
      * preserve.bnode.ids=false
      * reasoning.punning.enabled=true
  * Also, the empty database, "meta-dna", should be created

Make sure that you always upgrade the spacy model ("en_core_web_trf") when upgrading spacy itself. Also, when updating the model, if you run into the error, "cannot import name 'get_terminal_size' from 'click.termui'", make sure that you have upgraded the _typer_ package to the latest version (at least >= 0.4.1). 

Lastly, to run the DNA services, cd to the _dna_ directory and execute "flask run". The RESTful DNA APIs will be accessible at http://127.0.0.1:5000/dna/v1/repositories (local only).

## Multilingual Support

Only the English language is currently supported and tested. Support for multi-lingual text would be possible using a translation tool or an LLM to create the English rendering.

This is an area which should be further researched.
