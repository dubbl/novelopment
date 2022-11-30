from itertools import tee

from novel import Novel, Actor, NovelCommit


def generate_expressions(novel: Novel):
    for chapter in novel.chapters:
        generate_referring_expressions(chapter.content)


def generate_referring_expressions(content):
    for paragraph in content:
        for s1, s2 in pairwise(paragraph):
            if isinstance(s1.subject, str):
                continue
            if s1.subject == s2.subject:
                if isinstance(s1.subject, Actor):
                    s2.subject = "they"
                if isinstance(s1.subject, NovelCommit):
                    s2.subject = "it"


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)
