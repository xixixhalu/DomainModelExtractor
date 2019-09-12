#!/bin/bash

echo "Launching coreNLP server..."
cd ./stanford-corenlp-full*
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
