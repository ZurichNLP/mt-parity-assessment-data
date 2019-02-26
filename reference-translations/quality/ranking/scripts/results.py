#!/usr/bin/env python3

import csv
from collections import defaultdict
from argparse import ArgumentParser, FileType


VALID_RATINGS = ['A', 'B', 'X']


parser = ArgumentParser(description='Aggregates ratings from a results file.'
                                    'Also checks spam items.')
parser.add_argument('items', type=FileType('r'), help='The original items (`items.csv`).')
parser.add_argument('ratings', type=FileType('r'), help='The ratings (CSV).')

args = parser.parse_args()


# read rater's ratings
ratings = defaultdict(dict) # task_id => task_order => rating
for r in csv.DictReader(args.ratings):
    file_id, task_order = r['ID'].split('-')
    condition_st, file_id, level = file_id[0], file_id[1:], file_id[2]
    rating = r['Judgement']
    ratings[file_id][task_order] = rating

# evaluate ratings
results = defaultdict(lambda: defaultdict(int))
results_spam = []
for item in csv.DictReader(args.items):
    if item['file_id'] in ratings:
        is_spam = 'spam' in [item['A_origin'], item['B_origin']]
        rating = ratings[item['file_id']][item['file_order']]
        origin = item[rating  + '_origin'] if rating != 'X' else 'tie'
        if is_spam:
            segment_id = item['file_id'] + '-' + item['file_order']
            results_spam.append(segment_id if origin == 'spam' else False)
        if not is_spam:
            results[item['task_id']][origin] += 1

print("{0} {1} ratings for:".format('Monolingual' if condition_st == 'm' else 'Bilingual',
                                'document-level' if level == 'd' else 'sentence-level'))

for task_id, ratings in results.items():
    print("\ntask `{0}`:".format(task_id))
    total = 0
    for origin, count in ratings.items():
        print("\t{0}\t{1}".format(count, origin))
        total += count
    print("\t--")
    print("\t{0}\ttotal".format(total))

missed_spam = sum([1 for r in results_spam if r != False])
print("\nMissed spam: {0}/{1}".format(missed_spam, len(results_spam)))
if missed_spam > 0:
    print("Missed spam item ids: {0}".format(', '.join([i for i in results_spam if i])))
