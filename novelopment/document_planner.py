import logging
from typing import List

import simplenlg as nlg

from novel import Novel, ConnectedPhrase, ConnectorType, Sentence

log = logging.getLogger("novelopment.document_planner")


def plan_document(novel: Novel, content: dict, actors: dict, events: List):
    # beginnings
    beginnings_length = len(events) // 5
    chapter_prompt, i = beginnings_planner(
        novel, content, actors, events[:beginnings_length]
    )
    while chapter_prompt:
        chapter_prompt, i = chapter_planners[chapter_prompt](
            novel, content, actors, events[i:beginnings_length]
        )
    chapter_prompt, i = mid_part_planner(
        novel, content, actors, events[beginnings_length:]
    )
    while chapter_prompt:
        i = i + beginnings_length
        chapter_prompt, i = chapter_planners[chapter_prompt](
            novel, content, actors, events[i:]
        )


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

    chapter_prompt = None
    for i, event in enumerate(events):
        chapter_prompt = check_for_important_event(
            event,
            content,
            allowed_events=["first_commit"],
        )
        if chapter_prompt:
            break
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
    return chapter_prompt, i


def mid_part_planner(novel: Novel, content: dict, actors: dict, events: List):
    chapter = novel.new_chapter(title="Working on it")

    paragraph = []
    chapter_prompt = None
    for i, event in enumerate(events):
        chapter_prompt = check_for_important_event(event, content)
        if chapter_prompt:
            break
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
    return chapter_prompt, i


def second_author_planner(novel: Novel, content: dict, actors: dict, events: List):
    chapter = novel.new_chapter(title="Two is a crowd")

    paragraph = []
    chapter_prompt = None
    paragraph.append(
        Sentence(
            time=events[0].authored_date,
            subject=events[0].author,
            predicate="join",
            complements=[content["important_actors"]["first_author"]],
            connected_phrases=[
                ConnectedPhrase(
                    connector="Finally",
                    connector_type=ConnectorType.CUE_PHRASE,
                )
            ],
        ),
    )
    for i, event in enumerate(events):
        chapter_prompt = check_for_important_event(
            event, content, allowed_events=["first_different_user_author"]
        )
        if chapter_prompt:
            break
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
    return chapter_prompt, i


def the_end_planner(novel: Novel, content: dict, actors: dict, events: List):
    chapter = novel.new_chapter(title="The end (for now)")

    paragraph = []
    chapter_prompt = None
    for i, event in enumerate(events):
        chapter_prompt = check_for_important_event(
            event,
            content,
            allowed_events=["last_commit"],
        )
        if chapter_prompt:
            break
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
    return chapter_prompt, i


def check_for_important_event(event, content, allowed_events=None):
    if not allowed_events:
        allowed_events = []
    if event in content["important_events"].values():
        important_event_key = [
            k for k, v in content["important_events"].items() if v == event
        ][0]
        if important_event_key not in allowed_events:
            return important_event_key


chapter_planners = {
    "first_commit": beginnings_planner,
    "first_different_user_author": second_author_planner,
    "last_commit": the_end_planner,
}
