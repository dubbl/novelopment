from itertools import groupby

from novel import ConnectedPhrase, Novel


def aggregate(novel: Novel):
    for chapter in novel.chapters:
        chapter.content = aggregate_complements(chapter.content)


def aggregate_complements(content):
    """
    Aggregates sentences that only differ on their complements into one
    """
    aggregated_content = []
    for sentences in content:
        aggregated_sentences = []
        for _, group in groupby(
            sentences,
            key=lambda s: str(s.subject)
            + str(s.predicate)
            + str(s.time)
            + str(s.tense)
            + str(s.connected_phrase),
        ):
            grouped_sentences = list(group)
            start_sentence = grouped_sentences[0]
            for grouped_sentence in grouped_sentences[1:]:
                start_sentence.complements.extend(grouped_sentence.complements)
            aggregated_sentences.append(start_sentence)
        aggregated_content.append(aggregated_sentences)
    return aggregated_content
