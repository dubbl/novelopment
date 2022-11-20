from collections import Counter
import logging
import random

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
                chapter.paragraphs[-1].append(sentence)


def realize_sentence(sentence: Sentence):
    subject_word = get_word(sentence.subject)
    subject_word = nlg_factory.createNounPhrase(subject_word)
    if isinstance(sentence.subject, str):
        subject_word.setDeterminer("the")

    predicate = lexicon.getWord(sentence.predicate, nlg.LexicalCategory.VERB)

    complement_word = get_word(sentence.complement)
    complement_word = lexicon.getWord(complement_word, nlg.LexicalCategory.NOUN)

    p = nlg_factory.createClause()
    p.setTense(sentence.get_tense())
    p.setSubject(subject_word)
    p.setVerb(predicate)
    p.setComplement(complement_word)
    pp = nlg_factory.createPrepositionPhrase()
    pp.setPreposition("in")
    pp.addComplement(sentence.time.isoformat())
    p.addComplement(pp)
    return realiser.realiseSentence(p)


def get_word(value):
    if isinstance(value, str):
        if value in synonyms:
            return random.choice(synonyms[value])
        return value
    if isinstance(value, Actor):
        return value.name
    return value
