#!/bin/bash
# Script to create logxontology artifacts

cd ../ontologies
java -jar ../tools/robot.jar merge --inputs "*.ttl" --output ../dna-ontology.ttl
java -jar ../tools/robot.jar annotate --input ../dna-ontology.ttl --ontology-iri "urn:ontoinsights:ontology:dna" --output ../annotated-ontology.ttl
java -jar ../tools/robot.jar tree --input ../annotated-ontology.ttl --tree ../ontol-docs/dna-ontology-tree.html
rm ../annotated-ontology.ttl
