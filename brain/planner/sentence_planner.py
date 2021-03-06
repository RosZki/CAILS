import random

import brain.api.conceptnet as conceptnet
from brain import memory
from brain.conjugator import conjugator
from brain.generator import generate_simple_sentence
from brain.generator import generate_string_from_list

RELS_GEN = {
    'IsA': ["a "],
    'PartOf': ["a part of "],
    'HasA': ["a "],
    'UsedFor': ["for "],
    'CapableOf': [""],
    'AtLocation': ["commonly found at "],
    'HasProperty': [""],
    'type': ["a "]
}

KEYS_TO_REMOVE = ['name', 'personality', 'knowledge', 'params']

def collate_percentages(dict_perc):
    prev = 0
    for x in dict_perc.keys():
        curr = dict_perc[x] + prev
        dict_perc[x] = curr
        prev = curr
    return dict_perc

def check_if_duplicate(plan, plans):
    for x in plans:
        if set(x['params'].items()) == set(plan['params'].items()) and set(x['modifiers'].items()) == set(
                plan['modifiers'].items()):
            return True
    return False


def chain_access(list, keys, default={}):
    out = list
    try:
        for key in keys:
            out = out[key]
        return out
    except (AttributeError, KeyError, TypeError, IndexError) as e:
        return default


def plan_from_conceptnet(subject, num_sentences):
    REL_TEMP = list(RELS_GEN.keys())
    plans = []
    sent_left = num_sentences
    while sent_left > 0 and len(REL_TEMP) > 0:
        choices = []
        while len(choices) == 0 and len(REL_TEMP) > 0:
            random_rel = random.choice(REL_TEMP)
            choices = conceptnet.query(subject, 'node', random_rel)
            REL_TEMP.remove(random_rel)
        if len(choices) == 0:
            if len(plans) > 0:
                return plans
            else:
                return [{'params': {}, 'modifiers': {}}]
        if len(choices) >= sent_left:
            selection = random.sample(choices, sent_left)
        else:
            selection = choices

        sent_left = sent_left - len(choices)

        if random_rel == 'HasA':
            vp = 'have'
        elif random_rel == 'CapableOf':
            vp = 'can'
        else:
            vp = 'be'

        if selection is not None:
            random.shuffle(selection)

        for x in selection:
            text = random.choice(RELS_GEN[random_rel])
            if text == 'a ':
                if conjugator.plural(x[1])[0]:
                    text == ""
            plans.append(generate_sentence_plan(x, text, vp))

    return plans


def plan_introduction_from_context():
    pl = []
    for evt in memory.CURRENT_CONTEXT['events']:
        pl.append(plan_from_event('actors', evt))

    return (-1, pl)

def get_introductory_plan():
    t = []
    t2 = []
    out = []
    for indx, x in enumerate(memory.PLAN):
        num_l = x[2] - len(memory.PROGRESS[indx])

        if x[0] == 'location':
            if x[3]:
                if num_l == 1:
                    t.append("at least one location")
                else:
                    t.append("at least " + str(num_l) + " locations")
            else:
                if num_l == 1:
                    t.append("one location")
                else:
                    t.append(str(num_l) + " locations")
        elif x[0] == 'person':
            if x[3]:
                if x[2] == 1:
                    t.append("at least one person")
                else:
                    t.append("at least " + str(num_l) + " people")
            else:
                if num_l == 1:
                    t.append("one person")
                else:
                    t.append(str(num_l) + " people")
        else:
            if x[3]:
                if num_l == 1:
                    t.append("at least one kind of " + x[0])
                else:
                    t.append("at least " + str(num_l) + " kinds of " + x[0])
            else:
                if num_l == 1:
                    t.append("one kind of " + x[0])
                else:
                    t.append(str(num_l) + " kinds of " + x[0])
        if len(memory.PROGRESS[indx]) > 0:
            t2.append((x[0], memory.PROGRESS[indx]))

    out.append("The characters (including you) need to decide on " + generate_string_from_list(t) + ".")
    for x in t2:
        out.append("You have already decided on " + generate_string_from_list(x[1]) + " for " + x[0] + ".")

    return (-1, " ".join(out))

