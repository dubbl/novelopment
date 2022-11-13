from itertools import groupby
from operator import attrgetter


def identify_important_events(events):
    first_author = events[0].author
    first_second_author_commit = None
    for event in events:
        if event.author != first_author:
            first_second_author_commit = event
            break

    return {
        "first_commit": events[0],
        "last_commit": events[-1],
        "first_different_user_author": first_second_author_commit,
    }


def identify_important_actors(actors, content):
    return {
        "most_authored": sorted(
            actors.values(),
            key=attrgetter("authored_commits"),
            reverse=True,
        )[0],
        "most_committed": sorted(
            actors.values(),
            key=attrgetter("committed_commits"),
            reverse=True,
        )[0],
        "most_fixes_authored": sorted(
            actors.values(),
            key=attrgetter("authored_fix_commits"),
            reverse=True,
        )[0],
        "first_author": content["important_events"]["first_commit"].author,
        "first_committer": content["important_events"]["first_commit"].committer,
        "last_author": content["important_events"]["last_commit"].author,
        "last_committer": content["important_events"]["last_commit"].committer,
    }


def identify_important_dates(events, content):
    most_authored_date = get_biggest_group(events, "authored_date")[1]
    most_committed_date = get_biggest_group(events, "committed_date")[1]
    return {
        "most_authored_date": most_authored_date,
        "most_committed_date": most_committed_date,
        "first_authored": content["important_events"]["first_commit"].authored_date,
        "last_authored": content["important_events"]["last_commit"].authored_date,
    }


def get_biggest_group(items, attr):
    return sorted(
        [
            (len(list(group)), group_id)
            for group_id, group in groupby(items, key=attrgetter(attr))
        ],
        reverse=True,
    )[0]


def determine_content(actors: dict, events: list):
    content = {}
    content["important_events"] = identify_important_events(events)
    content["important_actors"] = identify_important_actors(actors, content)
    content["important_dates"] = identify_important_dates(events, content)
    return content


def get_first_author(events):
    return events[0].author
