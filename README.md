# Novelopment

Generate the story of your git repository.

## Usage

Example: `python3 src/main.py https://github.com/dubbl/novelopment.git`
Replace the URL with any other URL of a git repository or point it to a local
repository.

```
usage: novelopment [-h] [-s SEED] repository

Generate the story of a git repository.

positional arguments:
  repository            Filepath or URL of the git repository

optional arguments:
  -h, --help            show this help message and exit
  -s SEED, --seed SEED  Hexadecimal seed of the pseudorandom number generator. Defaults to the hash of the latest commit.

Commit for adventure!
```


## Installation

1. Run `poetry install` in the root folder.

2. pycorpora uses on installation triggers in its setup.py.
   These are not executed by poetry (on purpose), so the corpus data is not
   actually downloaded. I manually copied the required files from
   [corpora](https://github.com/dariusk/corpora/archive/master.zip) into the
   site-packages folder for pycorpora in the virtual environment.
