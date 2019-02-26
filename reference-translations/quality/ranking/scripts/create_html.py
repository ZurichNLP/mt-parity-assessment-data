#!/usr/bin/env python3

import os
import csv
import logging
from collections import defaultdict
from argparse import ArgumentParser, FileType


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def num_words(text):
    return len(text.split()) # no real tokenization, just split on whitespace


def get_css():
    with open('templates/style.css') as f:
        return f.read()


def get_html_instructions(monolingual=False):
    filename = 'instructions-{0}.html'.format('monolingual' if monolingual else 'bilingual')
    with open('templates/' + filename) as f:
        return f.read()


def get_html_body(items, monolingual=False):
    mode = 'm' if monolingual else 'b'
    html_body = ''
    for item in items:
        item_id = '{0}{1}-{2}'.format(mode, item['file_id'], item['file_order'])
        html_body += '<div class="item">'
        html_body += '\n\t<div class="title" id="{0}">{0}</div>'.format(item_id)
        if not monolingual:
            html_body += '\n\t<div class="source" id="{0}">{1}</div>'.format(item_id, item['src'])
        html_body += '\n\t<div class="translation" id="{0}">{1}</div>'.format(item_id, item['A'])
        html_body += '\n\t<div class="translation" id="{0}">{1}</div>'.format(item_id, item['B'])
        html_body += '\n</div>\n\n'
    return html_body


def get_html(items, monolingual=False):
    css = get_css()
    instructions = get_html_instructions(monolingual=monolingual)
    body = get_html_body(items, monolingual=monolingual)
    return '''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Rate Texts</title>
        <style>
            {0}
        </style>
      </head>
      <body>
        {1}
        {2}
      </body>
    </html>
    '''.format(css, instructions, body)


parser = ArgumentParser(description='Creates standalone HTML for each task in'
                                    'the CSV output of `create_experiment.py`.')
parser.add_argument('data', type=FileType('r'), help='The CSV output of '
                                                     '`create_experiment.py`.)')
parser.add_argument('-d', '--directory', default=os.getcwd(),
                    help='Output directory (default: current working directory).')

args = parser.parse_args()

# read data
files = defaultdict(list)
for item in csv.DictReader(args.data):
    files[item['file_id']].append(item)

# create html
for file_id, items in files.items():
    num_src_chars = sum([len(i['src']) for i in items])
    num_trg_chars = sum([len(i['A']) + len(i['B']) for i in items])
    num_trg_words = sum([num_words(i['A']) + num_words(i['B']) for i in items])
    logging.info('File %s: %s items, %s src chars, %s trg chars (%s words).',
                 file_id, len(items), num_src_chars, num_trg_chars, num_trg_words)
    for monolingual in [False, True]:
        prefix = 'm' if monolingual else 'b'
        target_file = args.directory + '/' + prefix + file_id + '.html'
        html = get_html(items, monolingual=monolingual)
        with open(target_file, 'w') as f:
            f.write(html)
