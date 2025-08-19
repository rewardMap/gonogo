from copy import deepcopy

try:
    from ....psychopy_render import (
        ImageStimulus,
        FeedBackStimulus,
        ActionStimulus,
        BaseStimulus,
    )
    from ....stimuli import (
        fixation_cross,
        make_card_stimulus,
        generate_stimulus_properties,
        draw_robot,
        mid_stimuli,
        STIMULUS_DEFAULTS,
    )
    from ....utils import check_random_state

except ImportError:
    from rewardgym import check_random_state
    from rewardgym.psychopy_render import (
        ImageStimulus,
        STIMULUS_DEFAULTS,
        FeedBackStimulus,
        ActionStimulus,
        BaseStimulus,
    )
    from rewardgym.stimuli import (
        fixation_cross,
        make_card_stimulus,
        generate_stimulus_properties,
        draw_robot,
        mid_stimuli,
    )


def gonogo_stimuli(random_state, stim_defaults=STIMULUS_DEFAULTS):
    random_state = check_random_state(random_state)
    stim_properties = []

    stim_defaults = deepcopy(stim_defaults)

    for _ in range(4):
        st_p = generate_stimulus_properties(
            random_state,
            patterns=[(2, 2), (3, 3)],
            colors=stim_defaults["colors"],
            shapes=stim_defaults["shapes"],
        )
        stim_properties.append(st_p)
        stim_defaults["colors"] = [
            i for i in stim_defaults["colors"] if i not in st_p["colors"]
        ]
        stim_defaults["shapes"] = [
            i for i in stim_defaults["shapes"] if i != st_p["shapes"]
        ]

    image_map = {}
    stimuli = {}

    for n in range(4):
        image_map[n] = make_card_stimulus(stim_properties[n], height=350, width=350)
        stimuli[n] = stim_properties[n]

    return image_map, stimuli


def gonogo_robots(random_state, stim_defaults=STIMULUS_DEFAULTS):
    random_state = check_random_state(random_state)
    colors = stim_defaults["colors"][:-1]
    no_colors = len(colors)
    allow_set = colors + colors

    start_color = random_state.integers(0, no_colors)

    color_set = colors[start_color::2][:4]
    color_set = random_state.permutation(color_set)

    image_map = {}
    for n in range(4):
        image_map[n] = draw_robot(
            height=450,
            width=450,
            body_color=allow_set[n],
            second_color=allow_set[n],
            button_color="gray",
        )

    return image_map, None


def get_psychopy_info(
    random_state=None, key_dict={"space": 0}, external_stimuli=None, fullpoints=None, **kwargs
):
    random_state = check_random_state(random_state)

    if external_stimuli is None:
        image_map, stimuli = gonogo_robots(random_state)
    else:
        image_map, stimuli = external_stimuli

    reward_feedback = FeedBackStimulus(
        1.0, text="{0}", target="reward", name="reward", bar_total=fullpoints, rl_label="reward"
    )

    base_stim = ImageStimulus(
        image_paths=[fixation_cross()], duration=0.3, name="fixation", autodraw=True
    )

    fix_isi = ImageStimulus(
        image_paths=[fixation_cross()], duration=0.3, name="isi", autodraw=False
    )

    def first_step(img):
        return [
            base_stim,
            ImageStimulus(
                duration=1.0,
                image_paths=[img],
                positions=[(0, 0)],
                name="cue",
                rl_label="obs"
            ),
            fix_isi,
            ImageStimulus(
                duration=0.001,
                image_paths=[
                    mid_stimuli(
                        other_color="gray",
                        shape="circle",
                        probe=False,
                        amount="",
                        shape_dim=250,
                    )
                ],
                positions=[(0, 0)],
                name="target",
            ),
            ActionStimulus(duration=1.0, key_dict=key_dict, timeout_action=1, rl_label="action"),
        ]

    final_step = [
        BaseStimulus(duration=1.0, name="reward-delay", rl_label="obs"),
        reward_feedback,
        BaseStimulus(name="iti", duration=1.0),
    ]

    info_dict = {
        0: {"psychopy": []},
        1: {"psychopy": first_step(image_map[0])},
        2: {"psychopy": first_step(image_map[1])},
        3: {"psychopy": first_step(image_map[2])},
        4: {"psychopy": first_step(image_map[3])},
        5: {"psychopy": final_step},
        6: {"psychopy": final_step},
        7: {"psychopy": final_step},
        8: {"psychopy": final_step},
    }

    return info_dict, stimuli
