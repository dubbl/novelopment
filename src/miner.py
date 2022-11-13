from datetime import date, datetime
from enum import IntEnum
import logging
import re
from typing import Any

from pydantic import BaseModel
from pydriller.repository import Commit, Repository

log = logging.getLogger(__name__)


class CommitSize(IntEnum):
    TINY = 1
    SMALL = 2
    MEDIUM = 3
    BIG = 4
    GIGANTIC = 5

    @classmethod
    def get_size_of_commit(cls, commit: Commit):
        if commit.lines > 1000:
            return cls.GIGANTIC
        if commit.lines > 500:
            return cls.BIG
        if commit.lines > 150:
            return cls.MEDIUM
        if commit.lines > 30:
            return cls.SMALL
        return cls.TINY


class Actor(BaseModel):
    email: str
    name: str
    authored_commits: list["NovelCommit"] = []
    committed_commits: list["NovelCommit"] = []


class NovelCommit(BaseModel):
    hash: str
    author: Any
    msg: str
    author_date: date
    author_datetime: datetime
    size: CommitSize
    is_fix: bool

    @classmethod
    def from_commit(cls, commit: "Commit", actors: dict[str, Actor]):
        fix_pattern = r"\bfix\b"
        if commit.author.email not in actors:
            actors[commit.author.email] = Actor(
                email=commit.author.email,
                name=commit.author.name,
            )
        if commit.committer.email not in actors:
            actors[commit.committer.email] = Actor(
                email=commit.committer.email,
                name=commit.committer.name,
            )
        if commit.author.email not in actors:
            actors[commit.author.email] = Actor(
                email=commit.author.email,
                name=commit.author.name,
            )
        novel_commit = cls(
            hash=commit.hash,
            author=Actor(
                email=commit.author.email,
                name=commit.author.name,
            ),
            msg=commit.msg,
            author_date=commit.author_date.date(),
            author_datetime=commit.author_date,
            size=CommitSize.get_size_of_commit(commit),
            is_fix=bool(re.search(fix_pattern, commit.msg, re.IGNORECASE)),
        )
        actors[commit.author.email].authored_commits.append(novel_commit)
        actors[commit.committer.email].committed_commits.append(novel_commit)
        return novel_commit


def extract_data(repo: Repository):
    events = []
    actors = {}
    for i, commit in enumerate(repo.traverse_commits()):
        log.info("Analyzed commit %d", i)
        events.append(NovelCommit.from_commit(commit, actors))
    return actors, events
