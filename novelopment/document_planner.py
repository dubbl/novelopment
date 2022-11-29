import logging
from typing import List

import simplenlg as nlg

from novel import Novel, ConnectedPhrase, ConnectorType, Sentence

log = logging.getLogger("novelopment.document_planner")


def plan_document(novel: Novel, content: dict, actors: dict, events: List):

    # beginnings
    beginnings_planner(novel, content, actors, events)
    mid_part_planner(novel, content, actors, events)
    return


def beginnings_planner(novel: Novel, content: dict, actors: dict, events: List):
    chapter = novel.new_chapter(title="Humble beginnings")

    paragraph = []
    paragraph.append(
        Sentence(
            time=content["important_dates"]["first_authored"],
            subject="book",
            predicate="start",
        ),
    )
    for event in events[: len(events) // 5]:
        paragraph.extend(
            [
                Sentence(
                    time=event.authored_date,
                    subject=event.author,
                    predicate="author",
                    complements=[event],
                ),
            ]
        )
    chapter.content.append(paragraph)


def mid_part_planner(novel: Novel, content: dict, actors: dict, events: List):
    chapter = novel.new_chapter(title="Working on it")

    paragraph = []
    for event in events[len(events) // 5 :]:
        paragraph.extend(
            [
                Sentence(
                    time=event.authored_date,
                    subject=event.author,
                    predicate="author",
                    complements=[event],
                ),
            ]
        )
    chapter.content.append(paragraph)
