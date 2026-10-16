"""python -m s7conv — то же, что консольная команда s7conv."""

from __future__ import annotations

import sys

from s7conv.cli import main

if __name__ == "__main__":
    sys.exit(main())
