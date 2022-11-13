from datetime import date, datetime
from enum import IntEnum
import logging
import re
from typing import Any

from pydantic import BaseModel
from pydriller.repository import Commit, Repository

log = logging.getLogger("novelopment.miner")


class CommitSize(IntEnum):
    TINY = 1
    SMALL = 2
    MEDIUM = 3
    BIG = 4
    GIGANTIC = 5

    @classmethod
    def get_size_of_commit(cls, commit: Commit):
        lines = commit.lines
        if lines > 1000:
            return cls.GIGANTIC
        if lines > 500:
            return cls.BIG
        if lines > 150:
            return cls.MEDIUM
        if lines > 30:
            return cls.SMALL
        return cls.TINY


class Actor(BaseModel):
    email: str
    name: str
    authored_commits: int = 0
    authored_fix_commits: int = 0
    committed_commits: int = 0

    def __repr__(self) -> str:
        return f"{self.name} <{self.email}>"

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


class NovelCommit(BaseModel):
    hash: str
    author: Actor
    committer: Actor
    msg: str
    authored_date: date
    authored_datetime: datetime
    committed_date: date
    committed_datetime: datetime
    size: CommitSize
    is_fix: bool

    @classmethod
    def from_commit(cls, commit: "Commit", actors: dict[str, Actor]):
        fix_pattern = r"\bfix\b"
        committer_email = commit.committer.email
        author_email = commit.author.email
        if author_email not in actors:
            actors[author_email] = Actor(
                email=author_email,
                name=commit.author.name,
            )
        if committer_email not in actors:
            actors[committer_email] = Actor(
                email=committer_email,
                name=commit.committer.name,
            )
        novel_commit = cls(
            hash=commit.hash,
            author=actors[author_email],
            committer=actors[committer_email],
            msg=commit.msg,
            authored_date=commit.author_date.date(),
            authored_datetime=commit.author_date,
            committed_date=commit.committer_date.date(),
            committed_datetime=commit.committer_date,
            size=CommitSize.get_size_of_commit(commit),
            is_fix=bool(re.search(fix_pattern, commit.msg, re.IGNORECASE)),
        )
        actors[author_email].authored_commits += 1
        actors[committer_email].committed_commits += 1
        if novel_commit.is_fix:
            actors[author_email].authored_fix_commits += 1
        return novel_commit


def extract_data(repo: Repository):
    events = []
    actors = {}
    for i, commit in enumerate(repo.traverse_commits()):
        log.debug("Analyzing commit %s", commit.hash)
        if i % 50 == 0:
            log.info("Analyzed %d commits", i)
        events.append(NovelCommit.from_commit(commit, actors))
    return actors, events
