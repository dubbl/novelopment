from itertools import groupby, zip_longest

from novel import ConnectedPhrase, ConnectorType, Novel


def aggregate(novel: Novel):
    for chapter in novel.chapters:
        chapter.content = aggregate_complements(chapter.content)
        chapter.content = aggregate_on_time(chapter.content)


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
            + str(s.connected_phrases),
        ):
            grouped_sentences = list(group)
            start_sentence = grouped_sentences[0]
            for grouped_sentence in grouped_sentences[1:]:
                start_sentence.complements.extend(grouped_sentence.complements)
            aggregated_sentences.append(start_sentence)
        aggregated_content.append(aggregated_sentences)
    return aggregated_content


def aggregate_on_time(content):
    """
    Aggregates sentences that happen around the same time using "while"
    """
    aggregated_content = []
    for sentences in content:
        aggregated_sentences = []
        for _, group in groupby(sentences, key=lambda s: str(s.time)):
            grouped_sentences = list(group)
            if len(grouped_sentences) == 1:
                aggregated_sentences.extend(grouped_sentences)
                continue
            first_pair = True
            for start_sentence, follow_sentence in grouper(grouped_sentences, 2):
                if first_pair:
                    first_pair = False
                else:
                    start_sentence.connected_phrases.append(
                        ConnectedPhrase(
                            connector="meanwhile",
                            connector_type=ConnectorType.CUE_PHRASE,
                        )
                    )
                    # remove time, as it is contained in previous start_sentence
                    start_sentence.tense = start_sentence.get_tense()
                    start_sentence.time = None
                if not follow_sentence:
                    aggregated_sentences.append(start_sentence)
                    break
                # remove time, as it is contained in start_sentence
                follow_sentence.tense = follow_sentence.get_tense()
                follow_sentence.time = None
                start_sentence.connected_phrases.append(
                    ConnectedPhrase(
                        phrases=[follow_sentence],
                        connector="while",
                        connector_type=ConnectorType.COMPLEMENTIZER,
                    )
                )
                aggregated_sentences.append(start_sentence)

        aggregated_content.append(aggregated_sentences)
    return aggregated_content


def grouper(iterable, n):
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=None)
