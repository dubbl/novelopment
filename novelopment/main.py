import argparse
import logging
from pathlib import Path
import random

import pycorpora
from pydriller.repository import Repository
import simplenlg as nlg

from aggregator import aggregate
from content_determiner import determine_content
from document_planner import plan_document
from expressions_generator import generate_expressions
from miner import extract_data
from novel import Novel
from realizer import realize

log = logging.getLogger("novelopment")
logging.basicConfig()

lexicon = nlg.lexicon.Lexicon.getDefaultLexicon()
nlg_factory = nlg.NLGFactory(lexicon)
realiser = nlg.realiser.Realiser(lexicon)


def main():
    args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.INFO)
    if args.verbose > 1:
        log.setLevel(logging.DEBUG)
    log.info("Loading repository %s", args.repository)
    repo = load_repo(args.repository, args.branch)
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

    content = determine_content(actors, events)
    for key in content:
        print(f"{key}:")
        for k, v in content[key].items():
            print(f"\t{k}: {v}")

    intro = novel.new_chapter(title="Introduction")

    actor_word = random.choice(["person", "human", "developer", "contributor"])
    actor_word = lexicon.getWord(actor_word, nlg.LexicalCategory.NOUN)
    predicate = "building"
    if len(actors) > 1:
        actor_word.setPlural(True)
        predicate = "coming together to build"
    actor_word = realiser.realise(actor_word)

    intro.paragraphs.append(
        [
            "While you may have been enticed to grab this book because of its "
            f'title "{novel.title}", this is actually the story of {len(actors)}'
            f" {actor_word} {predicate} {repo_name} in {len(events)} commits.",
        ]
    )
    # handle empty repos?
    plan_document(novel, content, actors, events)
    aggregate(novel)
    generate_expressions(novel)
    realize(novel)

    novel.print()


def get_repo_name(repository_location):
    if repository_location.endswith(".git"):
        return repository_location.split("/")[-1][:-4]
    return Path(repository_location).absolute().stem


def load_repo(filepath, branch):
    return Repository(filepath, only_in_branch=branch)


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
    "-b",
    "--branch",
    default="master",
    help="The branch that should story should be based on (default: master)",
    required=False,
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
parser.add_argument("--verbose", "-v", action="count", default=0)


if __name__ == "__main__":
    main()
