from collections import Counter
from datetime import date, datetime
import logging
import random

from pydantic import BaseModel
import simplenlg as nlg

from lexicon import synonyms
from miner import Actor
from novel import ConnectorType, Novel, Sentence

log = logging.getLogger("novelopment.realizer")

lexicon = nlg.lexicon.Lexicon.getDefaultLexicon()
nlg_factory = nlg.NLGFactory(lexicon)
realiser = nlg.realiser.Realiser(lexicon)


subject_counter = Counter()


def realize(novel: Novel):
    for chapter in novel.chapters:
        for paragraph_content in chapter.content:
            chapter.paragraphs.append([])
            for sentence in paragraph_content:
                sentence = realize_sentence(sentence)
                realized_sentence = realiser.realiseSentence(sentence)
                chapter.paragraphs[-1].append(realized_sentence)


def realize_sentence(sentence: Sentence):
    p = nlg_factory.createClause()
    p.setTense(sentence.get_tense())

    subject_word = get_word(sentence.subject)
    subject_word = nlg_factory.createNounPhrase(subject_word)
    if isinstance(sentence.subject, str):
        subject_word.setDeterminer("the")
    else:
        subject_word.setFeature(nlg.Feature.PERSON, nlg.Person.SECOND)
    p.setSubject(subject_word)

    predicate = lexicon.getWord(sentence.predicate, nlg.LexicalCategory.VERB)
    p.setVerb(predicate)

    complement_cpe = nlg.framework.CoordinatedPhraseElement()
    for complement in sentence.complements:
        complement_word = get_word(complement)
        complement_cpe.addCoordinate(
            nlg_factory.createNounPhrase(complement_word),
        )
    p.setComplement(complement_cpe)
    if sentence.time:
        pp = nlg_factory.createPrepositionPhrase()
        pp.setPreposition("on")
        pp.addComplement(get_word(sentence.time))
        if random.getrandbits(1):
            p.addPostModifier(pp)
        else:
            p.addFrontModifier(pp)
    if not sentence.connected_phrase:
        return p
    connected_phrase = sentence.connected_phrase
    if connected_phrase.connector_type == ConnectorType.CONJUNCTION:
        cpe = nlg.framework.CoordinatedPhraseElement()
        cpe.addCoordinate(p)
        for phrase in connected_phrase.phrases:
            phrase = realize_sentence(phrase)
            cpe.addCoordinate(phrase)
        return cpe
    if connected_phrase.connector_type == ConnectorType.COMPLEMENTIZER:
        for phrase in connected_phrase.phrases:
            phrase = realize_sentence(phrase)
            phrase.setFeature(
                nlg.Feature.COMPLEMENTISER,
                connected_phrase.connector,
            )
            p.addComplement(phrase)
            return p


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
