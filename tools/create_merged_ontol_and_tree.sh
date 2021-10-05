#!/bin/bash
# Script to create logxontology artifacts

cd ../ontologies
java -jar ../tools/robot.jar merge --inputs "*.ttl" --output ../dna-ontology.ttl
java -jar ../tools/robot.jar annotate --input ../dna-ontology.ttl --ontology-iri "urn:ontoinsights:dna" --output ../annotated-ontology.ttl
java -jar ../tools/robot.jar tree --input ../annotated-ontology.ttl --tree ../ontol-docs/dna-ontology-tree.html
rm ../annotated-ontology.ttl

cd ../ontologies/domain-specific
java -jar ../../tools/robot.jar merge --inputs "*.ttl" --output ../../domain-ontology.ttl
java -jar ../../tools/robot.jar annotate --input ../../domain-ontology.ttl --ontology-iri "urn:ontoinsights:dna" --output ../annotated-domain-ontology.ttl
java -jar ../../tools/robot.jar tree --input ../annotated-domain-ontology.ttl --tree ../../ontol-docs/domain-ontology-tree.html
rm ../annotated-domain-ontology.ttl
