# Intelligent Surveillance

## Current scope (what exists today)

At the moment, this repo contains a simple **rule-based bad-word detector** in `bad_word_detector.py`.

It loads a list of disallowed words from `datasets/english.csv` and scans an input text for exact (lowercased) token matches.

There is also a (currently disabled) helper for language detection based on NLTK stopwords, but it is not part of the main flow.

## How it works

`bad_word_detector.py` performs the following steps:

1. Splits the input string into lines (`text.split("\n")`).
2. For each line/sentence, strips a small set of punctuation characters.
3. Tokenizes via `sentence.lower().split()`.
4. Checks each token against the bad-word set loaded from `datasets/english.csv`.
5. Prints details when bad words are found and returns:
   - `"Good"` when no bad words are detected
   - `"bad"` when at least one bad word is detected

## Setup

1. Install Python requirements:

```powershell
pip install -r req.txt
```

NLTK is included via `req.txt` (`nltk==3.8.1`). If you later enable the language-detection portion of the code, you may also need the NLTK corpora (e.g. `stopwords`).

## Usage

This script’s `__main__` section currently calls `main(text)` with `text = ""`, so it won’t be very useful as-is without setting `text`.

Typical usage is to call `main(text)` from another script / notebook, for example:

```python
from bad_word_detector import main

result = main("some input text here")
print(result)
```

## Limitations (why it’s not NLP yet)

- It is **not** a trained NLP model yet.
- It doesn’t do contextual classification, stemming/lemmatization, or typo/variant handling.
- The only detection approach is exact word matching against the CSV list.

## Roadmap (what you’re working toward)

The project is being improved toward an **NLP-based text classification** system (instead of pure word matching).

Depending on what performs best for the multilingual/text-cleaning pipeline, an **SMT-based** approach may also be explored for preprocessing or text transformations.

