#! /bin/bash

# Runs the main.py on all the files in the inputs folder
# Then writes the reuslts to the results folder

mkdir -p results

for file in inputs/*.json
do
    echo "Running $file"
    python3 main.py < $file 1> results/$(basename $file)
done
