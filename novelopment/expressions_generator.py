from collections import Counter
from datetime import timedelta
from itertools import tee
import random

from lexicon import get_word
from miner import Actor, CommitSize, NovelCommit
from novel import Novel


def generate_expressions(novel: Novel):
    global_appearance = Counter()
    for chapter in novel.chapters:
        generate_referring_expressions(chapter.content)
        generate_describing_entity_expressions(chapter.content, global_appearance)
        generate_time_expressions(chapter.content)


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


time_checks = [
    ("year", {"days": 365}, 0, 10),
    ("week", {"days": 7}, 0, 51),
    ("day", {"days": 1}, 0, 6),
]


def generate_time_expressions(content):
    for paragraph in content:
        for s1, s2 in pairwise(paragraph):
            if not s1.time or not s2.time:
                continue
            if isinstance(s1.time, str) or isinstance(s2.time, str):
                continue
            delta = s2.time - s1.time
            for name, delta_params, min_range, max_range in time_checks:
                if name == "day" and random.getrandbits(1):
                    # days don't always have to be counted
                    continue
                for factor in range(max_range, min_range, -1):
                    if delta == timedelta(**delta_params) * factor:
                        name = name if factor == 1 else f"{name}s"
                        prefix = random.choice(
                            [
                                "exactly",
                                "around",
                                "roughly",
                                "about",
                                "roundabout",
                            ],
                        )
                        postfix = random.choice(
                            ["later", "down the line", "down the road"],
                        )
                        s2.time_expression = f"{prefix} {factor} {name} {postfix}"
                        break
                    if delta > timedelta(**delta_params) * factor and name != "day":
                        name = name if factor == 1 else f"{name}s"
                        postfix = random.choice(
                            ["later", "down the line", "down the road"],
                        )
                        s2.time_expression = f"More than {factor} {name} {postfix}"
                        break


def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def generate_describing_entity_expressions(content, global_appearance):
    chapter_appearance = Counter()
    for paragraph in content:
        for sentence in paragraph:
            describe_entities(sentence, global_appearance, chapter_appearance)


def describe_entities(sentence, global_appearance, chapter_appearance):
    if not isinstance(sentence.subject, str):
        sentence.subject = get_expression_for(
            sentence.subject,
            chapter_appearance,
            global_appearance,
        )
    new_complements = []
    for complement in sentence.complements:
        new_complements.append(
            get_expression_for(
                complement,
                chapter_appearance,
                global_appearance,
            ),
        )
    sentence.complements = new_complements
    for connected_phrases in sentence.connected_phrases:
        for connected_sentence in connected_phrases.phrases:
            describe_entities(
                connected_sentence,
                global_appearance,
                chapter_appearance,
            )


commit_size_expression = {
    CommitSize.TINY: "tiny",
    CommitSize.BIG: "huge",
    CommitSize.GIGANTIC: "gigantic",
}


def get_expression_for(something, chapter_appearance, global_appearance):
    expression = get_word(something.to_word())
    chapter_appearance[str(something)] += 1
    global_appearance[str(something)] += 1
    if isinstance(something, Actor):
        if global_appearance[str(something)] == 1:
            expression = f"first time contributor {expression}"
        elif chapter_appearance[str(something)] == 1:
            expression = random.choice(
                [
                    f"our old friend {expression}",
                    f"the previously mentioned {expression}",
                    f"aforementioned {expression}",
                ],
            )
    elif isinstance(something, NovelCommit):
        if something.is_fix:
            expression = random.choice(
                [
                    f"fix {expression}",
                    f"bug fixing {expression}",
                    f"defect fixing {expression}",
                    f"bug removal {expression}",
                    f"bug removing {expression}",
                ]
            )
        size_description = ""
        if commit_size_expression.get(something.size):
            size_description = commit_size_expression.get(something.size) + " "
        size_description = ""
        if commit_size_expression.get(something.size):
            size_description = commit_size_expression.get(something.size) + " "
        message_desc = random.choice(
            [
                f'with the message "{something.msg}"',
                f'claiming to "{something.msg}"',
                f'described as "{something.msg}"',
                f'called "{something.msg}"',
            ],
        )
        expression = f"a {size_description}{expression} {message_desc}"
    return expression
