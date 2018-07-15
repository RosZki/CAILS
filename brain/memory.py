import os
import random
import re

from ruamel.yaml import YAML

from CAILS.settings import CONTEXT_DIR
from CAILS.settings import MEMORY_DIR
from brain.api import conceptnet

CURRENT_CONTEXT = {}
CURRENT_MEMORY = {}

CURRENT_STATE = {}

PLAN = {}

DESC = {}

DISPLAY = {}

CURR_GOAL_IND = 0

PROGRESS = []

CURR_SPEAKER = 0


def clear_data():
    global CURRENT_CONTEXT
    global CURRENT_STATE
    global CURRENT_MEMORY
    global PLAN
    global DISPLAY
    global PROGRESS
    global DESC
    global CURR_GOAL_IND
    global CURR_SPEAKER

    CURRENT_CONTEXT = {}
    CURRENT_MEMORY = {}
    CURRENT_STATE = {}
    PLAN = {}
    DESC = {}
    DISPLAY = {}
    PROGRESS = []

    CURR_GOAL_IND = 0
    CURR_SPEAKER = 0


def check_if_within_topic(keywords):
    return True
    # return True if CURRENT_STATE['topics'].lower() in keywords else False


def read_context(context_name):
    clear_data()
    yaml = YAML(typ='safe')
    list_files = [x for x in os.listdir(CONTEXT_DIR + context_name + "\\knowledge_base")]

    global CURRENT_CONTEXT
    for x in list_files:
        name = x.split('.')[0]
        if name != 'concept_plan':
            CURRENT_CONTEXT[name] = yaml.load(open(CONTEXT_DIR + context_name + '\\knowledge_base\\' + x, 'r'))

    global CURRENT_STATE
    global PLAN
    global DISPLAY
    global PROGRESS
    global DESC
    CURRENT_STATE = yaml.load(open(CONTEXT_DIR + context_name + '\\context_plan.yml', 'r'))['state']
    PLAN = yaml.load(open(CONTEXT_DIR + context_name + '\\context_plan.yml', 'r'))['goals']
    DISPLAY = yaml.load(open(CONTEXT_DIR + context_name + '\\context_plan.yml', 'r'))['display']
    PROGRESS = yaml.load(open(CONTEXT_DIR + context_name + '\\context_plan.yml', 'r'))['initial_plan']
    DESC = yaml.load(open(CONTEXT_DIR + context_name + '\\context_plan.yml', 'r'))['description']

    for ind, val in enumerate(PLAN):
        PLAN[ind] = [val[0], val[1], int(re.findall('\d+', str(val[2]))[0]), '+' in str(val[2])]

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


def get_character_params(num=CURR_SPEAKER):
    curr_name = CURRENT_STATE['characters'][num]
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


def randomize_speaker():
    global CURR_SPEAKER
    CURR_SPEAKER = random.choice(list(range(0, len(CURRENT_STATE['characters']))))


def add_to_progress(items):
    global CURR_SPEAKER
    if len(PROGRESS) <= CURR_GOAL_IND:
        PROGRESS.append(items)
        randomize_speaker()
    else:
        PROGRESS[CURR_GOAL_IND].extend(items)
        randomize_speaker()

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
        if len([x for x in CURRENT_CONTEXT['characters'] if x['name'].lower() == item.lower()]) > 0 \
                and not check_if_in_plan(item):
            return True
        else:
            return False
    elif get_curr_goal()[1] == "location":
        if len([x for x in CURRENT_CONTEXT['locations'] if x['name'].lower() == item.lower()]) > 0 \
                and not check_if_in_plan(item):
            return True
        else:
            return False
    else:
        if conceptnet.check_if_connection(item, get_curr_goal()[0], get_curr_goal()[1]) \
                and not check_if_in_plan(item):
            return True
        else:
            return False


def check_if_in_plan(item):
    if any(item in sl for sl in PROGRESS):
        return True
    else:
        return False


def get_speaker():
    return CURR_SPEAKER

def get_all_non_speaker():
    a = list(range(0, len(CURRENT_STATE['characters'])))
    a.remove(CURR_SPEAKER)
    return a

def get_random_speaker():
    a = list(range(0, len(CURRENT_STATE['characters'])))
    return random.choice(a)


def get_character_display(id):
    if id > -1:
        return DISPLAY[CURRENT_STATE['characters'][id]]
    else:
        return None


def get_log_info(msgs):
    l = []
    for x in msgs:
        print('LOG', x)
        if x['flag']:
            speaker = x['name']
        else:
            speaker = "CAILS"
        l.append((speaker, x['message']))
    return l


def get_context_info():
    info = dict(DESC)
    d = []
    for x in DISPLAY:
        t = {}
        t['id'] = DISPLAY[x]['class_id']
        t['icon'] = DISPLAY[x]['agent_icon']
        d.append(t)
    info['display'] = d
    return info
