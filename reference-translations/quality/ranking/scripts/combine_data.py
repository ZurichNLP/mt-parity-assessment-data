#!/usr/bin/env python3

import re
import csv
import sys
import logging
from argparse import ArgumentParser, FileType

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def normalise(segment):
    return segment.replace('“', '"') \
                  .replace('”', '"') \
                  .replace('‘', "'") \
                  .replace('’', "'") \
                  .strip()

parser = ArgumentParser(description='Combines WMT18 ZH-EN articles with '
                                    'translations from Microsoft (Hassan et '
                                    'al., 2018) and Graham Neubig.')
parser.add_argument('src', help='The WMT18 ZH-EN testset (newstest2017-zhen-src.zh.sgm).')
parser.add_argument('trg_mt', help='The machine translations produced by Microsoft (microsoft-mt-combo6.txt).') # https://github.com/MicrosoftTranslator/Translator-HumanParityData/blob/master/Translator-HumanParityData/Translations/Translator-HumanParityData-Combo-6.txt
parser.add_argument('trg_human_a', help='The human translations collected by microsoft (microsoft-ht.txt).')
# https://github.com/MicrosoftTranslator/Translator-HumanParityData/blob/master/Translator-HumanParityData/References/Translator-HumanParityData-Reference-HT.txt
parser.add_argument('trg_human_b', help='The human translations collected by Graham Neugbig  (graham-ht.csv). Caution: Line breaks are encoded as \\r.')
parser.add_argument('-0', '--output', type=FileType('w'), default=sys.stdout,
                    help='Output file (CSV). Defaults to stdout.')

args = parser.parse_args()

# define regexes to find article ids (ugly)
article_id = re.compile(r'docid="([^"]+)"')
article_origlang = re.compile(r'origlang="([^"]+)"')
segment_content = re.compile(r'<seg[^>]+>(.*)</seg>')

# collect all article ids and sentence counts from sgm
lines = []
article_count = 0
with open(args.src) as f:
    for line_number, line in enumerate(f):
        try:
            wmt_id = article_id.search(line).groups()[0]
            wmt_order = article_count
            article_count += 1 # Graham's order numbers start at 0
            origlang = article_origlang.search(line).groups()[0]
        except AttributeError:
            pass
        if line.startswith('<seg'):
            sentence = segment_content.search(line).groups()[0]
            lines.append({
                'origlang': origlang,
                'wmt_id': wmt_id,
                'wmt_order': wmt_order,
                'src': sentence
            })

# collect human_a, mt (Microsoft)
for origin, filepath in {'human_a': args.trg_human_a, 'mt': args.trg_mt}.items():
    with open(filepath) as f:
        for line_number, sentence in enumerate(f):
            lines[line_number][origin] = normalise(sentence)

# calculate line numbers where articles begin to mix in human_b
wo = [line['wmt_order'] for line in lines]
offsets = {b: i for i, (a, b) in enumerate(zip([None] + wo, wo)) if a != b}

# collect human_b (Graham Neubig)
with open(args.trg_human_b, encoding='utf-8-sig') as f: # utf-8-sig since Excel writes BOM
    csv_reader = csv.DictReader(f)
    for article in csv_reader:
        wmt_order = article['Order']
        if wmt_order:
            sentences_src = [s for s in article['Original'].split('\n') if s != '']
            sentences_trg = [s for s in article['Translation (English)'].split('\n') if s != '']
            if len(sentences_src) == len(sentences_trg):
                line_number = offsets[int(wmt_order)]
                for sentence_src, sentence_trg in zip(sentences_src, sentences_trg):
                    assert lines[line_number]['src'] == sentence_src # just to be sure...
                    lines[line_number]['human_b'] = sentence_trg
                    line_number += 1
            else:
                logging.warning('Skipping item %s in human_b. Original contains %s sentences, Translation contains %s.', wmt_order, len(sentences_src), len(sentences_trg))

# write csv
writer = csv.DictWriter(args.output, fieldnames=['wmt_article', 'wmt_line', 'wmt_article_name', 'src', 'mt', 'human_a', 'human_b'])
writer.writeheader()
for line_number, line in enumerate(lines):
    if line['origlang'] == 'zh': # only keep articles who were originally written in Chinese
        writer.writerow({
            'wmt_article': line['wmt_order'],
            'wmt_line': line_number + 1,
            'wmt_article_name': line['wmt_id'],
            'src': line['src'],
            'mt': line['mt'],
            'human_a': line['human_a'],
            'human_b': line['human_b'] if 'human_b' in line else ''
        })
