
from pygraph.classes.digraph import digraph as pydigraph
from pagerank_weighted import pagerank_weighted as pagerank
from pagerank_weighted import pagerank_weighted_scipy as pagerank_scipy
from textcleaner import tokenize_by_sentences
from math import log10

DEBUG = False
# Methods for PageRank
PAGERANK_MANUAL = 0
PAGERANK_SCIPY = 1

# Types of summarization
SENTENCE = 0
WORD = 1

def textrank(text, summarize_by=SENTENCE, method=PAGERANK_MANUAL, summary_length=0.2):
    if summarize_by == SENTENCE:
        return textrank_by_sentence(text, method, summary_length)
    else:
        return textrank_by_word(text, method, summary_length)


def textrank_by_sentence(text, method=PAGERANK_MANUAL, summary_length=0.2):
    # Gets a dict of processed_sentence -> original_sentences
    tokens = tokenize_by_sentences(text)

    # Creates the graph and calculates the similarity coefficient for every pair of nodes.
    graph = get_graph(tokens.keys())
    set_graph_edge_weights(graph)

    # Ranks the tokens using the PageRank algorithm. Returns dict of sentence -> score
    scores = pagerank(graph) if method == PAGERANK_MANUAL else pagerank_scipy(graph)

    # Extracts the most important tokens.
    extracted_tokens = extract_tokens(graph.nodes(), scores, summary_length)

    # Sorts the extracted sentences by apparition order in the original text.
    summary = sort_by_apparition(extracted_tokens, tokens, text)

    return "\n".join(summary)


def sort_by_apparition(extracted_tokens, tokens, text):
    summary = []

    for extracted in extracted_tokens:
        original_sentence = tokens[extracted]
        try:
            index = text.index(original_sentence)
            if DEBUG:
                summary.append((original_sentence, index, extracted_tokens[extracted]))
            else:
                summary.append((original_sentence, index))

        except ValueError:
            print "ERROR: sentence not found: " + original_sentence

    summary.sort(key=lambda t: t[1])
    if DEBUG:
        debug_info = lambda item: "({0:.4f}) : {1}".format(item[2], item[0])
        return [debug_info(item) for item in summary]
    return [item[0] for item in summary]


def extract_tokens(sentences, scores, summary_length):
    sentences.sort(key=lambda s: scores[s], reverse=True)
    length = len(sentences) * summary_length
    return {sentences[i]: scores[sentences[i]] for i in range(int(length))}


def get_graph(sentences):
    graph = pydigraph()

    # Creates the graph.
    for sentence in sentences:
        graph.add_node(sentence)

    return graph


def set_graph_edge_weights(graph):
    for sentence_1 in graph.nodes():
        for sentence_2 in graph.nodes():
            if sentence_1 == sentence_2:
                continue

            edge_1 = (sentence_1, sentence_2)
            edge_2 = (sentence_2, sentence_1)

            if graph.has_edge(edge_1) or graph.has_edge(edge_2):
                continue

            similarity = get_similarity(sentence_1, sentence_2)

            graph.add_edge(edge_1, similarity)
            graph.add_edge(edge_2, similarity)


def get_similarity(s1, s2):

    words_sentence_one = s1.split()
    words_sentence_two = s2.split()

    common_word_count = get_common_word_count(words_sentence_one, words_sentence_two)

    log_s1 = log10(len(words_sentence_one))
    log_s2 = log10(len(words_sentence_two))

    if log_s1 + log_s2 == 0:
        return 0

    return common_word_count / (log_s1 + log_s2)


def get_common_word_count(words_sentence_one, words_sentence_two):
    words_set = set(words_sentence_two)
    return sum(1 for w in words_sentence_one if w in words_set)


def textrank_by_word(text, method, summary_length):
    pass



def get_test_graph(path):
    """Method to run test on the interpreter """
    # TODO: delete this method when no longer needed
    with open(path) as file:
        text = file.read()

    # Gets a dict of processed_sentence -> original_sentences
    tokens = tokenize_by_sentences(text)

    # Creates the graph and calculates the similarity coefficient for every pair of nodes.
    graph = get_graph(tokens.keys())
    set_graph_edge_weights(graph)

    return graph
    # Ranks the tokens using the PageRank algorithm.
    # return pagerank_scipy(graph)