def plan_from_event(key, event_info, subject="", c_s_n=""):
    init_plans = {'params': {
        'subj': generate_string_from_list(["I"  if x == c_s_n else x for x in event_info['actors']]),
        'vp': event_info['verb'],
        'sc': event_info['sc']
    }, 'modifiers': {
        'subj_plurality': conjugator.PLURAL if len(event_info['actors']) > 1 else conjugator.SINGULAR,
        'vp_tense': conjugator.PAST_TENSE,
        'voice': conjugator.FIRST_PERSON if c_s_n in event_info['actors'] else conjugator.THIRD_PERSON
    }}
    if key == 'location':
        return {'params': {
            'subj': event_info[key],
            'vp': 'be',
            'sc': "where " + generate_simple_sentence(init_plans['params'], init_plans['modifiers'])[:-1]
        }, 'modifiers': {
            'subj_plurality': conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.THIRD_PERSON
        }}
    elif key == 'actors':
        return init_plans
    elif key == 'others':
        return {'params': {
            'subj': subject,
            'vp': 'be',
            'sc': "there when " + generate_simple_sentence(init_plans['params'], init_plans['modifiers'])[:-1]
        }, 'modifiers': {
            'subj_plurality': conjugator.SINGULAR,
            'vp_tense': conjugator.PAST_TENSE,
            'voice': conjugator.THIRD_PERSON
        }}
    else:
        return {'params': {}, 'modifiers': {}}


def plan_from_memory(info, name, key="knowledge", subject="", c_s_n=""):
    # print(info, name, key, subject)
    if info == "events":
        context_info = chain_access([x for x in chain_access(memory.CURRENT_CONTEXT, [info]) if x['name'] == name], [0])
        memory_info = chain_access([x for x in chain_access(memory.CURRENT_MEMORY, [info]) if x['name'] == name], [0])
        if context_info == {}:
            return plan_from_event(key, memory_info, subject=subject, c_s_n=c_s_n)
        else:
            return plan_from_event(key, context_info, subject=subject, c_s_n=c_s_n)
    elif key == "knowledge":
        context_info = chain_access([x for x in chain_access(memory.CURRENT_CONTEXT, [info]) if x['name'] == name],
                                    [0, key, subject])
        memory_info = chain_access([x for x in chain_access(memory.CURRENT_MEMORY, [info]) if x['name'] == name],
                                   [0, key, subject])
        total_info = list(set(context_info.keys()).union(memory_info.keys()))
        if total_info == [] or total_info == {}:
            return {'params': {}, 'modifiers': {}}
        random_rel = random.choice(total_info)
        if random_rel == 'HasA':
            vp = 'have'
        else:
            vp = 'be'
        return generate_sentence_plan((subject, random.choice(
            chain_access(context_info, [random_rel], []) + chain_access(memory_info, [random_rel], []))),
                                      random.choice(RELS_GEN[random_rel]), vp)


    else:
        context_info = chain_access([x for x in chain_access(memory.CURRENT_CONTEXT, [info]) if x['name'] == name],
                                    [0, key])
        if key in RELS_GEN:
            text = random.choice(RELS_GEN[key])
        else:
            text = ""
        if type(context_info) == list:
            context_info = ", ".join(context_info)
        elif type(context_info) == dict:
            context_info = ""
        return {'params': {
            'subj': name,
            'vp': 'be',
            'sc': text + context_info
        }, 'modifiers': {
            'subj_plurality': conjugator.PLURAL if conjugator.plural(name)[0] else conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.THIRD_PERSON
        }}


def plan_randomly_from_memory(subject, num_sentences, c_s_n=""):
    rand_plans = []
    context_dir, opinion_dir_cont = traverse_and_check(subject, memory.CURRENT_CONTEXT, [], [], [])
    # print("cont: ", context_dir)
    for x in context_dir:
        if x[0] == 'events':
            pl = plan_from_memory(x[0], memory.CURRENT_CONTEXT[x[0]][x[1]]['name'], x[2], subject=subject, c_s_n=c_s_n)
            if not check_if_duplicate(pl, rand_plans):
                rand_plans.append(pl)
        else:
            y = [z for z in list(memory.CURRENT_CONTEXT[x[0]][x[1]].keys()) if z not in KEYS_TO_REMOVE]
            if len(y) < 1:
                break
            pl = plan_from_memory(x[0], memory.CURRENT_CONTEXT[x[0]][x[1]]['name'], random.choice(y), c_s_n=c_s_n)
            if not check_if_duplicate(pl, rand_plans):
                rand_plans.append(pl)

    # print("rand_plan_cont: ", plan_from_memory(rand[0], memory.CURRENT_CONTEXT[rand[0]][rand[1]]['name'], rand[2]))
    # print("op_cont: ", opinion_dir_cont)
    for x in opinion_dir_cont:
        pl = plan_from_memory(x[0], memory.CURRENT_CONTEXT[x[0]][x[1]]['name'], subject=subject, c_s_n=c_s_n)
        if not check_if_duplicate(pl, rand_plans):
            rand_plans.append(pl)
    # print("rand_plan_op_cont: ", chain_access(memory.CURRENT_CONTEXT, rand2))
    memory_dir, opinion_dir_mem = traverse_and_check(subject, memory.CURRENT_MEMORY, [], [], [])
    # print("mem: ", memory_dir)
    # print(memory_dir)
    for x in memory_dir:
        y = [z for z in list(memory.CURRENT_MEMORY[x[0]][x[1]].keys()) if z not in KEYS_TO_REMOVE]
        if len(y) < 1:
            break
        # print(x)
        # print(y)
        # print(memory.CURRENT_MEMORY)
        pl = plan_from_memory(x[0], memory.CURRENT_MEMORY[x[0]][x[1]]['name'], random.choice(y), c_s_n=c_s_n)
        if not check_if_duplicate(pl, rand_plans):
            rand_plans.append(pl)

    for x in opinion_dir_mem:
        pl = plan_from_memory(x[0], memory.CURRENT_MEMORY[x[0]][x[1]]['name'], subject=subject, c_s_n=c_s_n)
        if not check_if_duplicate(pl, rand_plans):
            rand_plans.append(pl)
    # print("context_dir:", context_dir)
    # print("opinion_dir_cont:", opinion_dir_cont)
    # print("memory_dir:", memory_dir)
    # print("opinion_dir_mem:", opinion_dir_mem)
    if len(rand_plans) > 0:
        if len(rand_plans) >= num_sentences:
            return random.sample(rand_plans, num_sentences)
        else:
            return rand_plans
    else:
        return []
        # print("rand_plan_cont: ", plan_from_me
        # print("op_mem: ", opinion_dir_mem)


