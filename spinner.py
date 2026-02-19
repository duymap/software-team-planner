import threading
import re

AGENT_LABELS = {
    "pm": "Project Manager planning",
    "architect": "Architect designing system",
    "developer": "Developer creating implementation",
    "reviewer": "Reviewer analyzing plan",
    "qa": "QA defining test strategy",
    "coder": "Coder generating source code",
}

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

GREEN = "\033[32m"
RESET = "\033[0m"

NEXT_SPEAKER_RE = re.compile(r"Next speaker: (\w+)")
AGENT_HEADER_RE = re.compile(r"^(\w+) \(to [\w\s]+\):\s*$")


class AgentSpinner:
    """Spinner that shows while an agent is thinking."""

    def __init__(self, target_stream):
        self._stream = target_stream
        self._thread = None
        self._stop_event = threading.Event()
        self._label = ""

    def start(self, label: str):
        self.stop()
        self._label = label
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self):
        if self._thread and self._thread.is_alive():
            self._stop_event.set()
            self._thread.join(timeout=1)
        self._thread = None

    def _spin(self):
        idx = 0
        while not self._stop_event.is_set():
            frame = SPINNER_FRAMES[idx % len(SPINNER_FRAMES)]
            self._stream.write(f"\r{GREEN}{frame} {self._label}...{RESET}")
            self._stream.flush()
            idx += 1
            self._stop_event.wait(timeout=0.1)


class SpinnerStream:
    """Wraps stdout to intercept AG2 'Next speaker' lines and show a spinner instead."""

    def __init__(self, original_stdout):
        self._original = original_stdout
        self._spinner = AgentSpinner(original_stdout)
        self._buffer = ""

    def write(self, text: str):
        self._buffer += text
        if "\n" not in self._buffer:
            return

        lines = self._buffer.split("\n")
        self._buffer = lines[-1]

        for line in lines[:-1]:
            stripped = line.strip()

            # Intercept "Next speaker: agent_name" → start spinner
            match = NEXT_SPEAKER_RE.search(stripped)
            if match:
                agent_name = match.group(1).lower()
                label = AGENT_LABELS.get(agent_name, f"{agent_name} working")
                self._spinner.start(label)
                continue

            # Intercept "agent_name (to chat_manager):" → stop spinner, print header
            header_match = AGENT_HEADER_RE.match(stripped)
            if header_match:
                self._spinner.stop()
                agent_name = header_match.group(1).lower()
                label = AGENT_LABELS.get(agent_name, agent_name.upper())
                self._original.write(f"\n{'─' * 60}\n")
                self._original.write(f"  {GREEN}{label} — response:{RESET}\n")
                self._original.write(f"{'─' * 60}\n")
                self._original.flush()
                continue

            # Pass through everything else
            self._original.write(line + "\n")

    def flush(self):
        if self._buffer.strip():
            self._original.write(self._buffer)
            self._buffer = ""
        self._original.flush()

    def fileno(self):
        return self._original.fileno()

    @property
    def encoding(self):
        return self._original.encoding

    def isatty(self):
        return self._original.isatty()

    def stop(self):
        """Stop any active spinner and flush."""
        self._spinner.stop()
        self.flush()
