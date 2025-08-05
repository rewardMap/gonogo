import pathlib
from typing import Literal, Union

import numpy as np

try:
    from ....reward_classes import PseudoRandomReward
    from ....utils import check_seed
    from ...yaml_tools import load_task_from_yaml
except ImportError:
    from rewardgym import check_seed
    from rewardgym.reward_classes import PseudoRandomReward
    from rewardgym.tasks.yaml_tools import load_task_from_yaml


def get_task(
    render_backend: Literal["pygame", "psychopy"] = None,
    seed: Union[int, np.random.Generator] = 1000,
    key_dict=None,
):
    seed = check_seed(seed)
    yaml_file = pathlib.Path(__file__).parents[1].resolve() / "task.yaml"
    info_dict, environment_graph = load_task_from_yaml(yaml_file)

    reward_structure = {
        5: PseudoRandomReward(reward_list=[-1, -1, 0, 0, 0, 0, 0, 0, 0, 0], seed=seed),
        6: PseudoRandomReward(
            reward_list=[-1, -1, -1, -1, -1, -1, -1, -1, 0, 0], seed=seed
        ),
        7: PseudoRandomReward(reward_list=[1, 1, 1, 1, 1, 1, 1, 1, 0, 0], seed=seed),
        8: PseudoRandomReward(reward_list=[1, 1, 0, 0, 0, 0, 0, 0, 0, 0], seed=seed),
    }

    info_dict.update(
        {"position": {0: "go-win", 1: "go-punish", 2: "nogo-win", 3: "nogo-punish"}}
    )

    if render_backend == "pygame":
        from .backend_pygame import get_pygame_info

        pygame_dict = get_pygame_info()
        info_dict.update(pygame_dict)

    elif render_backend == "psychopy" or render_backend == "psychopy-simulate":
        from .backend_psychopy import get_psychopy_info

        if key_dict is None:
            key_dict = {"space": 0}

        psychopy_dict, _ = get_psychopy_info(seed=seed, key_dict=key_dict)
        info_dict.update(psychopy_dict)

    return environment_graph, reward_structure, info_dict