def traverse_and_check(subject, tree, curr_dir, list_dir, opinion_dir, equal=True, arr=None):
    # print("curr_dir: ",curr_dir)
    # print("list_dir: ", list_dir)
    if type(tree) is dict:
        for key in list(tree.keys()):
            curr_dir.append(key)
            if equal:
                if type(key) == str and key.lower() == subject.lower():
                    opinion_dir.append(curr_dir[:])
            else:
                if type(key) == str and subject.lower() in key.lower():
                    opinion_dir.append(curr_dir[:])
            traverse_and_check(subject, tree[key], curr_dir, list_dir, opinion_dir)
            curr_dir.pop()
    elif type(tree) is list:
        for index, subtree in enumerate(tree):
            curr_dir.append(index)
            traverse_and_check(subject, subtree, curr_dir, list_dir, opinion_dir)
            curr_dir.pop()
    else:
        # print(tree, "vs.", subject)
        if equal:
            if type(tree) == str and subject.lower() == tree.lower():
                # print("Match!")
                # print("list_dir [before]:", list_dir)
                # print("curr_dir:", curr_dir)
                list_dir.append(curr_dir[:])
                # print("list_dir [after]:", list_dir)
                return list_dir, opinion_dir
        else:
            if type(tree) == str and subject.lower() in tree.lower():
                # print("Match!")
                # print("list_dir [before]:", list_dir)
                # print("curr_dir:", curr_dir)
                list_dir.append(curr_dir[:])
                # print("list_dir [after]:", list_dir)
                return list_dir, opinion_dir
    # print("pre-return: ",list_dir)
    return list_dir, opinion_dir


def generate_sentence_plan(choice, text, vp):
    if conjugator.plural(choice[1])[0] and text == "a ":
        text = ""
    if text == "a " and choice[1][0].lower() in ['a', 'e', 'i', 'o', 'u']:
        text = "an "

    return {'params': {
        'subj': choice[0],
        'vp': vp,
        'sc': text + choice[1]
    },
        'modifiers': {
            'subj_plurality': conjugator.PLURAL if conjugator.plural(choice[0])[0] else conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.THIRD_PERSON
        }}


def describe_subject(subject, num_sentences, c_s_n=""):
    # plans = plan_from_memory("characters", memory.CURRENT_CHARACTER, key="knowledge", subject=subject)
    # if len(plans) == 0 or plans[0]['params'] == {} or plans[0]['modifiers'] == {}:
    plans = plan_randomly_from_memory(subject, num_sentences, c_s_n=c_s_n)
    # plans = []
    if len(plans) < num_sentences:
        plans.extend(plan_from_conceptnet(subject, num_sentences - len(plans)))
    return plans


