"""Pytest configuration for wordcount-cli.

Makes the single-file CLI importable as a module from a clean checkout, so
``pytest`` works from the project root without installing the package.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
