# DomainModelExtractor

Extract Domain information from User Stories

# Features (Proposed)

- Analyze TDs and Pos-tags via Stanford coreNLP.
- Extract Enities&Relationship from inputs
- Construct UML Class
- Generate viewable UML diagram

# Quick Start

## Environment

- Ubuntu 14.04 64bit / MacOS
- Python 2.7

## Setup

- Clone this project to your local

- Download Stanford coreNLP package from [HERE](http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip); UNZIP and COPY it to the dir of `DomainModelExtractor`
  - More detail at [https://stanfordnlp.github.io/CoreNLP/](https://stanfordnlp.github.io/CoreNLP/)
  
- Initialize and install the required the packages
```shell
sh install.sh
```

## For development and testing

- Launch NLP server
```shell
sh launch_server.sh
```

- Testing the connection
```python
python test/test_coreNLP.py
```



