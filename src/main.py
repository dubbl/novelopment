import argparse
import random

import pycorpora
from pydantic import BaseModel
from pydriller.repository import Repository


class Chapter(BaseModel):
    title: str = ''
    paragraphs: list[str] = []

    def print(self) -> None:
        print(self.title)
        for paragraph in self.paragraphs:
            print(paragraph)


class Novel(BaseModel):
    title: str = ''
    author: str = 'Novelopment 0.1'
    synopsis: str = ''
    chapters: list[Chapter] = []

    def new_chapter(self, **kwargs) -> Chapter:
        chapter = Chapter(**kwargs)
        self.chapters.append(chapter)
        return chapter

    def print(self) -> None:
        print(self.title)
        print(f'By {self.author}\n')
        print(self.synopsis)
        for chapter in self.chapters:
            chapter.print()


def main():
    args = parser.parse_args()
    repo = load_repo(args.repository)
    seed = args.seed
    if not seed:
        seed = list(repo.traverse_commits())[-1].hash
    random.seed(int(seed, 16))
    title_adj = random.choice(pycorpora.words.adjs['adjs'])
    novel = Novel(
        title=f'The {title_adj} story of {get_repo_name(args.repository)}',
    )

    chapter_all = novel.new_chapter(title='All commits')
    for commit in repo.traverse_commits():
        first_line_commit_msg = commit.msg.split('\n')[0]
        chapter_all.paragraphs.append(
            f'{commit.author.name} be like {first_line_commit_msg}',
        )

    novel.print()


def get_repo_name(path):
    if path.endswith('.git'):
        return path.split('/')[-1][:-4]
    # TODO: handle local repos
    return ''


def load_repo(filepath):
    return Repository(filepath)


parser = argparse.ArgumentParser(
    prog = 'novelopment',
    description = 'Generate the story of a git repository.',
    epilog = 'Commit for adventure!',
)
parser.add_argument(
    'repository',
    help='Filepath or URL of the git repository',
)
parser.add_argument(
    '-s',
    '--seed',
    action='store',
    dest='seed',
    help=(
        'Hexadecimal seed of the pseudorandom number generator. '
        'Defaults to the hash of the latest commit.'
    ),
    required=False,
)


if __name__ == '__main__':
    main()
