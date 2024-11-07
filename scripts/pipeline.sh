#!/bin/sh

cd ../trees
rm -rf *
cd ..
python3 scripts/random-graph-to-tree.py
wait
cd ../First\ Passage
for file in ../compiler/trees/*; do 
    if [ -f "$file" ]; then
        echo "$file"
        ./tree "$file" 
        wait
        python3 get_F.py
    fi 
done