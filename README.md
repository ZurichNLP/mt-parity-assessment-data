# A Set of Recommendations for Assessing Human–Machine Parity in Language Translation

This repository contains all experimental data described and analysed in:

```TeX
@unpublished{laeubli2019parity,
  Author = {Läubli, Samuel and Casthilo, Sheila and Neubig, Graham and Sennrich, Rico and Shen, Qinlan and Toral, Antonio},
  Title  = {A Set of Recommendations for Assessing Human--Machine Parity in Language Translation},
  Year   = {2019},
  Note   = {Under review}}
```

### Structure

| Subdirectory                                                                               | Reference   | Main Finding                                                                                                                                                                                                                 |
|--------------------------------------------------------------------------------------------|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`raters`](raters)                                                               | Section 3   | Employing professional translators rather than crowd workers and researchers increases the rating gap between human and machine translation.                                                                                 |
| [`linguistic-context`](https://github.com/laeubli/parity)                                       | Section 4   | Evaluating full documents rather than isolated sentences increases the rating gap between human and machine translation.                                                                                                     |
| [`reference-translations/quality`](reference-translations/quality)               | Section 5.1 | Machine translation contains significantly more incorrect words, omissions, mistranslated names, and word order errors than human translation in Hassan et al.'s (2018) [dataset](http://aka.ms/Translator-HumanParityData). |
| [`reference-translations/directionality`](reference-translations/directionality) | Section 5.2 | Translated texts are simpler than original texts, and in turn easier to machine translate.                                                                                                                                   |
