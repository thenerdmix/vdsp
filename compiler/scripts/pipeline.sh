#!/bin/sh

cd ..
python3 scripts/random-graph-to-tree.py
wait
cd ../First\ Passage
./tree ../compiler/tree.json
wait
python3 get_F.py