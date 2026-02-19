import os
import sys

from orchestrator import user_proxy, manager
from spinner import SpinnerStream

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

    # Wrap stdout to replace "Next speaker:" with spinner
    spinner_stream = SpinnerStream(sys.stdout)
    sys.stdout = spinner_stream

    chat_result = user_proxy.initiate_chat(
        manager,
        message=user_input,
    )

    # Restore stdout
    spinner_stream.stop()
    sys.stdout = spinner_stream._original

    print("\n" + "=" * 60)
    print("  Planning Session Complete")
    print("=" * 60)
    print(f"\nTotal messages: {len(chat_result.chat_history)}")
    print(f"Cost: {chat_result.cost}")

    # Ask user if they agree with the plan
    print("\n" + "-" * 60)
    confirm = input("Do you agree with this plan and want to generate the codebase? (yes/no): ").strip().lower()

    if confirm not in ("yes", "y"):
        print("Codebase generation skipped. Goodbye!")
        return

    # Ask for output folder
    output_dir = input("Enter the folder path to store the generated source code:\n> ").strip()
    if not output_dir:
        print("No folder path provided. Aborting.")
        return

    output_dir = os.path.expanduser(output_dir)
    output_dir = os.path.abspath(output_dir)

    if os.path.exists(output_dir) and os.listdir(output_dir):
        overwrite = input(f"Folder '{output_dir}' is not empty. Continue anyway? (yes/no): ").strip().lower()
        if overwrite not in ("yes", "y"):
            print("Aborted.")
            return

    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "-" * 60)
    print("Generating codebase from the plan...")
    print("-" * 60 + "\n")

    from codegen import generate_codebase

    file_count = generate_codebase(chat_result.chat_history, output_dir)

    print("\n" + "=" * 60)
    print(f"  Code Generation Complete — {file_count} files created")
    print(f"  Output: {output_dir}")
    print("=" * 60)


if __name__ == "__main__":
    main()