def get_current_goal():
    g = memory.get_curr_goal()
    if g[1] == "characters":
        if int(g[2]) - memory.get_curr_progress_num() == 1:
            if memory.get_curr_progress_num() > 0:
                sc = "to find one more person"
            else:
                sc = "to find one person"
        else:
            if memory.get_curr_progress_num() > 0:
                sc = "to find " + str(int(g[2]) - memory.get_curr_progress_num()) + " more people"
            else:
                sc = "to find " + str(int(g[2]) - memory.get_curr_progress_num()) + " people"
        return {'params': {
            'subj': "we",
            'vp': "need",
            'sc': sc
        },
            'modifiers': {
                'subj_plurality': conjugator.PLURAL,
                'vp_tense': conjugator.PRESENT_TENSE,
                'voice': conjugator.THIRD_PERSON
            }
        }
    elif g[1] == "location":
        if int(g[2]) - memory.get_curr_progress_num() == 1:
            if memory.get_curr_progress_num() > 0:
                sc = "to decide on one more location"
            else:
                sc = "to decide on a location"

        else:
            if memory.get_curr_progress_num() > 0:
                sc = "to decide on " + str(int(g[2]) - memory.get_curr_progress_num()) + " more locations"
            else:
                sc = "to decide on " + str(int(g[2]) - memory.get_curr_progress_num()) + " locations"
        return {'params': {
            'subj': "we",
            'vp': "need",
            'sc': sc
        },
            'modifiers': {
                'subj_plurality': conjugator.PLURAL,
                'vp_tense': conjugator.PRESENT_TENSE,
                'voice': conjugator.THIRD_PERSON
            }
        }
    else:
        if int(g[2]) - memory.get_curr_progress_num() == 1:
            if memory.get_curr_progress_num() > 0:
                sc = "to pick one more kind of " + g[0]
            else:
                sc = "to pick a kind of " + g[0]
        else:
            if memory.get_curr_progress_num() > 0:
                sc = "to pick " + str(int(g[2]) - memory.get_curr_progress_num()) + " more kinds of " + g[0]
            else:
                sc = "to pick " + str(int(g[2]) - memory.get_curr_progress_num()) + " kinds of " + g[0]
        return {'params': {
            'subj': "we",
            'vp': "need",
            'sc': sc
        },
            'modifiers': {
                'subj_plurality': conjugator.PLURAL,
                'vp_tense': conjugator.PRESENT_TENSE,
                'voice': conjugator.THIRD_PERSON
            }
        }


def describe_current_plan():
    output = ["Plan finished!","Here's a summary."]
    for idx, x in enumerate(memory.PLAN):
        output.append("For " + x[0] + ": " + generate_string_from_list(memory.PROGRESS[idx]) + ".")
    return (-1, " ". join(output))

def agree_on_valid_subject(valid, obj):
    return {'params': {
        'subj': valid,
        'vp': "be",
        'sc': "a good choice for " + obj
    },
        'modifiers': {
            'subj_plurality': conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.THIRD_PERSON
        }
    }


def message_about_already_in(alr):
    return {'params': {
        'subj': generate_string_from_list(alr) if len(alr) > 1 else alr,
        'vp': "be",
        'sc': "already part of the plan"
    },
        'modifiers': {
            'subj_plurality': conjugator.PLURAL if len(alr) > 1 else conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.THIRD_PERSON
        }
    }


def verify_if_goal(topic):
    g = memory.get_curr_goal()
    if g[0][0].lower() in ['a', 'e', 'i', 'o', 'u']:
        con = " an "
    else:
        con = " a "
    return "Is " + topic + con + g[0] + "? "

def verify_if_valid_goal(topic):
    g = memory.get_curr_goal()
    if g[1] == 'characters':
        return "Should we bring " + topic + " then?"
    else:
        return "Does " + topic + " sound like a good " + g[0] + "? "

def comment_on_if_valid(topic, dict_agree):
    print("dict_agree:", dict_agree)
    perc = collate_percentages(dict_agree)
    agree = perc['agree']
    disagree = perc['disagree']
    print("perc:", perc)
    r = random.random()
    if r < agree:
        return {'params': {
            'subj': 'I',
            'vp': 'think',
            'sc': 'that ' + topic + ' could be a good idea'
        }, 'modifiers': {
            'subj_plurality': conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.FIRST_PERSON
        }}
    elif r < disagree:
        return {'params': {
            'subj': 'I',
            'vp': 'think',
            'sc': 'that ' + topic + ' could be a bad idea'
        }, 'modifiers': {
            'subj_plurality': conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.FIRST_PERSON
        }}
    else:
        return {'params': {
            'subj': 'I',
            'vp': 'be',
            'sc': 'not sure if ' + topic + ' is a good idea'
        }, 'modifiers': {
            'subj_plurality': conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.FIRST_PERSON
        }}

def comment_on_if_(topic, perc):
    a=1

def get_progress_info(to_be_added):
    return {'params': {
        'subj': to_be_added,
        'vp': "be",
        'sc': "successfully added to the plan"
    },
        'modifiers': {
            'subj_plurality': conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.THIRD_PERSON
        }
    }
