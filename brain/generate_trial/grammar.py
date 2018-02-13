from ruamel.yaml import YAML
from CAILS.settings import CFG_DIR

starting_nodes = []
branch_nodes = []
terminal_nodes = []
path_to_terminal = []
CURRENT_CFG = {}

def read_cfg_file(cfg_name):
    yaml = YAML(typ='safe')
    global CURRENT_CFG
    all_nodes = []
    TEMP_CFG = yaml.load(open(CFG_DIR + cfg_name))
    for w in TEMP_CFG.keys():
        temp = TEMP_CFG[w].split('|')
        temp2 = []
        for x in temp:
            y = x.split()
            temp2.append(y)
            for z in y:
                all_nodes.append(z)
        CURRENT_CFG[w] = temp2

    all_nodes = set(all_nodes)

    for x in all_nodes:
        if x not in CURRENT_CFG.keys():
            terminal_nodes.append(x)

    for x in CURRENT_CFG.keys():
        if x not in all_nodes:
            starting_nodes.append(x)
        else:
            branch_nodes.append(x)

    print("starting: ", starting_nodes)
    print("branch: ", branch_nodes)
    print("terminal: ", terminal_nodes)