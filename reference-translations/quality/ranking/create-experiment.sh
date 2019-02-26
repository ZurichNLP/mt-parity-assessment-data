#!/usr/bin/env bash

mkdir -p output/html

./scripts/combine_data.py \
  input/newstest2017-zhen-src.zh.sgm \
  input/microsoft-mt-combo6.txt \
  input/microsoft-ht.txt \
  input/graham-ht.csv \
  > data.csv

./scripts/create_experiment.py data.csv > items.csv

./scripts/create_html.py items.csv -d output/html
