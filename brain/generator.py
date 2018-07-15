import random

from brain.conjugator import conjugator

SENTENCE_PATTERNS = [
    "[adv_time] [,] [adj_subj] subj [prep_subj] [adv_manner] vp [adv_place]",
    "[adv_time] [,] [adj_subj] subj [prep_subj] vp [adv_manner] [adv_place]",
    "[adv_place] [,] [adj_subj] subj [prep_subj] [adv_manner] vp [adv_time]",
    "[adv_place] [,] [adj_subj] subj [prep_subj] vp [adv_manner] [adv_time]",

    "[adj_subj] subj [prep_subj] vp [adj_sc] sc [prep_sc]",

    "[adv_time] [,] [adj_subj] subj [prep_subj] [adv_manner] vp [adj_do] do [prep_do] [adv_place]",
    "[adv_time] [,] [adj_subj] subj [prep_subj] vp [adj_do] do [prep_do] [adv_manner] [adv_place]",
    "[adv_place] [,] [adj_subj] subj [prep_subj] [adv_manner] vp [adj_do] do [prep_do] [adv_time]",
    "[adv_place] [,] [adj_subj] subj [prep_subj] vp [adj_do] do [prep_do] [adv_manner] [adv_time]",
    "[adv_time] [,] [adj_subj] subj [prep_subj] [adv_manner] vp [adj_do] do [prep_do] [adj_io] io [prep_io] [adv_place]",
    "[adv_time] [,] [adj_subj] subj [prep_subj] vp [adj_do] do [prep_do] [adj_io] io [prep_io] [adv_manner] [adv_place]",
    "[adv_place] [,] [adj_subj] subj [prep_subj] [adv_manner] vp [adj_do] do [prep_do] [adj_io] io [prep_io] [adv_time]",
    "[adv_place] [,] [adj_subj] subj [prep_subj] vp [adj_do] do [prep_do] [adj_io] io [prep_io] [adv_manner] [adv_time]",

    "[adv_time] [,] [adj_subj] subj [prep_subj] [adv_manner] vp [adj_do] do [adj_io] io [prep_io] [adj_oc] oc [adv_place]",
    "[adv_time] [,] [adj_subj] subj [prep_subj] vp [adj_do] do [adj_io] io [prep_io] [adj_oc] oc [adv_manner] [adv_place]",
    "[adv_place] [,] [adj_subj] subj [prep_subj] [adv_manner] vp [adj_do] do [adj_io] io [prep_io] [adj_oc] oc [adv_time]",
    "[adv_place] [,] [adj_subj] subj [prep_subj] vp [adj_do] do [adj_io] io [prep_io] [adj_oc] oc [adv_manner] [adv_time]"
]


def get_valid_patterns(keys):
    return [x for x in SENTENCE_PATTERNS[:]
            if all(y in
                   [z[1:-1] for z in x.split() if z.startswith('[') and z.endswith(']')] +
                   [w for w in x.split() if not (w.startswith('[') and w.endswith(']'))]
                   for y in keys)
            and
            set([y for y in x.split() if not (y.startswith('[') and y.endswith(']'))]).issubset(keys)]


def generate_string_from_list(list):
    if len(list) > 2:
        return ", ".join(list[:-1]) + ", and " + list[len(list) - 1]
    elif len(list) == 2:
        return list[0] + " and " + list[1]
    elif len(list) == 1:
        return list[0]
    else:
        return ""


def apply_pattern(pattern, params, modifiers, capitalize):
    # print('In apply_pattern, params:', params)
    split_pattern = pattern.split()
    prev_status = False
    curr_sentence = ""
    for x in split_pattern:
        if x.startswith('[') and x.endswith(']'):
            x = x[1:len(x) - 1]
        if x in params:
            if curr_sentence is "":
                if not params[x][0].isupper() and capitalize:
                    curr_sentence = params[x].capitalize()
                else:
                    curr_sentence = params[x]
            else:
                if x == "vp":
                    curr_sentence = curr_sentence + " " + conjugator.conjugate(params[x],
                                                                               number=modifiers.get('subj_plurality'),
                                                                               person=modifiers.get('voice'),
                                                                               tense=modifiers.get('vp_tense'))
                elif x.startswith("adj") or x.startswith("adv"):
                    curr_sentence = curr_sentence + " " + generate_string_from_list(params[x])
                else:
                    curr_sentence = curr_sentence + " " + params[x]
            prev_status = True
        elif x is ',' and prev_status is True:
            curr_sentence = curr_sentence + ","
            prev_status = False
        else:
            prev_status = False
    return curr_sentence + "."


def get_point_of_view(noun):
    if noun.lower() == "i" or noun.lower() == 'my' or noun.lower() == 'our':
        return conjugator.FIRST_PERSON
    elif noun.lower() == "you" or noun.lower == 'your':
        return conjugator.SECOND_PERSON
    else:
        return conjugator.THIRD_PERSON


def generate_simple_sentence(params={}, modifiers={}, capitalize=True, default_sentence="I have no idea."):
    # print("params:", params)
    # print("modifiers: ", modifiers)
    if params == {} or modifiers == {}:
        return default_sentence
    return apply_pattern(random.choice(get_valid_patterns(params.keys())), params, modifiers, capitalize)


def generate_simple_question(subject, type):
    if type == 'confirmation':
        return subject + "?"
    else:
        return type.capitalize() + " " + conjugator.conjugate("be",
                                                              number=conjugator.SINGULAR if not
                                                              conjugator.plural(subject)[0] else
                                                              conjugator.PLURAL,
                                                              person=conjugator.THIRD_PERSON,
                                                              tense=conjugator.PRESENT_TENSE) + " " + subject + "?"
