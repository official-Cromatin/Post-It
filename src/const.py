from pathlib import Path

# Read VERSION file
with open(Path(__file__).resolve().parent / "VERSION") as f:
    VERSION = f.read().strip()


__all__ = VERSION
