from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel
import simplenlg as nlg

from miner import Actor, NovelCommit


class Chapter(BaseModel):
    title: str = ""
    paragraphs: list[list[str]] = []

    content: list[list["Sentence"]] = []

    def print(self) -> None:
        print(self.title)
        for sentences in self.paragraphs:
            print(" ".join(sentences))


class Novel(BaseModel):
    title: str = ""
    author: str = "Novelopment 0.1"
    synopsis: str = ""
    chapters: list[Chapter] = []

    def new_chapter(self, **kwargs) -> Chapter:
        chapter = Chapter(**kwargs)
        self.chapters.append(chapter)
        return chapter

    def print(self) -> None:
        print(self.title)
        print(f"By {self.author}\n")
        print(self.synopsis)
        for chapter in self.chapters:
            chapter.print()


class ConnectorType(Enum):
    COMPLEMENTIZER = nlg.Feature.COMPLEMENTISER
    CUE_PHRASE = nlg.Feature.CUE_PHRASE
    CONJUNCTION = nlg.Feature.CONJUNCTION


class ConnectedPhrase(BaseModel):
    phrases: list["Sentence"] = []
    connector: str = "and"
    connector_type: ConnectorType = ConnectorType.CONJUNCTION


class Sentence(BaseModel):
    time: Optional[Union[datetime, date]]
    subject: Optional[Union[Actor, NovelCommit, str]]
    subject_determiner: Optional[str]
    predicate: str
    complements: List[Union[Actor, NovelCommit, str]] = []
    tense: Optional[nlg.Tense]
    connected_phrases: List[ConnectedPhrase] = []

    def get_tense(self):
        if self.tense:
            return self.tense
        if self.time and self.time > date.today():
            return nlg.Tense.FUTURE
        if self.time and self.time < date.today():
            return nlg.Tense.PAST
        return nlg.Tense.PRESENT


ConnectedPhrase.update_forward_refs()
