#!/bin/bash
ls ./Data
read -p "Choose one of the above input dir: " path
echo "Copy input files.."
cp -v ./Data/$path/* ./input/
echo "Done!"

echo "Launching coreNLP server..."
cd ./stanford-corenlp-full*
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
