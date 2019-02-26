#!/usr/bin/env python3

import sys
import csv
import random
import logging
from copy import deepcopy
from argparse import ArgumentParser, FileType
from collections import defaultdict


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

random.seed(80469)


def random_range(start, end):
    r = list(range(start, end))
    random.shuffle(r)
    return r


def make_spam(string):
    tokens = string.split()
    d = len(tokens)//10 # leave the first and last 10% of tokens untouched
    head = tokens[:d]
    tail = tokens[len(tokens)-d:]
    rest = tokens[d:len(tokens)-d]
    random.shuffle(rest) # shufle the remaining tokens randomly
    spam_tokens = head + rest + tail
    return ' '.join(spam_tokens)


def merge_sentences(sentences):
    """Merges all sentences of an article into one item of type article."""
    def merge(sents):
        return ' '.join(sents)
    return {
        'wmt_article': sentences[0]['wmt_article'],
        'wmt_line': '{0}:{1}'.format(sentences[0]['wmt_line'], sentences[-1]['wmt_line']),
        'wmt_article_name': sentences[0]['wmt_article_name'],
        'src': merge([s['src'] for s in sentences]),
        'mt': merge([s['mt'] for s in sentences]),
        'human_a': merge([s['human_a'] for s in sentences]),
        'human_b': merge([s['human_b'] for s in sentences]) if 'human_b' in sentences[0] else '',
    }


def create_experimental_item(item, ab_choices):
    assert len(ab_choices) == 2, "A/B test item must have exactly two choices."
    for choice in ab_choices:
        assert choice in item, "Unknown origin: " + choice
    exp_item = deepcopy(item)
    choices = [
        (exp_item[ab_choices[0]], ab_choices[0]),
        (exp_item[ab_choices[1]], ab_choices[1])
    ]
    random.shuffle(choices)
    exp_item['A'] = choices[0][0]
    exp_item['A_origin'] = choices[0][1]
    exp_item['B'] = choices[1][0]
    exp_item['B_origin'] = choices[1][1]
    return exp_item


def create_experimental_spam_item(article, level):
    if level == 's': # sentence
        item = random.choice(article) # chose a random sentence
    elif level == 'd': # document
        item = merge_sentences(article)
    item['spam'] = make_spam(item['mt'])
    ab_choices = ('human_a', 'spam')
    return create_experimental_item(item, ab_choices)


parser = ArgumentParser(description='Creates A/B rating tasks from output of'
                                    '`combine_data.py`.')
parser.add_argument('data', type=FileType('r'), help='The WMT 2018 ZH-EN data '
                                                     'with alternative '
                                                     'translations (output of '
                                                     '`combine_data.py`.)')
parser.add_argument('-d', '--documents', type=int, default=50,
                    help='Number of documents per rater.')
parser.add_argument('-ds', '--documents_spam', type=int, default=3,
                    help='Number of spam documents per task.')
parser.add_argument('-s', '--sentences', type=int, default=104,
                    help='Number of sentences per rater.')
parser.add_argument('-ss', '--sentences_spam', type=int, default=8,
                    help='Number of spam sentences per task.')
parser.add_argument('-o', '--output', type=FileType('w'), default=sys.stdout,
                    help='Output file (CSV). Defaults to stdout.')

args = parser.parse_args()

# collect data
articles = defaultdict(list)
articles_with_human_b = set()
for sentence in csv.DictReader(args.data):
    articles[sentence['wmt_article']].append(sentence)
    if sentence['human_b'] != '':
        articles_with_human_b.add(sentence['wmt_article'])
sents_per_article = [len(article) for article in articles.values()]
logging.info('Input: %s articles, %s containing `human_b`.', len(articles), len(articles_with_human_b))

# sample 50 articles and 104 sentences containing human_b, in random order
random_article_ids = []
random_sentences = []
articles_with_human_b = sorted(articles_with_human_b)
while not (len(random_sentences) >= args.sentences):
    random_sentences = []
    random.shuffle(articles_with_human_b)
    random_article_ids = articles_with_human_b[:args.documents]
    for article_id in articles_with_human_b[args.documents:]:
        random_sentences.extend(articles[article_id])
random_articles = [merge_sentences(articles[i]) for i in random_article_ids]
random_sentences = random_sentences[:args.sentences]
random.shuffle(random_sentences)

# prepare spam items

# Spam items are created from articles for which human_b is not available.
# We render mt nonsensical and expect raters to chose human_a.

articles_without_human_b = [articles[i] for i in articles.keys() if i not in articles_with_human_b]
random.shuffle(articles_without_human_b)

# compose experiment

# task | raters  | condition           | items       | level    | file
# cd   | group 1 | mt vs. human_b      | first half  | document | 1d
# cs   | group 1 | mt vs. human_b      | first half  | sentence | 1s
# dd   | group 1 | human_a vs. human_b | second half | document | 1d
# ds   | group 1 | human_a vs. human_b | second half | sentence | 1s
# ed   | group 2 | mt vs. human_b      | second half | document | 2d
# es   | group 2 | mt vs. human_b      | second half | sentence | 2s
# fd   | group 2 | human_a vs. human_b | first half  | document | 2d
# fs   | group 2 | human_a vs. human_b | first half  | sentence | 2s

all_experimental_items = []

file_mapping = {
    'cd': '1d',
    'cs': '1s',
    'dd': '1d',
    'ds': '1s',
    'ed': '2d',
    'es': '2s',
    'fd': '2d',
    'fs': '2s'
}

file_order = {
    '1d': random_range(1, args.documents + args.documents_spam * 2 + 1),
    '1s': random_range(1, args.sentences + args.sentences_spam * 2 + 1),
    '2d': random_range(1, args.documents + args.documents_spam * 2 + 1),
    '2s': random_range(1, args.sentences + args.sentences_spam * 2 + 1)
}

for level, all_items in zip('ds', [random_articles, random_sentences]):
    for task, a_choice, items in zip('cdef', [
            'mt',
            'human_a',
            'mt',
            'human_a'
        ], [
            all_items[int(len(all_items)/2):],
            all_items[:int(len(all_items)/2)],
            all_items[:int(len(all_items)/2)],
            all_items[int(len(all_items)/2):]
        ]):
        experimental_items = []
        task_id = task + level
        ab_choices = (a_choice, 'human_b')
        # regular items
        for item in items:
            item = create_experimental_item(item, ab_choices)
            experimental_items.append(item)
        # spam items
        num_spam_items = args.documents_spam if level == 'd' else args.sentences_spam
        for _ in range(num_spam_items):
            article = articles_without_human_b.pop()
            item = create_experimental_spam_item(article, level)
            experimental_items.append(item)
        # shuffle spam and regular items
        random.shuffle(experimental_items)
        # add task_id, order
        for i, item in enumerate(experimental_items, start=1):
            item['task_id'] = task_id
            item['task_order'] = i
            item['file_id'] = file_mapping[task_id]
            item['file_order'] = file_order[item['file_id']].pop()
        all_experimental_items.extend(experimental_items)

# sort items by file_id, file_order ASC
all_experimental_items = sorted(all_experimental_items,
                                key=lambda x: (x['file_id'], x['file_order']))

# write experimental data
writer = csv.DictWriter(args.output, extrasaction="ignore", fieldnames=[
    'file_id', # e.g., 1d
    'file_order', # e.g., 1
    'task_id', # e.g., dd
    'task_order', # e.g., 23
    'wmt_article',
    'wmt_line',
    'src',
    'A',
    'B',
    'A_origin',
    'B_origin'
])
writer.writeheader()
for item in all_experimental_items:
    writer.writerow(item)
