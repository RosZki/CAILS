import random

from brain import generator
from brain import interpreter
from brain import memory
from brain.planner import sentence_planner
from brain.planner.sentence_planner import collate_percentages

to_verify = []
to_verify_what = []
to_verify_valid = []

# 0 = DEF, 1 = need_to_verify, 2 = waiting_for_answer
F_DEFAULT = 0
F_VERIFY_VALID = 1
F_VERIFY_WHAT = 2
F_ASKING_Q = 3
CURR_FLAG = F_DEFAULT


def add_additional_modifiers(plan, modifiers):
    for x in list(modifiers.keys()):
        plan[x] = modifiers[x]
    return plan


def pop_random(lst):
    return lst.pop(random.randrange(0, len(lst)))


def collate(plans):
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
    for x in collated_plans:
        rand = random.random()
        rand2 = random.random()
        if len(x) == 1:
            if rand2 < its:
                s.append("I think that " + generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'], False))
            elif rand2 < itd:
                s.append(generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'])[:-1] + ", I think.")
            elif rand2 < ns:
                s.append(
                    "I'm not sure but " + generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'], False))
            elif rand2 < rc:
                s.append(
                    "If I recall correctly, " + generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'],
                                                                                   False))
            else:
                s.append(generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers']))
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
            g1 = generator.generate_simple_sentence(x[0]['params'], x[0]['modifiers'])
            g2 = generator.generate_simple_sentence(x[1]['params'], x[1]['modifiers'], False)

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


def generate_narrator(plans):
    output = []
    for x in plans:
        output.append(generator.generate_simple_sentence(x['params'], x['modifiers']))
    return " ".join(output)


def stutter(output, percentage):
    words = output.split()
    final_words = []
    for word in words:
        if random.random() < percentage:
            final_words.append(word[0] + "-" + word)
        else:
            final_words.append(word)
    return " ".join(final_words)


def generate_responses(plans):
    output = []
    for x in plans:
        if x[0] > -1:
            output.append(
                (x[0], stutter(finalize_output(collate(x[1]), {
                    'however': memory.get_character_params(x[0])['speech']['however'],
                    'and': memory.get_character_params(x[0])['speech']['and']
                }, {
                       'i_think_start': memory.get_character_params(x[0])['speech'][
                           'i_think_start'],
                       'i_think_end': memory.get_character_params(x[0])['speech'][
                           'i_think_end'],
                       'not_sure': memory.get_character_params(x[0])['speech']['not_sure'],
                       'recall_correctly': memory.get_character_params(x[0])['speech'][
                           'recall_correctly']
                   }), memory.get_character_params(x[0])['speech']['stutter'])
                 )
            )
        else:
            output.append(
                (x[0],
                 generate_narrator(x[1])
                 )
            )
    return output


def plan_response(message):
    # final_message = []
    tagged = interpreter.stanford_pos(message)
    keywords = interpreter.consolidate(interpreter.get_keywords(tagged))
    c_s = memory.get_speaker()
    valid = []
    plans = []
    already_in = []
    global to_verify
    prev_length = len(to_verify)
    for x in keywords:
        if memory.check_if_valid_goal(x):
            valid.append(x)
        elif memory.check_if_in_plan(x):
            already_in.append(x)
        else:
            to_verify.append(x)
    if len(already_in) > 0:
        plans.append((-1, sentence_planner.message_about_already_in(already_in)))
        plans.append((c_s, sentence_planner.message_about_already_in(already_in)))
    if prev_length > 0:
        if any(word in message.lower() for word in ["yes", 'yeah']):
            valid.append(to_verify[0])
        else:
            memory.randomize_speaker()
        to_verify = to_verify[1:]
    if len(valid) > 0:
        p = sentence_planner.agree_on_valid_subject(valid, memory.get_curr_goal()[0])
        p2_g = memory.get_speaker(0)
        p2 = sentence_planner.describe_subject(random.choice(valid),
                                               memory.get_character_params(p2_g)['speech']['verbosity'])
        plans.append((-1, sentence_planner.get_progress_info(valid)))
        done = memory.add_to_progress(valid)
        if done:
            final = memory.move_progress()
            to_verify = to_verify[:]
            if final:
                return [sentence_planner.describe_current_plan()]
        if p != None:
            plans.append((c_s, [p]))
            if len(p2[0]['params']) + len(p2[0]['modifiers']) > 0:
                plans.append((p2_g, p2))
            else:
                a = 1
    if len(to_verify) == 0:
        plans.append((memory.get_speaker(2), [sentence_planner.get_current_goal()]))
    # print(plans)

    for x in plans:
        x[1][:] = [y for y in x[1] if y != {'params': {}, 'modifiers': {}}]

    # for x in plans:
    #    final_message.append(generator.generate_simple_sentence(x['params'], x['modifiers']))


    output = generate_responses(plans)

    if len(to_verify) > 0:
        output.append((c_s,
                       stutter(sentence_planner.verify_if_goal(to_verify[0]),
                               memory.get_character_params(c_s)['speech']['stutter'])))

    # output = " ".join(final_message)
    return output


def plan_i(message):

    plans = []
    c_s = memory.get_speaker()
    n_s = memory.get_all_non_speaker()
    global CURR_FLAG
    global to_verify_what
    global to_verify_valid
    print("FLAG:", CURR_FLAG)
    if CURR_FLAG == F_VERIFY_VALID:
        if any(word in message.lower() for word in ["yes", 'yeah']):
            p = sentence_planner.agree_on_valid_subject(to_verify_valid[0], memory.get_curr_goal()[0])
            p2_g = random.choice(n_s)
            p2 = sentence_planner.describe_subject(to_verify_valid[0],
                                                   memory.get_character_params(p2_g)['speech']['verbosity'])
            plans.append([-1, [sentence_planner.get_progress_info(to_verify_valid[0])]])
            done = memory.add_to_progress([to_verify_valid[0]])
            if done:
                final = memory.move_progress()
                to_verify_valid = []
                to_verify_what = []
                if final:
                    return [sentence_planner.describe_current_plan()]
            if p != None:
                plans.append([c_s, [p]])
                if len(p2[0]['params']) + len(p2[0]['modifiers']) > 0:
                    plans.append([p2_g, p2])
                else:
                    #CURR_FLAG = F_ASKING_Q
                    a=1
        else:
            memory.randomize_speaker()
        to_verify_valid = to_verify_valid[1:]
        CURR_FLAG = F_DEFAULT
    elif CURR_FLAG == F_VERIFY_WHAT:
        if any(word in message.lower() for word in ["yes", 'yeah']):
            to_verify_valid.append(to_verify_what[0])
        else:
            memory.randomize_speaker()
        to_verify_what = to_verify_what[1:]
        CURR_FLAG = F_DEFAULT
    elif CURR_FLAG == F_ASKING_Q:
        a = 2
    else:
        tagged = interpreter.stanford_pos(message)
        print("TAG:", tagged)
        keywords = interpreter.consolidate(interpreter.get_keywords(tagged))
        print("KEY:", keywords)
        already_in = []
        for x in keywords:
            if memory.check_if_valid_goal(x):
                to_verify_valid.append(x)
            elif memory.check_if_in_plan(x):
                already_in.append(x)
            else:
                to_verify_what.append(x)
        if len(already_in) > 0:
            plans.append([-1, sentence_planner.message_about_already_in(already_in)])
            plans.append([c_s, sentence_planner.message_about_already_in(already_in)])
    if len(to_verify_valid) > 0 and CURR_FLAG != F_ASKING_Q:
        CURR_FLAG = F_VERIFY_VALID
        for x in plans:
            print(x)
            x[1] = [y for y in x[1] if y != {'params': {}, 'modifiers': {}}]
        output = generate_responses(plans)
        output.append((c_s,
                       stutter(sentence_planner.verify_if_valid_goal(to_verify_valid[0]),
                               memory.get_character_params(c_s)['speech']['stutter'])))
        sp = random.choice(n_s)
        sp_g = sentence_planner.comment_on_if_valid(
                                     to_verify_valid[0],{
                                         'agree': memory.get_character_params(sp)['speech']['agree'],
                                         'disagree': memory.get_character_params(sp)['speech']['disagree']
                                     }
                                     )
        output.append((sp,
                       stutter(generator.generate_simple_sentence(sp_g['params'], sp_g['modifiers']),
                               memory.get_character_params(sp)['speech']['stutter'])))
    elif len(to_verify_what) > 0 and CURR_FLAG != F_ASKING_Q:
        CURR_FLAG = F_VERIFY_WHAT
        for x in plans:
            x[1] = [y for y in x[1] if y != {'params': {}, 'modifiers': {}}]
        output = generate_responses(plans)
        output.append((c_s,
                       stutter(sentence_planner.verify_if_goal(to_verify_what[0]),
                               memory.get_character_params(c_s)['speech']['stutter'])))
    else:
        plans.append([random.choice(n_s), [sentence_planner.get_current_goal()]])
        print("pl:", plans)
        for x in plans:
            x[1][:] = [y for y in x[1] if y != {'params': {}, 'modifiers': {}}]
        output = generate_responses(plans)

    return output




def plan_introduction():
    plans = []
    plans.append(sentence_planner.plan_introduction_from_context())
    out = generate_responses(plans)
    out.append(sentence_planner.get_introductory_plan())
    out.extend(generate_responses([(memory.get_speaker(), [sentence_planner.get_current_goal()])]))
    return out
