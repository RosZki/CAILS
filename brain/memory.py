import os
import re

from ruamel.yaml import YAML

from CAILS.settings import CONTEXT_DIR
from CAILS.settings import MEMORY_DIR
from brain.api import conceptnet

CURRENT_CONTEXT = {}
CURRENT_MEMORY = {'characters': [{'name': "Pooh", "knowledge": {'Piglet': {'IsA': ['friend', 'ally']}}}]}

CURRENT_STATE = {'topics': 'picnic', 'location': 'Hundred Acre Wood', 'character': 'Pooh', 'others': {
    'Hundred Acre Wood': ['Piglet', 'Rabbit', 'Owl', 'Kanga', 'Roo', 'Eeyore', 'Tigger']
}}

PLAN = {}

CURR_GOAL_IND = 0

PROGRESS = []

IS_WAITING_VERIFICATION = False

def check_if_within_topic(keywords):
    return True
    #return True if CURRENT_STATE['topics'].lower() in keywords else False


def read_context(context_name):
    yaml = YAML(typ='safe')
    list_files = [x for x in os.listdir(CONTEXT_DIR + context_name + "\\knowledge_base")]

    global CURRENT_CONTEXT
    for x in list_files:
        name = x.split('.')[0]
        if name != 'concept_plan':
            CURRENT_CONTEXT[name] = yaml.load(open(CONTEXT_DIR + context_name + '\\knowledge_base\\' + x, 'r'))

    global CURRENT_STATE
    global PLAN
    CURRENT_STATE = yaml.load(open(CONTEXT_DIR + context_name + '\\context_plan.yml', 'r'))['state']
    PLAN = yaml.load(open(CONTEXT_DIR + context_name + '\\context_plan.yml', 'r'))['goals']

    for ind, val in enumerate(PLAN):
        PLAN[ind] = [val[0], val[1], re.findall('\d+', str(val[2]))[0], '+' in str(val[2])]

    print("STATE",CURRENT_STATE)
    print("PLAN", PLAN)
        # CURRENT_STATE['location'] = CURRENT_CONTEXT['locations'][0]['name']
        # CURRENT_STATE['character'] = CURRENT_CONTEXT['locations'][0]['characters'][0]



def save_memory(filename):
    yaml = YAML(typ='safe')
    with open(MEMORY_DIR + filename, 'w+') as outfile:
        yaml.dump(CURRENT_MEMORY, outfile)


def chain_access(list, keys, default={}):
    out = list
    try:
        for key in keys:
            out = out[key]
        return out
    except (AttributeError, KeyError, TypeError, IndexError) as e:
        return default


def add_to_character_memory(name, rel, val):
    y = [x for x in CURRENT_MEMORY['characters'] if x['name'] == CURRENT_STATE['character']]
    if len(y) > 0:
        y = y[0]
        if name in y['knowledge'].keys():
            if rel in y['knowledge'][name]:
                y['knowledge'][name][rel].append(val)
            else:
                y['knowledge'][name][rel] = [val]
        else:
            y['knowledge'][name] = {rel: [val]}
    else:
        CURRENT_MEMORY['characters'].append({
            'name': CURRENT_STATE['character'],
            'knowledge': {
                name: {rel: [val]}
            }
        })


def add_to_event_memory(actors, verb, sc, others=None, location=None):
    num = len(chain_access(CURRENT_CONTEXT, ['events'], [])) + len(chain_access(CURRENT_MEMORY, ['events'], []))
    if len(chain_access(CURRENT_MEMORY, ['events'], [])) > 0:
        if location == None:
            location = CURRENT_STATE['location']
        if others == None:
            others = chain_access(CURRENT_STATE, ['others', location], [])
        for x in actors:
            if x in others:
                others.remove(x)

        CURRENT_MEMORY['events'].append({
            'actors': actors,
            'location': location,
            'verb': verb,
            'sc': sc,
            'others': others
        })
    else:
        CURRENT_MEMORY['events'] = [{
            'actors': actors,
            'location': location,
            'verb': verb,
            'sc': sc,
            'others': others
        }]


def get_information(info_type, key_type, key):
    return [x for x in CURRENT_CONTEXT[info_type] if x[key_type] == key]


def get_curr_character_params():
    curr_name = CURRENT_STATE['character']
    x = [x for x in CURRENT_CONTEXT['characters'] if x['name'] == curr_name]
    if len(x) < 1:
        return []
    else:
        return x[0]['params']


def get_curr_goal():
    return PLAN[CURR_GOAL_IND]


def get_curr_progress_num():
    if len(PROGRESS) > CURR_GOAL_IND:
        return len(PROGRESS[CURR_GOAL_IND])
    else:
        return 0

def add_to_progress(items):
    if len(PROGRESS) <= CURR_GOAL_IND:
        print("APPEND")
        PROGRESS.append(items)
    else:
        print("EXTEND")
        PROGRESS[CURR_GOAL_IND].extend(items)

    print("PROGRESS:", PROGRESS)

    if len(PROGRESS[CURR_GOAL_IND]) >= int(PLAN[CURR_GOAL_IND][2]):
        return True
    else:
        return False


def move_progress():
    global CURR_GOAL_IND
    CURR_GOAL_IND = CURR_GOAL_IND + 1

    if CURR_GOAL_IND >= len(PLAN):
        return True
    else:
        return False


def check_if_valid_goal(item):
    if get_curr_goal()[1] == "characters":
        if len([x for x in CURRENT_CONTEXT['characters'] if x['name'].lower() == item.lower()]) > 0:
            return True
        else:
            return False
    elif get_curr_goal()[1] == "location":
        if len([x for x in CURRENT_CONTEXT['locations'] if x['name'].lower() == item.lower()]) > 0:
            return True
        else:
            return False
    else:
        if conceptnet.check_if_connection(item, get_curr_goal()[0], get_curr_goal()[1]):
            return True
        else:
            return False
