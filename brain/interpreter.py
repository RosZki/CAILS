import nltk
from nltk.tag.stanford import CoreNLPPOSTagger
from nltk.parse.corenlp import CoreNLPParser
from pycorenlp import StanfordCoreNLP
from brain import memory
from brain.conjugator import conjugator
from brain.planner.sentence_planner import traverse_and_check

DEFAULT_TAGS = ['NNP', 'NNPS', 'NN', 'NNS']
KEYWORD_TAGS = DEFAULT_TAGS[:]
KEYWORD_TAGS.extend(['VBG', 'PRP', 'PRP$', 'WP', 'WP$', 'WRB', 'WDT'])

STANFORD_TAGGER = CoreNLPPOSTagger('http://localhost:9000/')
STANFORD_SERVER = StanfordCoreNLP('http://localhost:9000/')
STANFORD_PARSER = CoreNLPParser('http://localhost:9000/')


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
    return [combine_similar(y, tags) for y in
            [STANFORD_TAGGER.tag(nltk.word_tokenize(x)) for x in nltk.sent_tokenize(input)]]


def f(input):
    return STANFORD_SERVER.annotate(input, properties={'annotators': 'tokenize,ssplit,pos,parse,coref',
                                                       'outputFormat': 'json'})


# def c(input, tags=DEFAULT_TAGS):
#    final = []
#    tokens_per_sent = [y['tokens'] for y in [x for x in
#        STANFORD_SERVER.annotate(input, properties={'annotators': 'tokenize,ssplit,pos,parse,coref', 'outputFormat':'json'})['sentences']
#    ]]
#    for tokens in tokens_per_sent:
#        final.append([(x['word'],x['pos']) for x in tokens])
#    return [combine_similar(x,tags) for x in final]


def get_keywords(input, tags=KEYWORD_TAGS):
    return [[y[0] for y in x if y[1] in tags] for x in input]


def consolidate(input):
    output = []
    for x in input:
        output.extend(x)
    return output


def get_sentence_structure(input):
    return ["-".join([y[1] for y in x if y[1] != '.']) for x in input]


def extract_question(input):
    a = 1

def get_labels(tree):
    return [x.label() if type(x) == nltk.Tree else x for x in tree] if type(tree) == nltk.Tree else []


def extract_all(tree, tag, list_ent=None, old=None):
    PHRASE_NODES = ["ADJP", "ADVP", "CONJP", "FRAG", "INTJ", "LST",
                    "NAC", "NP", "NX", "PP", "PRN", "PRT", "QP",
                    "RRC", "UCP", "VP", "WHADJP", "WHAVP", "WHNP",
                    "WHPP", "X", "S", "SBAR", "SBARQ", "SINV", "SQ"]
    if list_ent == None:
        list_ent = []
    l = get_labels(tree)
    if tag in l:
        for ind, x in enumerate(l):
            if x == tag:
                extract_all(tree[ind], tag, list_ent=list_ent, old=tree[ind])
            elif x in PHRASE_NODES:
                extract_all(tree[ind], tag, list_ent=list_ent, old=old)
    elif len(set(l) & set(PHRASE_NODES)) > 0:
        for ind, x in enumerate(l):
            if x in PHRASE_NODES:
                extract_all(tree[ind], tag, list_ent=list_ent, old=old)
    else:
        if old is not None:
            list_ent.append(old)
    return [" ".join(x.leaves()) for x in list_ent]


def extract_info(input):
    IS_LIST = ['be', 'is', 'are', 'was', 'were', 'am']
    t = list(STANFORD_PARSER.raw_parse(input))[0][0]
    subjs = []
    vb = ""
    vp_np = []
    vp_jj = []
    if t.label() == "S":
        subjs = extract_all(t[0], "NP", old=t[0])
        vb = t[1][0][0]
        vb = conjugator.base_form(vb)
        vp_np = extract_all(t[1], "NP")
        vp_jj = extract_all(t[1], "JJ")
        vp = " ".join(t[1].leaves())
        print("SUBJ:", subjs)
        print("VB:", vb)
        print("VP_NPL", vp_np)
        print("VP_JJ:", vp_jj)
        if vb in IS_LIST:
            for x in subjs:
                for y in vp_np:
                    memory.add_to_character_memory(x, 'IsA', y)
                for y in vp_jj:
                    memory.add_to_character_memory(x, 'HasProperty', y)
        else:
            memory.add_to_event_memory(subjs,vb,vp)
    else:
        #process question
        #q = t[0]
        #vb = t[1][0][0]
        #vb = conjugator.get_base_form(vb)
        #vp = " ".join(t[1][1].leaves())
        #get_keywords(stanford_pos(vp))
        #if vb not in IS_LIST:
        #    if 'events' in memory.CURRENT_MEMORY.keys():
        #        mem = [x for x in memory.CURRENT_MEMORY['events'] if x['verb'] == vb]
        #    else:
        #        mem = []
        #    cont = [x for x in memory.CURRENT_CONTEXT['events'] if x ['verb'] == vb]
        #
        #
        #else:
        #    # process w is ___ question
        a = 1

    print(memory.CURRENT_MEMORY)
    return [subjs,vb,vp_np,vp_jj]
