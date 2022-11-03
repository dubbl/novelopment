import argparse

from pydriller.repository import Repository


def main():
    args = parser.parse_args()
    repo = load_repo(args.repository)
    novel = ''
    for commit in repo.traverse_commits():
        first_line_commit_msg = commit.msg.split('\n')[0]
        novel += f'{commit.author.name} be like {first_line_commit_msg}\n'
    print(novel)
    print(len(novel.split(' ')))


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
