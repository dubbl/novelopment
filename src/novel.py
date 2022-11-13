from pydantic import BaseModel


class Chapter(BaseModel):
    title: str = ""
    paragraphs: list[str] = []

    def print(self) -> None:
        print(self.title)
        for paragraph in self.paragraphs:
            print(paragraph)


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
