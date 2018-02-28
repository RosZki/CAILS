from ruamel.yaml import YAML
from CAILS.settings import CONTEXT_DIR
from CAILS.settings import MEMORY_DIR
import os

CURRENT_CONTEXT = {}
CURRENT_MEMORY = {'characters': [{'name': "Pooh", "knowledge": {'Piglet': {'IsA': ['friend','ally']}}}]}

CURRENT_STATE = {'location': 'Hundred Acre Wood', 'character':'Pooh'}


def read_context(context_name):
    yaml = YAML(typ='safe')
    list_files = [x for x in os.listdir(CONTEXT_DIR + context_name)]

    global CURRENT_CONTEXT
    for x in list_files:
        name = x.split('.')[0]
        CURRENT_CONTEXT[name] = yaml.load(open(CONTEXT_DIR + context_name + '\\' + x, 'r'))
    #CURRENT_STATE['location'] = CURRENT_CONTEXT['locations'][0]['name']
    #CURRENT_STATE['character'] = CURRENT_CONTEXT['locations'][0]['characters'][0]


def save_memory(filename):
    yaml = YAML(typ='safe')
    print(CURRENT_MEMORY)
    with open(MEMORY_DIR + filename, 'w+') as outfile:
        yaml.dump(CURRENT_MEMORY, outfile)


def get_information(info_type, key_type, key):
    return [x for x in CURRENT_CONTEXT[info_type] if x[key_type] == key]
