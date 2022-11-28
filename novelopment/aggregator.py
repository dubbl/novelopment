from itertools import groupby

from novel import ConnectedPhrase, Novel

MAX_CONJUNCTIONS: int = 5


def aggregate(novel: Novel):
    for chapter in novel.chapters:
        new_content = []
        for sentences in chapter.content:
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
                if len(grouped_sentences) == 1:
                    aggregated_sentences.append(grouped_sentences[0])
                    continue
                start_sentence = None
                for i, sentence in enumerate(grouped_sentences):
                    if not sentence.connected_phrase:
                        start_sentence = sentence
                        break
                    aggregated_sentences.append(sentence)
                if not start_sentence:
                    # all sentences already have connected phrases
                    continue
                start_sentence.connected_phrase = ConnectedPhrase(
                    phrases=grouped_sentences[i + 1 : i + MAX_CONJUNCTIONS],
                )
                aggregated_sentences.append(start_sentence)
            new_content.append(aggregated_sentences)
        chapter.content = new_content
