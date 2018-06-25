import random

from brain import generator
from brain import interpreter
from brain import memory
from brain.planner import sentence_planner

to_verify = []


def add_additional_modifiers(plan, modifiers):
    for x in list(modifiers.keys()):
        plan[x] = modifiers[x]
    return plan


def pop_random(lst):
    return lst.pop(random.randrange(0, len(lst)))


def collate(plans):
    print("PLAN CHECK", plans)
    if len(plans) == 1 and (plans[0]['params'] == {} or plans[0]['modifiers'] == {}):
        return [plans]
    elif len(plans) == 1:
        return [plans]
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
        collated_plans.append([pop_random(list_plans)])
   # print("collated:",collated_plans)
    return collated_plans


def collate_percentages(dict_perc):
    prev = 0
    for x in dict_perc.keys():
        curr = dict_perc[x] + prev
        dict_perc[x] = curr
        prev = curr
    return dict_perc


def finalize_output(collated_plans, dict_conj, dict_hedgers):
    d = collate_percentages(dict_conj)
    hw = d['however']
    ad = d['and']
    s = []
    d2 = collate_percentages(dict_hedgers)
    its = d2['i_think_start']
    itd = d2['i_think_end']
    ns = d2['not_sure']
    rc = d2['recall_correctly']
    default = generator.generate_simple_sentence()
    print("COLLATED", collated_plans)
    for x in collated_plans:
        print("LEN: ", len(x))
        rand = random.random()
        rand2 = random.random()
        if len(x) == 1:
            if rand2 < its:
                s.append("I think that " + generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'], False))
            elif rand2 < itd:
                s.append(generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'])[:-1] + ", I think.")
            elif rand2 < ns:
                s.append("I'm not sure but " + generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'], False))
            elif rand2 < rc:
                s.append("If I recall correctly, " + generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'], False))
            else:
                s.append(generator.generate_simple_sentence(x[0]['params'],x[0]['modifiers']))
            break
        if rand2 < its:
            g1 = "I think that " + generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'], False)
            g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'], False)
        elif rand2 < itd:
            g1 = generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'])
            g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'])[:-1] + ", I think."
        elif rand2 < ns:
            g1 = "I'm not sure but " + generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'], False)
            g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'], False)
        elif rand2 < rc:
            g1 = "If I recall correctly, " + generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'],
                                                                                    False)
            g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'], False)
        else:
            g1 = generator.generate_simple_sentence(x[0]['params'],x[0]['modifiers'])
            g2 = generator.generate_simple_sentence(x[1]['params'],x[1]['modifiers'], False)

        if rand < hw:
            s.append(g1[:-1] + "; however, " + g2)
        elif rand < ad:
            s.append(g1[:-1] + " and " + g2)
        else:
            if rand2 < its:
                g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'])
            elif rand2 < itd:
                g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'])[:-1] + ", I think."
            elif rand2 < ns:
                g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'])
            elif rand2 < rc:
                g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'])
            else:
                g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'])
            s.append(g1 + " " + g2)
    if len(s) > 0:
        return " ".join(s)
    else:
        return default


def stutter(output, percentage):
    words = output.split()
    final_words = []
    for word in words:
        if random.random() < percentage:
            final_words.append(word[0] + "-" + word)
        else:
            final_words.append(word)
    return " ".join(final_words)


def plan_response(message, params):
    #final_message = []
    tagged = interpreter.stanford_pos(message)
    keywords = interpreter.consolidate(interpreter.get_keywords(tagged))
    valid = []
    p = None
    global to_verify
    if len(to_verify) > 0:
        if "yes" in message.lower():
            done = memory.add_to_progress([to_verify[0]])
            to_verify = to_verify[1:]
            if done:
                final = memory.move_progress()
                to_verify = to_verify[:]
                if final:
                    return sentence_planner.describe_current_plan()
            if p != None:
                plans = [p]
                plans.append(sentence_planner.describe_current_goal())
            else:
                plans = [sentence_planner.describe_current_goal()]
        else:
            plans = [sentence_planner.describe_current_goal()]
    else:
        topic = random.choice(keywords)
        for x in keywords:
            if memory.check_if_valid_goal(x):
                valid.append(x)
            else:
                to_verify.append(x)
        if len(valid) > 0:
            p = sentence_planner.agree_on_valid_subjects(valid)
            done = memory.add_to_progress(valid)
            if done:
                final = memory.move_progress()
                to_verify = to_verify[:]
                if final:
                    return sentence_planner.describe_current_plan()
                if len(to_verify) > 0:
                    return stutter(sentence_planner.verify_if_goal(to_verify[0]), params['speech']['stutter'])
            if len(to_verify) > 0:
                return stutter(sentence_planner.verify_if_goal(to_verify[0]), params['speech']['stutter'])
            else:
                plans = [sentence_planner.describe_current_goal()]
        else:
            if len(to_verify) > 0:
                return stutter(sentence_planner.verify_if_goal(to_verify[0]), params['speech']['stutter'])
            plans = sentence_planner.describe_subject(topic, params['speech']['verbosity'])
    # print(plans)
    print("PLANS: ", plans)
    if len(plans) > 1:
        plans[:] = [x for x in plans if x != {'params': {}, 'modifiers': {}}]
    print("plans:", plans)
    #for x in plans:
    #    final_message.append(generator.generate_simple_sentence(x['params'], x['modifiers']))
    output = finalize_output(collate(plans), {
        'however': params['speech']['however'],
        'and': params['speech']['and']
    },{
        'i_think_start': params['speech']['i_think_start'],
        'i_think_end': params['speech']['i_think_end'],
        'not_sure': params['speech']['not_sure'],
        'recall_correctly': params['speech']['recall_correctly']
    })

    #output = " ".join(final_message)
    output = stutter(output, params['speech']['stutter'])
    return output


def plan_introduction(params):
    final_message = []
    plans = sentence_planner.plan_introduction_from_context()
    plans.append(sentence_planner.describe_current_goal())

    for x in plans:
        final_message.append(generator.generate_simple_sentence(x['params'],x['modifiers']))

    return " ".join(final_message)

    #return stutter(finalize_output(collate(plans), {
    #    'however': params['speech']['however'],
    #    'and': params['speech']['and']
    #},{
    #    'i_think_start': params['speech']['i_think_start'],
    #    'i_think_end': params['speech']['i_think_end'],
    #    'not_sure': params['speech']['not_sure'],
    #    'recall_correctly': params['speech']['recall_correctly']
    #}) + " " + finalize_output(collate([sentence_planner.describe_current_goal()]), {
    #    'however': params['speech']['however'],
    #    'and': params['speech']['and']
    #},{
    #    'i_think_start': params['speech']['i_think_start'],
    #    'i_think_end': params['speech']['i_think_end'],
    #    'not_sure': params['speech']['not_sure'],
    #    'recall_correctly': params['speech']['recall_correctly']
    #}), params['speech']['stutter'])