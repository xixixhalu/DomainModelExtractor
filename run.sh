#!/bin/bash

misspell_detect() {
	files=($(python3 misspelling.py -l))

	for f in "${files[@]}"
	do
		echo "Processing $f..."
		python3 misspelling.py -f $f
	done
}

for arg in "$@"; do
  if [[ "$arg" = -m ]] || [[ "$arg" = --misspell ]]; then
    MISSPELL_DETECTION=true
  fi
done

###

if [[ "$MISSPELL_DETECTION" = true ]]; then
  misspell_detect
fi