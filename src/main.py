import argparse
import logging
from pathlib import Path
import random

import pycorpora
from pydriller.repository import Repository
import simplenlg as nlg

from miner import extract_data
from novel import Novel

logging.basicConfig()
log = logging.getLogger(__name__)

lexicon = nlg.lexicon.Lexicon.getDefaultLexicon()
nlg_factory = nlg.NLGFactory(lexicon)
realiser = nlg.realiser.Realiser(lexicon)


def main():
    args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)
    log.info("Loading repository %s", args.repository)
    repo = load_repo(args.repository)
    repo_name = get_repo_name(args.repository)
    seed = args.seed
    if not seed:
        seed = list(repo.traverse_commits())[-1].hash
    random.seed(int(seed, 16))
    title_adv = random.choice(pycorpora.words.adverbs["adverbs"])
    title_adj = random.choice(
        pycorpora.words.encouraging_words["encouraging_words"],
    )
    novel = Novel(
        title=f"The {title_adv} {title_adj} story of {repo_name}",
    )
    log.info("Extracting data from repository")
    actors, events = extract_data(repo)

    intro = novel.new_chapter(title="Introduction")

    actor_word = random.choice(['person', 'human', 'developer', 'contributor'])
    actor_word = lexicon.getWord(actor_word, nlg.LexicalCategory.NOUN)
    if len(actors) > 1:
        actor_word.setPlural(True)
    actor_word = realiser.realise(actor_word)

    intro.paragraphs.append(
        "While you may have been enticed to grab this book because of its title"
        f' "{novel.title}", this is actually the story of {len(actors)}'
        f" {actor_word} who came together to build {repo_name}.",
    )

    novel.print()


def get_repo_name(repository_location):
    if repository_location.endswith(".git"):
        return repository_location.split("/")[-1][:-4]
    return Path(repository_location).absolute().stem


def load_repo(filepath):
    return Repository(filepath)


parser = argparse.ArgumentParser(
    prog="novelopment",
    description="Generate the story of a git repository.",
    epilog="Commit for adventure!",
)
parser.add_argument(
    "repository",
    help="Filepath or URL of the git repository",
)
parser.add_argument(
    "-s",
    "--seed",
    action="store",
    dest="seed",
    help=(
        "Hexadecimal seed of the pseudorandom number generator. "
        "Defaults to the hash of the latest commit."
    ),
    required=False,
)
parser.add_argument(
    "--verbose",
    dest="verbose",
    help="increase output verbosity",
    action="store_true",
)


if __name__ == "__main__":
    main()
