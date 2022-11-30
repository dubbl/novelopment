from datetime import date, datetime
from enum import Enum
from typing import List, Optional, Union

from ebooklib import epub
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

    def to_epub(self, output):
        book = epub.EpubBook()

        # set metadata
        book.set_title(self.title)
        book.set_language("en")

        book.add_author(self.author)
        book.add_author("Hauke Lübbers", role="ill", uid="coauthor")

        title = epub.EpubHtml(
            title=self.title,
            file_name="cover.xhtml",
            lang="en",
        )
        title.content = self.to_html()
        book.add_item(title)
        # create chapter
        book_chapters = []
        for i, chapter in enumerate(self.chapters):
            c = epub.EpubHtml(
                title=chapter.title,
                file_name=f"chapter_{i}.xhtml",
                lang="en",
            )
            c.content = chapter.to_html()
            # add chapter
            book.add_item(c)
            book_chapters.append(c)

        # define CSS style
        style = "body {color: white;}"
        nav_css = epub.EpubItem(
            uid="style_nav",
            file_name="style/nav.css",
            media_type="text/css",
            content=style,
        )
        book.add_item(nav_css)

        # define Table Of Contents
        book.toc = book_chapters

        # add default NCX and Nav file
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # basic spine
        book.spine = [title, "nav", *book_chapters]

        # write to the file
        epub.write_epub(output, book, {})


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
