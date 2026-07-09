"""Runs multiple labeled subprocesses concurrently, prefixing each one's output with its
label, and terminating every child together on interrupt."""
from __future__ import annotations

import subprocess
import sys
import threading


def _pump(process: subprocess.Popen, label: str) -> None:
    assert process.stdout is not None
    for line in process.stdout:
        sys.stdout.write(f"[{label}] {line}")
        sys.stdout.flush()
    process.stdout.close()


def run_labeled_processes(commands: dict[str, list[str]]) -> int:
    """Run each command concurrently, prefixing its output lines with its label.

    Blocks until every process exits, or until interrupted (Ctrl+C) - in which case
    every child is terminated before this returns. Returns the highest exit code
    across all children.
    """
    processes: dict[str, subprocess.Popen] = {}
    threads: list[threading.Thread] = []

    for label, cmd in commands.items():
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
        )
        processes[label] = proc
        thread = threading.Thread(target=_pump, args=(proc, label), daemon=True)
        thread.start()
        threads.append(thread)

    try:
        for proc in processes.values():
            proc.wait()
    except KeyboardInterrupt:
        sys.stdout.write("\nInterrupted - terminating all watchers...\n")
        for proc in processes.values():
            proc.terminate()
        for proc in processes.values():
            proc.wait()

    for thread in threads:
        thread.join(timeout=2)

    return max((proc.returncode or 0) for proc in processes.values())
