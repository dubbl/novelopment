from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union

from jinja2 import Environment, BaseLoader
from pydantic import BaseModel
import simplenlg as nlg

from miner import Actor, NovelCommit

jinja_env = Environment(loader=BaseLoader)
chapter_template = """
<h2>{{ title }}</h2>
{% for paragraph in paragraphs %}
    <p>
        {% for sentence in paragraph %}
            {{ sentence }}
        {% endfor %}
    </p>
{% endfor %}
"""

title_template = """
<h1>{{ title }}</h1>

<p>A robotic novel by {{ author }}<p>
"""


class Chapter(BaseModel):
    title: str = ""
    paragraphs: list[list[str]] = []

    content: list[list["Sentence"]] = []

    def print(self) -> None:
        print(self.title)
        for sentences in self.paragraphs:
            print(" ".join(sentences))

    def to_html(self) -> str:
        template = jinja_env.from_string(chapter_template)
        return template.render(**self.dict())


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

    def to_html(self) -> str:
        template = jinja_env.from_string(title_template)
        return template.render(**self.dict())


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
    time_expression: Optional[str]
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
