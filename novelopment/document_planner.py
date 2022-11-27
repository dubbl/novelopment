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
    author_authors_first_commit = Sentence(
        time=content["important_dates"]["first_authored"],
        subject=content["important_actors"]["first_author"],
        predicate="author",
        complement="the first commit",
    )
    connected_phrase = ConnectedPhrase(
        connector_type=ConnectorType.COMPLEMENTIZER,
        connector="when",
        phrases=[author_authors_first_commit],
    )
    paragraph.append(
        Sentence(
            time=content["important_dates"]["first_authored"],
            subject="book",
            predicate="start",
            connected_phrase=connected_phrase,
        ),
    )
    chapter.content.append(paragraph)


def mid_part_planner(novel: Novel, content: dict, actors: dict, events: List):
    chapter = novel.new_chapter(title="Working on it")

    paragraph = []
    for event in events:
        paragraph.extend(
            [
                Sentence(
                    time=event.authored_date,
                    subject=event.author,
                    predicate="author",
                    complement=event,
                ),
            ]
        )
    chapter.content.append(paragraph)
