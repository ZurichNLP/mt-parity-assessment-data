#!/usr/bin/env python3

"""Combines experimental items in `items.csv` with results
stored in `results/documents` and `results/sentences`.

Output is written to STDOUT as CSV.
"""

import sys
import csv
import glob
from collections import defaultdict
from argparse import ArgumentParser, FileType


VALID_RATINGS = ['A', 'B', 'X']
FIELDNAME = {
    'm': 'fluency',
    'b': 'adequacy',
}


def read_ratings(ratings_file):
    ratings = [] # (file_id, task_order, condition_st, rating)
    with open(ratings_file) as rf:
        for r in csv.DictReader(rf):
            file_id, file_order = r['ID'].split('-')
            condition_st, file_id, level = file_id[0], file_id[1:], file_id[2]
            rating = r['Judgement']
            ratings.append((file_id, file_order, condition_st, rating))
    return ratings


def add_results(items, results_folder):
    for ratings_file in glob.glob(results_folder + '*.csv'):
        for file_id, file_order, condition_st, rating in read_ratings(ratings_file):
            item = items[file_id][file_order]
            origin = item[rating  + '_origin'] if rating != 'X' else 'tie'
            field = FIELDNAME[condition_st] + '_rater'
            field = field + '1' if field + '1' not in item else field + '2'
            item[field] = origin
        

parser = ArgumentParser(description='Combines experimental items with results.')
parser.add_argument('--items', type=FileType('r'), required=False, default='items.csv',
                    help='The original items.')
parser.add_argument('--sents', type=str, required=False, default='results/sentences/',
                    help='Folder containing stentence-level results.')
parser.add_argument('--docs', type=str, required=False, default='results/documents/',
                    help='Folder containing document-level results.')
args = parser.parse_args()

# read experimental items into memory
items = defaultdict(dict) # task_id => task_order => item (entire csv row)
for item in csv.DictReader(args.items):
    items[item['file_id']][item['file_order']] = item

# add sentence-level results
add_results(items, args.sents)

# add document-level results
add_results(items, args.docs)

# write results
fieldnames = [
    'file_id', 'file_order', 'task_id', 'task_order', 'wmt_article', 'wmt_line', 'level',
    FIELDNAME['m'] + '_rater1', FIELDNAME['m'] + '_rater2', 
    FIELDNAME['b'] + '_rater1', FIELDNAME['b'] + '_rater2', 
    'A_origin', 'B_origin', 'src', 'A', 'B',
]
writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
writer.writeheader()
for _, the_items in items.items():
    for _, item in the_items.items():
        item['level'] = 'sentence' if item['file_id'].endswith('s') else 'document'
        writer.writerow(item)



