import random

from brain import generator
from brain import interpreter
from brain.planner import sentence_planner


def add_additional_modifiers(plan, modifiers):
    for x in list(modifiers.keys()):
        plan[x] = modifiers[x]
    return plan


def pop_random(lst):
    return lst.pop(random.randrange(0, len(lst)))


def collate(plans):
    if len(plans) == 1 and (plans[0]['params'] == {} or plans[0]['modifiers'] == {}):
        return plans
    list_plans = plans[:]
    collated_plans = []
    list_of_subjects = list(set([x['params']['subj'].lower() for x in list_plans]))
    dict_of_plans = {}
    for subj in list_of_subjects:
        dict_of_plans[subj.lower()] = [x for x in list_plans if x['params']['subj'].lower() == subj.lower()]
    while len(list_plans) > 1:
        elem1 = pop_random(list_plans)
        elem2 = pop_random(list_plans)
        collated_plans.append((elem1, elem2))
    if len(list_plans) > 0:
        collated_plans.append(pop_random(list_plans))
    print(collated_plans)
    return collated_plans

def compound(collated_plans):
    a = 1

def stutter(output, percentage):
    words = output.split()
    final_words = []
    for word in words:
        if random.random() < percentage:
            final_words.append(word[0] + "-" + word)
        else:
            final_words.append(word)
    return " ".join(final_words)


def add_hedgers(sentences, dict_hedgers):
    a = 1

def plan_response(message, params):
    final_message = []
    tagged = interpreter.stanford_pos(message)
    keywords = interpreter.consolidate(interpreter.get_keywords(tagged))

    topic = random.choice(keywords)

    plans = sentence_planner.describe_subject(topic, params['num_sentences'])
    for x in plans:
        final_message.append(generator.generate_simple_sentence(x['params'], x['modifiers']))

    output = " ".join(final_message)
    output = stutter(output, params['stutter'])
    return output
