from ruamel.yaml import YAML
from CAILS.settings import CONTEXT_DIR
import os

CURRENT_CONTEXT = {}
CURRENT_MEMORY = {'characters':[{'name': "Pooh", "knowledge": {'Piglet': {'IsA': ['sad person']}}}]}
CURRENT_CHARACTER = 'Pooh'


def read_context(context_name):
    yaml = YAML(typ='safe')
    list_files = [x for x in os.listdir(CONTEXT_DIR + context_name)]

    global CURRENT_CONTEXT
    for x in list_files:
        name = x.split('.')[0]
        CURRENT_CONTEXT[name] = yaml.load(open(CONTEXT_DIR + context_name + '\\' + x))


# def save_memory(filename):
#    yaml = YAML(type='safe')
#    yaml.dump(CURRENT_MEMORY, MEMORY_DIR+filename)

def get_information(info_type, key_type, key):
    return [x for x in CURRENT_CONTEXT[info_type] if x[key_type] == key]
