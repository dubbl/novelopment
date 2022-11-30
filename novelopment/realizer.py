import logging
import random

import simplenlg as nlg

from lexicon import get_word
from miner import Actor
from novel import ConnectorType, Novel, Sentence

log = logging.getLogger("novelopment.realizer")

lexicon = nlg.lexicon.Lexicon.getDefaultLexicon()
nlg_factory = nlg.NLGFactory(lexicon)
realiser = nlg.realiser.Realiser(lexicon)


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

    if sentence.subject:
        subject_word = get_word(sentence.subject)
        subject_word = nlg_factory.createNounPhrase(subject_word)
        if sentence.subject_determiner:
            subject_word.setDeterminer(sentence.subject_determiner)
        p.setSubject(subject_word)

    predicate = get_word(sentence.predicate)
    predicate = lexicon.getWord(predicate, nlg.LexicalCategory.VERB)
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
    if sentence.time_expression:
        p.setFeature(nlg.Feature.CUE_PHRASE, sentence.time_expression)
    if not sentence.connected_phrases:
        return p
    for connected_phrase in sentence.connected_phrases:
        if connected_phrase.connector_type == ConnectorType.CONJUNCTION:
            cpe = nlg.framework.CoordinatedPhraseElement()
            cpe.addCoordinate(p)
            for phrase in connected_phrase.phrases:
                phrase = realize_sentence(phrase)
                cpe.addCoordinate(phrase)
            p = cpe
        if connected_phrase.connector_type == ConnectorType.COMPLEMENTIZER:
            for phrase in connected_phrase.phrases:
                phrase = realize_sentence(phrase)
                phrase.setFeature(
                    nlg.Feature.COMPLEMENTISER,
                    get_word(connected_phrase.connector),
                )
                p.addComplement(phrase)
        if connected_phrase.connector_type == ConnectorType.CUE_PHRASE:
            p.setFeature(
                nlg.Feature.CUE_PHRASE,
                get_word(connected_phrase.connector) + ",",
            )
    return p
