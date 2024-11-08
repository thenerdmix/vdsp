#!/bin/sh

cd ../trees
rm -rf *
cd ..
python3 scripts/compare_trees.py
wait
cd First\ Passage
for file in ../trees/*; do 
    if [ -f "$file" ]; then
        echo "$file"
        cp "$file" inp.json
        ./tree 
        wait
        python3 get_F.py "$file"
    fi 
done