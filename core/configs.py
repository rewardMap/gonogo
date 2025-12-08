from rewardgym.utils import check_random_state
from rewardgym.tasks.utils import check_conditions_present


def get_configs(stimulus_set: str = "1"):
    random_state = check_random_state(int(stimulus_set))

    condition_dict = {
        "go-win": {0: {0: 1}},
        "go-punish": {0: {0: 2}},
        "nogo-win": {0: {0: 3}},
        "nogo-punish": {0: {0: 4}},
    }

    condition_template = ["go-win", "go-punish", "nogo-win", "nogo-punish"] * 15  # 80 %
    iti_template = [0.5, 0.75, 1.0, 1.25] * 15
    isi_template = [0.25, 0.75, 1.125, 1.75, 2.0] * 12  # 5 * 12 = 60

    n_blocks = 3

    check = False
    while not check:
        conditions = random_state.permutation(condition_template).tolist()
        check = check_conditions_present(conditions[:8], list(condition_dict.keys()))

    isi = random_state.permutation(isi_template).tolist()
    iti = random_state.permutation(iti_template).tolist()

    for _ in range(n_blocks - 1):
        conditions.extend(random_state.permutation(condition_template).tolist())
        isi.extend(random_state.permutation(isi_template).tolist())
        iti.extend(random_state.permutation(iti_template).tolist())

    config = {
        "name": "gonogo",
        "stimulus_set": stimulus_set,
        "isi": isi,
        "iti": iti,
        "condition": conditions,
        "condition_dict": condition_dict,
        "ntrials": len(conditions),
        "update": ["isi", "iti"],
        "add_remainder": True,
        "breakpoints": [59, 119],
        "break_duration": 45,
    }

    return config
