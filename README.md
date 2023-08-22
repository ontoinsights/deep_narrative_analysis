# Deep Narrative Analysis (DNA)
Updated 22 August 2023

## License
Creative Commons 

Attribution 4.0 International 

CC BY 4.0

## Overview 

Deep Narrative Analysis (DNA) is a toolset for analyzing narratives (biographical/autobiographical text, news articles, posts in Facebook and public online forums, etc.). It combines semantic, ontological and natural language technologies with AI/machine learning to 1) create knowledge graphs encoding the details of the narratives and any background/contextual knowledge from online and structured data sources, and 2) perform inference, reasoning and statistical and network analyses. 

For more detailed information on DNA, see the paper, [_Translating Narratives to Knowledge Graphs_](./Translating%20Narratives%20to%20Knowledge%20Graphs.pdf).

To view the DNA ontology, see the [dna-ontologies web page](https://ontoinsights.github.io/dna-ontologies/).

## File Structure

The semantics (ontologies) and processing are captured in the directories of this project. The following folder structure is used:

* _dna_ contains the (evolving) Deep Narrative Analysis application
  * The import structure of the DNA Python modules is visualized at https://github.com/ontoinsights/deep_narrative_analysis/blob/master/python_modules_overview.png
  * The _dna/resources_ dirctory contains background data, WordNet lexical details, etc. in pickle and text files
* _tests_ holds pytest validation code for the dna RESTful services and underlying processing
  * This code is NOT executed when pushing new code (as part of a GitHub workflow) since a Stardog server would have to be deployed 
  * However, the code is run locally and the htmlcov subdirectory is included with the results
  * To see code coverage data, open the index.html in tests/htmlcov
* _ontologies_ holds the definitions of the concepts and relationships that are extracted from the narratives and background data
  * All the posted ontology files are written in Turtle (OWL2)
  * In addition, a Protege-ready merge of the ontology files (dna-ontology.ttl) is available in the top-level directory
  * A human-friendly, searchable tree view is available at https://ontoinsights.github.io/dna-ontologies/
  * Note that there is a 'cameo' sub-directory, holding the CAMEO ethnicity and religion details which have been superceded by the Wikidata information
  * Note also that there is a 'synonyms' directory holding many possible synonyms for the concepts (which has been superceded by the use of ChatGPT)
* _ontol-docs_ contains documentation explaining the DNA ontologies and their usage
  * The _graphs_ subdirectory contains PNGs of the ontology concepts, where the graph local names correspond to the Turtle file modules' local names
  * The file, dna-ontology-tree.html, holds a downloadable version of the searchable tree view
* _tools_ contains scripts used to generate the DNA ontology artifacts (the Protege-ready merge and tree output)
  * The create_merged_ontol_and_tree script uses a branched version of the robot.jar from the OBO ROBOT GitHub repository (https://github.com/ontodev/robot/tree/tree-view)
* _notebooks_ holds the Jupyter notebooks used to scrape/parse web pages, perform input and analysis experiments on the narratives, etc.
* _yaml_ contains a file with the DNA Repositories RESTful API definintions
  * The APIs are also viewable, in a more human-friendly manner, at https://ontoinsights.github.io/dna-swagger/

The original, "proof-of-concept" DNA codebase (based on analyzing Holocaust narratives) was _archived with the tag, v0.1.0-poc_, in July 2022. The second version (using WordNet to include synonyms and do multi-language processing) was _archived with the tag, v0.5.0-preChat, in March 2023. The current code is being refactored to obtain news articles using an API, better capture semantics using ChatGPT, and enable more automated NL and ML analyses. In addition, the ontologies have been updated to remove synonym text, although the WordNet synset ids are still included.

## Environment and Execution

DNA has been developed and tested in a Python 3.11 environment.

Necessary libraries are specified in the _requirements.txt_ file in the main directory. Please download (e.g. via pip install) all the requirements, and follow the remainder of the instructions in this section to get other, necessary components. (Note that you may need to update Xcode on Mac, install a Rust compiler, etc., if errors occur while doing the pip installs. If errors are reported, pip typically explains how to address them.) Lastly, set the environment variables AND download other components (such as Stardog) BEFORE starting the DNA application or doing any testing.

These environment variables need to be set for the DNA application:

* `PATH` needs to specifically include the GitHub project's dna directory (for ease of testing) and the Stardog install location
* `STARDOG_ENDPOINT`, `STARDOG_USER`, `STARDOG_PASSWORD` MUST be set (regarding the endpoint for HTTP access, typically http://localhost:5820, and a valid user name/password, admin/admin by default)
* Stardog execution details:
  * `STARDOG_HOME` should be set to the directory where the data and logs will be stored, as well as where the Stardog license key is available
    * This is typically NOT the install location for the executable binaries since the latter will be updated as the Stardog product evolves
  * `JAVA_HOME` should be defined (the OntoInsights development environment is using OpenJDK for Java 3.11) 
    * Stardog executes in a Java environment - hence, the requirement
    * JAVA_HOME is typically set to `$(/usr/libexec/java_home)`
  * `STARDOG_SERVER_JAVA_ARGS` should be configured for your development environment (for example, "-Xms14g -Xmx14g -XX:MaxDirectMemorySize=28g")
* `GEONAMES_ID` MUST be set if using 'external sources' for additional information (as specified by the DNA RESTful API, dna/v1/repositories/narratives POST)

Other components that must be installed are:

* Stardog triple store, downloadable from https://www.stardog.com/get-started/
  * Make sure to have added Stardog's bin directory location to your PATH environment variable
  * As regards the Stardog configuration (specified in a stardog.properties file found in the STARDOG_HOME directory), the following settings are used as DNA 'defaults':
    * spatial.enabled=true
    * spatial.use.jts=true
    * edge.properties=true
    * query.all.graphs=false
    * query.timeout=10m
    * virtual.transparency=false
    * preserve.bnode.ids=false
    * reasoning.punning.enabled=true 
  * To start Stardog for localhost access, execute the command, `stardog_admin server start --bind 127.0.0.1`
  * After starting Stardog, the database, "ontologies", should be created with the files from DNA _ontologies_ 
    * To do so, execute the command `stardog-admin db create -n ontologies *.ttl` from DNA's _ontologies_ directory 
  * Also, the empty database, "meta-dna", should be created (from any directory, execute `stardog-admin db create -n meta-dna`)
* spaCy transformer language model 
  * Accomplished by executing "python3 -m spacy download en_core_web_trf"

Make sure that you always upgrade the spacy model ("en_core_web_trf") when upgrading spacy itself. Also, when updating the model, if you run into the error, "cannot import name 'get_terminal_size' from 'click.termui'", make sure that you have upgraded the _typer_ package to the latest version (at least >= 0.4.1). 

Lastly, to run the DNA services, cd to the _dna_ directory and execute "flask run". The RESTful DNA APIs will be accessible at http://127.0.0.1:5000/dna/v1/repositories (local only).

## Multilingual Support

DNA is designated to extend to languages beyond English, although English is the only language that has been tested to-date. To directly parse a non-English language, the underlying language resources (spaCy, ChatGPT, etc.) are usable, as they are designed to support a variety of languages.

To this end, the following details are relevant for multi-lingual/non-English research with DNA. The following steps should be performed:

* Update the spaCy language model by downloading spaCy's '-trf' (if available) or '-lg' models for the desired language and updating the model reference in nlp.py (line 62)
* Modify the SPARQL language tag (for example, '@en') used for Stardog and external queries in the utilities_and_language_specific.py file, line 12
* Translate the prepositions, days/months, etc. (defined using English strings) in the utilities_and_language_specific.py file to their language-equivalent terms
* Update the pronouns that are directly referenced in the coreference_resolution.py module (see the function, _check_pronouns) to their language-equivalent terms
* Update the prepositions ('after' in create_labels.py and 'to' in create_verb_turtle.py) and modals (in nlp_sentence_dictionary.py) that are directly searched for and used in the processing; They should be updated to their language-equivalent terms
  * The references to be updated are noted by 'TODO' comments
* Account for multi-lingual access to external services (Wikipedia, Wikidata, GeoNames, ... in query_sources.py), coding for specific language search and results
* Update the text details (texts to be ingested and results that are expected) in each of the test*.py files (in the _tests_ directory) to the desired language
