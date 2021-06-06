# DomainModelExtractor

Extract Domain information from User Stories

# Features (Proposed)

- Analyze TDs and Pos-tags.
- Extract Enities, Attributes, Behaviors, Relationship from inputs
- Construct UML Class
- Generate viewable UML diagram

# Quick Start

## Environment

- Ubuntu 14.04 64bit / MacOS
- Python 3.8

## Setup

- Clone this project to your local

- Download Stanford coreNLP package from [HERE](http://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-05.zip); COPY and UNZIP it to the dir of `DomainModelExtractor`
  - More detail at [https://stanfordnlp.github.io/CoreNLP/](https://stanfordnlp.github.io/CoreNLP/)
  - How to setup and use Stanford CoreNLP Server with Python [https://www.khalidalnajjar.com/setup-use-stanford-corenlp-server-python/](https://www.khalidalnajjar.com/setup-use-stanford-corenlp-server-python/)
  
- Initialize and install the required the packages
```shell
sh install.sh
```

## For development and testing

- Launch NLP server on terminal A
```shell
sh launch_server.sh
```

- Testing the connection on ternimal B
```python
python test/test_coreNLP.py
```
```diff
+ Now the working environment is fully setup!
```

## Featured Commands

```shell
Usage:	run.sh [-m|-p|-s|-t|-v] [-f <filename>]
Parameters:
	-m 	Misspelling detection
	-p 	Preprosessing
	-s 	SSR matching
	-t 	Rule transformation
	-v 	Visualization
	-f 	Specify a project file. Default: all project files
Example:
	sh run.sh -mpstv
	sh run.sh -mpstv -f 2014-USC-Project02
	sh run.sh [-m|-p|-s|-t|-v]
	sh run.sh [-m|-p|-s|-t|-v] -f 2014-USC-Project02
```

