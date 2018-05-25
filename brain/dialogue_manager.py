from brain import memory
from brain import interpreter
from brain.planner import response_planner

def introduce():
    return response_planner.plan_introduction()

def reply(input):
    kw = interpreter.get_keywords(interpreter.stanford_pos(input))
    if memory.check_if_within_topic(kw):
        p = response_planner.plan_response(input,memory.get_curr_character_params())
    else:
        print('out of topic!')
        p = response_planner.plan_response(input,memory.get_curr_character_params())
    inf = interpreter.extract_info(input)
    print(inf)
    return p