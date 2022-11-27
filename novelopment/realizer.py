from collections import Counter
import logging
import random
from typing import Optional

from pydantic import BaseModel
import simplenlg as nlg

from lexicon import synonyms
from miner import Actor
from novel import Novel, Sentence

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
    subject_word = get_word(sentence.subject)
    subject_word = nlg_factory.createNounPhrase(subject_word)
    if isinstance(sentence.subject, str):
        subject_word.setDeterminer("the")
    else:
        subject_word.setFeature(nlg.Feature.PERSON, nlg.Person.SECOND)

    predicate = lexicon.getWord(sentence.predicate, nlg.LexicalCategory.VERB)

    complement_word = None
    if sentence.complement:
        complement_word = get_word(sentence.complement)
        complement_word = lexicon.getWord(
            complement_word,
            nlg.LexicalCategory.NOUN,
        )

    p = nlg_factory.createClause()
    p.setTense(sentence.get_tense())
    p.setSubject(subject_word)
    p.setVerb(predicate)
    if complement_word:
        p.setComplement(complement_word)
    if sentence.time:
        pp = nlg_factory.createPrepositionPhrase()
        pp.setPreposition("in")
        pp.addComplement(sentence.time.isoformat())
        p.addPostModifier(pp)
    if sentence.connected_phrase:
        # TODO: handle connection types other than conjunctions
        cpe = nlg.framework.CoordinatedPhraseElement()
        cpe.addCoordinate(p)
        for phrase in sentence.connected_phrase.phrases:
            phrase = realize_sentence(phrase)
            cpe.addCoordinate(phrase)
        return cpe
    return p


def get_word(value):
    if isinstance(value, str):
        if value in synonyms:
            return random.choice(synonyms[value])
        return value
    elif isinstance(value, BaseModel):
        return value.to_word()
    return str(value)
