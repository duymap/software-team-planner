from autogen import GroupChat, GroupChatManager

from agents import create_agents
from config import reasoning_config


def select_next_speaker(last_speaker, groupchat):
    """Custom speaker selection enforcing the pipeline flow with reviewer feedback loop."""
    last_msg = groupchat.messages[-1]["content"].lower()

    if last_speaker == pm:
        return architect
    elif last_speaker == architect:
        return developer
    elif last_speaker == developer:
        return reviewer
    elif last_speaker == reviewer:
        if "approved" in last_msg:
            return qa
        else:
            return developer  # feedback loop
    elif last_speaker == qa:
        return None  # terminate
    return None


pm, architect, developer, reviewer, qa = create_agents()

allowed_transitions = {
    pm: [architect],
    architect: [developer],
    developer: [reviewer],
    reviewer: [developer, qa],
    qa: [pm],
}

group_chat = GroupChat(
    agents=[pm, architect, developer, reviewer, qa],
    allowed_or_disallowed_speaker_transitions=allowed_transitions,
    speaker_transitions_type="allowed",
    messages=[],
    max_round=15,
    send_introductions=True,
    speaker_selection_method=select_next_speaker,
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=reasoning_config,
    is_termination_msg=lambda msg: "final sign-off" in msg.get("content", "").lower(),
)
