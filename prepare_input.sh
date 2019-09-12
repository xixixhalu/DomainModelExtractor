#!/bin/bash

ls ./Data
read -p "Choose one of the above input dir: " path
echo "Copy input files.."
cp -v ./Data/$path/* ./input/
echo "Done!"
