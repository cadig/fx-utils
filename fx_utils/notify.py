"""Local notification helpers (currently: macOS `say` text-to-speech)."""
from __future__ import annotations

import shutil
import subprocess


def speak(message: str) -> None:
    """Speak `message` via macOS `say`. No-op (silently) if `say` isn't available."""
    say_path = shutil.which("say")
    if say_path is None:
        return
    subprocess.run([say_path, message], check=False)
