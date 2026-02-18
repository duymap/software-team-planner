from autogen import ConversableAgent, GroupChat, GroupChatManager

from agents import create_agents
from config import reasoning_config


pm, architect, developer, reviewer, qa = create_agents()

# User proxy agent to initiate the chat so the PM actually processes the input
user_proxy = ConversableAgent(
    name="user",
    system_message="You are the user who submits a project idea for the team to plan.",
    human_input_mode="NEVER",
    llm_config=False,
    max_consecutive_auto_reply=0,
)


def select_next_speaker(last_speaker, groupchat):
    """Custom speaker selection enforcing the pipeline flow with reviewer feedback loop."""
    last_msg = groupchat.messages[-1]["content"].lower()

    if last_speaker == user_proxy:
        return pm
    elif last_speaker == pm:
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


allowed_transitions = {
    user_proxy: [pm],
    pm: [architect],
    architect: [developer],
    developer: [reviewer],
    reviewer: [developer, qa],
    qa: [user_proxy],
}

group_chat = GroupChat(
    agents=[user_proxy, pm, architect, developer, reviewer, qa],
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
