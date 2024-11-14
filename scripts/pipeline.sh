#!/bin/sh

cd ../trees
rm -rf *
cd ../proc_order
rm -rf *
cd ..
python3 scripts/compare_trees.py
wait
cd First\ Passage
for file in ../trees/*; do 
    if [ -f "$file" ]; then
        echo $(basename ${file})
        cp "$file" inp.json
        cp "../proc_order/$(basename ${file})" proc_order.json
        ./tree 
        wait
        python3 get_F.py "$file"
    fi 
done