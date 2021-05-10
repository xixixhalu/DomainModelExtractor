#!/bin/bash

misspelling_cmd='python3 misspelling.py '
preprocessing_cmd='python3 preprocessing.py '
ssr_matching_cmd='python3 ssr_matching.py '
rule_transforming_cmd='python3 rule_transforming.py '
visualizing_cmd='python3 visualizing.py '

usage() { 
	echo "Usage:	$0 [-m|-p|-s|-t|-v] [-f <filename>]" 1>&2;
	echo "Parameters:	
	-m 	Misspelling detection
	-p 	Preprosessing
	-s 	SSR matching
	-t 	Rule transformation
	-v 	Visualization
	-f 	Specify a project file. Default: all project files"
	echo "Example:
	sh run.sh -mpstv
	sh run.sh -mpstv -f 2014-USC-Project02
	sh run.sh [-m|-p|-s|-t|-v]
	sh run.sh [-m|-p|-s|-t|-v] -f 2014-USC-Project02"
	exit 1; 
}

misspell_detect() {
	files=$1
	for f in "${files[@]}"
	do
		echo "misspelling detecting $f..."
		eval $misspelling_cmd"-f "$f
	done
}

preprocess() {
	files=$1
	for f in "${files[@]}"
	do
		echo "Pre-processing $f..."
		eval $preprocessing_cmd"-f "$f
	done
}

ssr_match() {
	files=$1
	for f in "${files[@]}"
	do
		echo "SSR matching $f..."
		eval $ssr_matching_cmd"-f "$f
	done
}

rule_transform() {
	files=$1
	for f in "${files[@]}"
	do
		echo "Rule transforming $f..."
		eval $rule_transforming_cmd"-f "$f
	done
}

visualize() {
	files=$1
	for f in "${files[@]}"
	do
		echo "Visualizing $f..."
		eval $visualizing_cmd"-f "$f
	done
}

while getopts mpstvf: o; do
  case $o in
    (m) 
		MISSPELL_DETECTION=true
		;;
    (p) 
		PREPROCESSING=true
		;;
    (s) 
		SSR_MATCHING=true
		;;
	(t) 
		RULE_TRANSFORMING=true
		;;
	(v) 
		VISUALIZING=true
		;;
    (f) 
		file=$OPTARG
		;;
    (*) 
		usage
  esac
done
shift "$((OPTIND - 1))"

###

if [ -z "${MISSPELL_DETECTION}" ] && [ -z "${PREPROCESSING}" ] && [ -z "${SSR_MATCHING}" ] && [ -z "${RULE_TRANSFORMING}" ] && [ -z "${VISUALIZING}" ]; then
    usage
fi

if [[ "$MISSPELL_DETECTION" = true ]]; then
	if [ -z "${file}" ]; then
 		files=($(eval $misspelling_cmd"-l"))
 	else
 		files=($file)
 	fi
	misspell_detect $files
fi

if [[ "$PREPROCESSING" = true ]]; then
	if [ -z "${file}" ]; then
 		files=($(eval $preprocessing_cmd"-l"))
 	else
 		files=($file)
 	fi
	preprocess $files
fi

if [[ "$SSR_MATCHING" = true ]]; then
	if [ -z "${file}" ]; then
 		files=($(eval $ssr_matching_cmd"-l"))
 	else
 		files=($file)
 	fi
	ssr_match $files
fi

if [[ "$RULE_TRANSFORMING" = true ]]; then
	if [ -z "${file}" ]; then
 		files=($(eval $rule_transforming_cmd"-l"))
 	else
 		files=($file)
 	fi
	rule_transform $files
fi

if [[ "$VISUALIZING" = true ]]; then
	if [ -z "${file}" ]; then
 		files=($(eval $visualizing_cmd"-l"))
 	else
 		files=($file)
 	fi
	visualize $files
fi
