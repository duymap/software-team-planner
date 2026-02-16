from orchestrator import pm, manager

DEFAULT_PROJECT_IDEA = (
    "Build a REST API for a task management app with user auth, "
    "CRUD operations, and real-time notifications"
)


def main():
    print("=" * 60)
    print("  Software Project Planner — Multi-Agent System")
    print("=" * 60)

    user_input = input("\nEnter your project idea (or press Enter for demo):\n> ").strip()
    if not user_input:
        user_input = DEFAULT_PROJECT_IDEA
        print(f"\nUsing default: {user_input}")

    print("\n" + "-" * 60)
    print("Starting multi-agent planning session...")
    print("-" * 60 + "\n")

    chat_result = pm.initiate_chat(
        manager,
        message=user_input,
    )

    print("\n" + "=" * 60)
    print("  Planning Session Complete")
    print("=" * 60)
    print(f"\nTotal messages: {len(chat_result.chat_history)}")
    print(f"Cost: {chat_result.cost}")


if __name__ == "__main__":
    main()
