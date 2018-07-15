from brain.generate_trial import grammar


def generate_pattern(params, gen_params):
    if all(v in grammar.terminal_nodes for v in gen_params.keys()):
        print("Error: presence of invalid params.")
        return ""
    while all(v == 0 for v in gen_params.values()):
        a = 1
