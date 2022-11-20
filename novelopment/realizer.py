from collections import Counter
import logging
import random
from typing import Optional

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
            skip = False
            for i, sentence in enumerate(paragraph_content):
                if skip:
                    # current sentence was already included by previous one
                    skip = False
                    continue
                next_sentence = None
                if len(paragraph_content) > i + 1:
                    next_sentence = paragraph_content[i + 1]
                sentence, skip = realize_sentence(
                    sentence,
                    next_sentence=next_sentence,
                )
                realized_sentence = realiser.realiseSentence(sentence)
                chapter.paragraphs[-1].append(realized_sentence)


def realize_sentence(sentence: Sentence, next_sentence: Optional[Sentence] = None):
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
    if sentence.time:
        pp = nlg_factory.createPrepositionPhrase()
        pp.setPreposition("in")
        pp.addComplement(sentence.time.isoformat())
        p.addPostModifier(pp)

    included_next = False
    if next_sentence and sentence.time == next_sentence.time:
        next_sentence.time = None
        next_sentence.tense = sentence.get_tense()
        p2, _ = realize_sentence(next_sentence)
        p2.setFeature(nlg.Feature.COMPLEMENTISER, "when")
        p.addComplement(p2)
        included_next = True

    return p, included_next


def get_word(value):
    if isinstance(value, str):
        if value in synonyms:
            return random.choice(synonyms[value])
        return value
    if isinstance(value, Actor):
        return value.name
    return value
