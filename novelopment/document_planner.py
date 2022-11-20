import logging
from typing import List

import simplenlg as nlg

from novel import Novel
from realizer import Sentence

log = logging.getLogger("novelopment.document_planner")


def plan_document(novel: Novel, content: dict, actors: dict, events: List):

    # beginnings
    beginnings_planner(novel, content, actors, events)
    return


def beginnings_planner(novel: Novel, content: dict, actors: dict, events: List):
    chapter = novel.new_chapter(title="Humble beginnings")

    paragraph = []
    paragraph.append(
        Sentence(
            time=content["important_dates"]["first_authored"],
            subject="book",
            predicate="start",
            tense=nlg.Tense.PRESENT,
        ),
    )
    paragraph.extend(
        [
            Sentence(
                time=content["important_dates"]["first_authored"],
                subject=content["important_actors"]["first_author"],
                predicate="author",
                complement="the first commit",
            ),
        ]
    )
    chapter.content.append(paragraph)

    return
