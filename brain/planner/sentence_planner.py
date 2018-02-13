import random

import brain.api.conceptnet as conceptnet
from brain import memory
from brain.conjugator import conjugator

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
                if conjugator.is_plural(x[1]):
                    text == ""
            plans.append(generate_sentence_plan(x, text, vp))
    return plans


def plan_from_memory(info, name, key="knowledge", subject=""):
    if key is "knowledge":
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
        return {'params': {
            'subj': name,
            'vp': 'be',
            'sc': text + context_info
        }, 'modifiers': {
            'subj_plurality': conjugator.PLURAL if conjugator.is_plural(name) else conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.THIRD_PERSON
        }}


def plan_randomly_from_memory(subject, num_sentences):
    rand_plans = []
    context_dir, opinion_dir_cont = traverse_and_check(subject, memory.CURRENT_CONTEXT, [], [], [])
    # print("cont: ", context_dir)
    for x in context_dir:
        y = list(memory.CURRENT_CONTEXT[x[0]][x[1]].keys())
        y.remove('name')
        rand_plans.append(plan_from_memory(x[0], memory.CURRENT_CONTEXT[x[0]][x[1]]['name'], random.choice(y)))
    # print("rand_plan_cont: ", plan_from_memory(rand[0], memory.CURRENT_CONTEXT[rand[0]][rand[1]]['name'], rand[2]))
    # print("op_cont: ", opinion_dir_cont)
    for x in opinion_dir_cont:
        rand_plans.append(plan_from_memory(x[0], memory.CURRENT_CONTEXT[x[0]][x[1]]['name'], subject=x[2]))
    # print("rand_plan_op_cont: ", chain_access(memory.CURRENT_CONTEXT, rand2))
    memory_dir, opinion_dir_mem = traverse_and_check(subject, memory.CURRENT_MEMORY, [], [], [])
    # print("mem: ", memory_dir)
    for x in memory_dir:
        y = list(memory.CURRENT_MEMORY[x[0]][x[1]].keys())
        y.remove('name')
        rand_plans.append(plan_from_memory(x[0], memory.CURRENT_MEMORY[x[0]][x[1]]['name'], random.choice(y)))

    for x in opinion_dir_mem:
        rand_plans.append(plan_from_memory(x[0], memory.CURRENT_MEMORY[x[0]][x[1]]['name'], subject=x[2]))

    if len(rand_plans) > 0:
        if len(rand_plans) >= num_sentences:
            return random.choice(rand_plans, num_sentences)
        else:
            return rand_plans
    else:
        return []
        # print("rand_plan_cont: ", plan_from_me
        # print("op_mem: ", opinion_dir_mem)


def traverse_and_check(subject, tree, curr_dir, list_dir, opinion_dir):
    # print("curr_dir: ",curr_dir)
    # print("list_dir: ", list_dir)
    if type(tree) is dict:
        for key in list(tree.keys()):
            curr_dir.append(key)
            if key == subject:
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
        if tree == subject:
            # print("Match!")
            # print("list_dir [before]:", list_dir)
            # print("curr_dir:", curr_dir)
            list_dir.append(curr_dir[:])
            # print("list_dir [after]:", list_dir)
            return list_dir, opinion_dir
    # print("pre-return: ",list_dir)
    return list_dir, opinion_dir


def generate_sentence_plan(choice, text, vp):
    if conjugator.is_plural(choice[1]) and text == "a ":
        text = ""
    return {'params': {
        'subj': choice[0],
        'vp': vp,
        'sc': text + choice[1]
    },
        'modifiers': {
            'subj_plurality': conjugator.PLURAL if conjugator.is_plural(choice[0]) else conjugator.SINGULAR,
            'vp_tense': conjugator.PRESENT_TENSE,
            'voice': conjugator.THIRD_PERSON
        }}


def describe_subject(subject, num_sentences):
    # plans = plan_from_memory("characters", memory.CURRENT_CHARACTER, key="knowledge", subject=subject)
    # if len(plans) == 0 or plans[0]['params'] == {} or plans[0]['modifiers'] == {}:
    #plans = plan_randomly_from_memory(subject, num_sentences)
    plans = []
    if len(plans) < num_sentences:
        plans.extend(plan_from_conceptnet(subject, num_sentences - len(plans)))
    return plans


def answer_question(event):
    a = 1


def plan_response():
    a = 1
