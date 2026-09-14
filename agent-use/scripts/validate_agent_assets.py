#!/usr/bin/env python3
"""Preferred v2 validation entry point; delegates to validate_skill.py."""
import sys
sys.dont_write_bytecode = True
from validate_skill import main

if __name__ == "__main__":
    raise SystemExit(main())
