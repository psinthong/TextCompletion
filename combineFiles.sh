#!/bin/bash

outf='./train_Set_1.txt'
for f in ./train_data/Combine/*; do
	cat $f >> ${outf}
done