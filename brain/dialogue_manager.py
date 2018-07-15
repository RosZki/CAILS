from brain import interpreter
from brain import memory
from brain.planner import response_planner


def generate_display_params(plans):
    f = []
    for x in plans:
        disp = memory.get_character_display(x[0])
        t = {}
        t['message'] = x[1]
        if disp is not None:
            t['flag'] = True
            t['id'] = disp['class_id']
            t['icon'] = disp['agent_icon']
            t['name'] = disp['name']
        else:
            t['flag'] = False
        f.append(t)
    return f


def introduce():
    return generate_display_params(response_planner.plan_introduction())


def reply(input):
    kw = interpreter.get_keywords(interpreter.stanford_pos(input))
    if memory.check_if_within_topic(kw):
        p = response_planner.plan_i(input)
    else:
        print('out of topic!')
        p = response_planner.plan_i(input)
    inf = interpreter.extract_info(input)
    return generate_display_params(p)
