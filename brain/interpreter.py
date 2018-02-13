import nltk
from nltk.tag.stanford import CoreNLPPOSTagger

DEFAULT_TAGS = ['NNP', 'NNPS', 'NN', 'NNS']
KEYWORD_TAGS = DEFAULT_TAGS[:]
KEYWORD_TAGS.extend(['VBG', 'PRP', 'PRP$', 'WP', 'WP$', 'WRB', 'WDT'])

STANFORD_TAGGER = CoreNLPPOSTagger('http://localhost:9000/')

def combine_similar(input, tags):
    output = []
    curr = []
    tag = ""
    for x in input:
        if x[1] not in tags:
            if len(curr) > 0:
                output.append((" ".join([x[0] for x in curr]), tag))
                curr[:] = []
                tag = ""
            output.append(x)
        elif x[1] == tag:
            curr.append(x)
        else:
            if len(curr) > 0:
                output.append((" ".join([x[0] for x in curr]), tag))
                curr[:] = []
            tag = x[1]
            curr.append(x)
    if len(curr) > 0:
        output.append((" ".join([x[0] for x in curr]), tag))
    return output


def tokenize_and_tag(input, tags=DEFAULT_TAGS):
    return [combine_similar(y, tags) for y in [nltk.pos_tag(nltk.word_tokenize(x)) for x in nltk.sent_tokenize(input)]]

def stanford_pos(input, tags=DEFAULT_TAGS):
    return [combine_similar(y, tags) for y in [STANFORD_TAGGER.tag(nltk.word_tokenize(x)) for x in nltk.sent_tokenize(input)]]


def get_keywords(input, tags=KEYWORD_TAGS):
    return [[y[0] for y in x if y[1] in tags] for x in input]

def consolidate(input):
    output = []
    for x in input:
        output.extend(x)
    return output

def get_sentence_structure(input):
    return ["-".join([y[1] for y in x if y[1] != '.']) for x in input]  