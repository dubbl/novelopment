from datetime import date
import random

from pydantic import BaseModel

synonyms: dict[str, list[str]] = {
    "actor": ["person", "human", "developer", "contributor", "individual"],
    "book": ["book", "story", "novel", "adventure", "tale", "saga", "coverage"],
    "author": ["author", "write", "create", "add", "craft", "compose"],
    "while": ["while", "whilst", "when"],
    "meanwhile": ["meanwhile", "at the same time", "concurrently", "simultaneously"],
    "they": ["they", "they themselves", "the very same one"],
}


def get_word(value):
    if isinstance(value, str):
        if value in synonyms:
            return random.choice(synonyms[value])
        return value
    elif isinstance(value, BaseModel):
        return value.to_word()
    elif isinstance(value, date):
        return value.strftime(f"%A, %B {ordinal(value.day)} %Y")
    return str(value)


def ordinal(n):
    return f'{n}{"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4]}'
