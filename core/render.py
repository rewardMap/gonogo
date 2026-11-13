from copy import deepcopy

from rewardgym import check_random_state
from rewardgym.render import ImageDefinition
from rewardgym.render.passive_routines import FeedBackRoutine, PresentationRoutine
from rewardgym.render.response_routines import ActionRoutine
from rewardgym.stimuli import (
    STIMULUS_DEFAULTS,
    draw_robot,
    fixation_cross,
    generate_stimulus_properties,
    make_card_stimulus,
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


def get_render_info(
    random_state=None, key_dict=None, external_stimuli=None, fullpoints=None, **kwargs
):
    if key_dict is None:
        key_dict = {"space": 0}
    random_state = check_random_state(random_state)

    if external_stimuli is None:
        image_map, stimuli = gonogo_robots(random_state)
    else:
        image_map, stimuli = external_stimuli

    reward_feedback = FeedBackRoutine(
        duration=1.0,
        name="reward",
        rl_label="reward",
        bar_total=fullpoints
    )

    fixation = ImageDefinition(
        image=fixation_cross(),
        pos=(0, 0),
        name="fix",
        autoDraw=True
    )

    fixation2 = ImageDefinition(
        image=fixation_cross(),
        pos=(0, 0),
        name="fix",
        autoDraw=False
    )

    base_stim = PresentationRoutine(
        duration=0.3,
        name="fixation",
        stimulus_definitions=[fixation]
    )


    fix_isi = PresentationRoutine(
        name="isi",
        duration=0.3,
        stimulus_definitions=[fixation2]
    )

    def first_step(img):
        return [
            base_stim,
            PresentationRoutine(
                duration=1.0,
                name="cue",
                rl_label="obs",
                stimulus_definitions=[
                    ImageDefinition(
                        image=img,
                        pos=(0, 0),
                        name="robot"
                    )
                ]
            ),
            fix_isi,
            ActionRoutine(
                name="response",
                rl_label="action",
                duration=1.0,
                key_dict=key_dict,
                timeout_action=1.0,
                presentation_settings={
                    "name_before": "target",
                },
                stimulus_definitions=[
                    ImageDefinition(
                        name="circle",
                        image=mid_stimuli(
                        other_color="gray",
                        shape="circle",
                        probe=False,
                        amount="",
                        shape_dim=250,
                    ),
                    pos=(0, 0))],
            )
        ]

    final_step = [
        PresentationRoutine(duration=1.0, name="reward-delay"),
        reward_feedback,
        PresentationRoutine(name="iti", duration=1.0, rl_label="obs"),
    ]

    info_dict = {
        0: {"render": []},
        1: {"render": first_step(image_map[0])},
        2: {"render": first_step(image_map[1])},
        3: {"render": first_step(image_map[2])},
        4: {"render": first_step(image_map[3])},
        5: {"render": final_step},
        6: {"render": final_step},
        7: {"render": final_step},
        8: {"render": final_step},
    }

    return info_dict, stimuli
