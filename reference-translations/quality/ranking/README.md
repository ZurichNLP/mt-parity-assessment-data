# human-parity-graham

## Task assignment

Groups of raters are assigned the following tasks. Files are stored in the `output` directory.

raters               | files (documents, sentences)
-------------------- | ----------------------------
monolingual, group 1 | m1d.pdf, m1s.pdf
monolingual, group 2 | m2d.pdf, m2s.pdf
bilingual, group 1   | b1d.pdf, b1s.pdf
bilingual, group 2   | b2d.pdf, b2s.pdf

## Task composition

Tasks are composed as follows:

task | raters  | condition           | items       | level    | file
---- | ------- | ------------------- | ----------- | -------- | ----
cd   | group 1 | mt vs. human_b      | first half  | document | 1d
cs   | group 1 | mt vs. human_b      | first half  | sentence | 1s
dd   | group 1 | human_a vs. human_b | second half | document | 1d
ds   | group 1 | human_a vs. human_b | second half | sentence | 1s
ed   | group 2 | mt vs. human_b      | second half | document | 2d
es   | group 2 | mt vs. human_b      | second half | sentence | 2s
fd   | group 2 | human_a vs. human_b | first half  | document | 2d
fs   | group 2 | human_a vs. human_b | first half  | sentence | 2s

Each task will be run in two variants: monolingual and bilingual. Monolingual tasks will be prefixed with “m”, e.g., “mcd”; bilingual tasks will be prefixed with “b”, e.g., “bcd”.

Raters will use task ids and order numbers to record their choices in spreadsheets, such as “mcd-1”, “mcd-2”, etc.

## data.csv

Contains all articles of the WMT 2018 Chinese–English testset that were originally written in Chinese.

* `wmt_article`: Article number, starting at 0.
* `wmt_line`: Original line number, starting at 1.
* `wmt_article_name`: Article name.
* `src`: Chinese source.
* `mt`: [Machine translation](https://github.com/MicrosoftTranslator/Translator-HumanParityData/blob/master/Translator-HumanParityData/Translations/Translator-HumanParityData-Combo-6.txt) produced by Microsoft ([Hassan et al., 2018](https://arxiv.org/abs/1803.05567)).
* `human_a`: [Human translation](https://github.com/MicrosoftTranslator/Translator-HumanParityData/blob/master/Translator-HumanParityData/References/Translator-HumanParityData-Reference-HT.txt) commissioned by Microsoft ([Hassan et al., 2018](https://arxiv.org/abs/1803.05567)).
* `human_b`: Human translation commissioned by Graham Neubig (if available).

Note that `wmt_article` and `wmt_line` numbers include articles originally written in English.

## items.csv

Contains experimental items sampled from `data.csv`. In addition to the fields described above, each item has

* `task`: The task id. Document level tasks end in “d”, sentence level tasks in “s”.
* `order`: The number of the experimental item within the task. Starts at 1.
* `A`: The string shown to raters as option A.
* `B`: The string shown to raters as option B.
* `A_origin`: Where option A comes from, e.g., `human_a`.
* `B_origin`: Where option B comes from, e.g., `mt`.

If `A_origin` or `B_origin` is `spam`, raters are expected not to chose `A` or `B`, respectively.
