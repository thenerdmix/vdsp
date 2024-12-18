#!/bin/sh

cd ../trees/compare-trees-pipeline
rm -rf *
cd ../../proc_order
rm -rf *
cd ..
python3 scripts/compare_trees.py
wait
cd First\ Passage
for file in ../trees/compare-trees-pipeline/*; do 
    if [ -f "$file" ]; then
        echo $(basename ${file})
        cp "$file" inp.json
        cp "../proc_order/$(basename ${file})" proc_order.json
        ./tree 
        wait
        python3 get_F.py "$file"
    fi 
done