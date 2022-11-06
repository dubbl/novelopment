import argparse

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
    novel = Novel(title=f'The story of {get_repo_name(args.repository)}')

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


if __name__ == '__main__':
    main()
