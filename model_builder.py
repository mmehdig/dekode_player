from itertools import product, combinations, permutations
import nltk
from tqdm import tqdm

game_size = 10

read_expr = nltk.sem.Expression.fromstring

if game_size == 7:
    colors = ['blue', 'green', 'pink', 'purple', 'red', 'white', 'yellow']
elif game_size == 4:
    colors = ['blue', 'green', 'red', 'yellow']
elif game_size == 10:
    colors = [f'{i:d}' for i in range(game_size)]

options = [f'oo{i:d}' for i in range(game_size)]

color2option = {c: o for c, o in zip(colors, options)}
option2color = {o: c for c, o in zip(colors, options)}


choices = ['e0', 'e1', 'e2', 'e3', 'e4']


def display_result(mb):
    reversed_val_dict = {
        mb.valuation[o]: o
        for o in options
    }

    setting = tuple(reversed_val_dict[mb.valuation[k]] for k in choices)
    print(f"{option2color[setting[0]]}\t{option2color[setting[1]]}\t{option2color[setting[2]]}\t{option2color[setting[3]]}\t{option2color[setting[4]]}")
    print()

    return setting

def setting_to_logic(setting):
    return f'({" & ".join([f"({k}={v})" for k, v in zip(choices, setting)])})'

def history_to_assumptions(history):
    # initialise the assumptions
    assumptions = [
        nltk.sem.Expression.fromstring(f'({" & ".join([f"({o1}!={o2})" for o1, o2 in combinations(options, 2)])})'),
        nltk.sem.Expression.fromstring(" & ".join([f'({" or ".join([f"({k}={v})" for v in options])})' for k in choices]))
    ]

    for setting, (e_score, g_score) in history:
        setting_dict = {k: v for k, v in zip(choices, setting)}
        # e_score => exact match of the options and entities
        _exact_matches = list(combinations(setting_dict, e_score))
        if len(_exact_matches) == 0:
            _exact_matches = [tuple()]

        _general_matches = {
            exact_match: list(set([
                tuple([(k,v) for k,v in zip(ks, vs)])
                for ks in combinations(set(setting_dict.keys()) - set(exact_match), g_score - e_score)
                for vs in permutations([setting_dict[k] for k in (set(setting_dict.keys()) - set(exact_match))], g_score - e_score)
                if sum([1 for k,v in zip(ks, vs) if v == setting_dict[k]]) == 0
            ]))
            for exact_match in _exact_matches
        }

        combined_matches = " or ".join([
            f'({" & ".join(exact_match_formatting)})'
            for exact_match in _exact_matches
            for general_match in _general_matches[exact_match]
            for general_match_dict in [dict(general_match)]
            for exact_match_formatting in [[
                f"({k}={setting_dict[k]})" if k in exact_match else (f"({k}={general_match_dict[k]})" if k in general_match_dict else f"({k}!={setting_dict[k]})")
                for k in choices
            ]]
        ])

        assumptions.append(nltk.sem.Expression.fromstring(combined_matches))

    return assumptions


def _convert_to_vars(sample_history):
    return [(tuple(color2option[c] for c in evidence), score) for evidence, score in sample_history]


def infer_results(inputs):
    assumptions = history_to_assumptions(_convert_to_vars(inputs))
    # model search
    mb0 = nltk.MaceCommand(None, assumptions, 50)
    print()
    print("Build a possible model ... ")
    mb0.build_model()

    setting = display_result(mb0)

    mb1 = nltk.MaceCommand(nltk.sem.Expression.fromstring(setting_to_logic(setting)), assumptions, 50)
    if mb1.build_model():
        print("There are more answers:")
        display_result(mb1)
    else:
        print("That is the only answer")

if __name__ == "__main__":
    #infer_results(input_history)
    """
    input_history = [
        (('8', '8', '8', '8', '8'), (0, 0)),
        (('2', '2', '3', '3', '0'), (0, 1)),
        (('0', '0', '1', '5', '3'), (0, 2)),
        (('1', '1', '0', '6', '6'), (0, 1)),
        (('3', '9', '9', '8', '5'), (2, 2)),
        (('3', '5', '5', '4', '5'), (1, 2)),
        (('3', '9', '4', '1', '4'), (2, 3)),
        (('3', '4', '9', '4', '2'), (0, 3)),
        (('4', '9', '2', '0', '5'), (4, 4)),
        (('4', '9', '2', '1', '5'), (3, 3)),
    ]

    for evidence, scores in input_history:
        print(f"{evidence[0]}\t{evidence[1]}\t{evidence[2]}\t{evidence[3]}\t{evidence[4]}\t ({scores[0]}, {scores[1]})")
    """

    input_history = []
    for evidence, scores in input_history:
        print(f"{evidence[0]}\t{evidence[1]}\t{evidence[2]}\t{evidence[3]}\t{evidence[4]}\t ({scores[0]}, {scores[1]})")
    infer_results(input_history)
    while True:
        input_settings = input("setting:")
        input_e_score = input("score position match:")
        input_g_score = input("score item match:")
        try:
            setting = tuple([item.strip() for item in input_settings.split(',')])
            e_score = int(input_e_score)
            g_score = int(input_g_score)
            input_history.append((setting, (e_score, g_score)))

            for evidence, scores in input_history:
                print(f"{evidence[0]}\t{evidence[1]}\t{evidence[2]}\t{evidence[3]}\t{evidence[4]}\t ({scores[0]}, {scores[1]})")
            infer_results(input_history)
        except:
            break
