#!/usr/bin/env python3
"""Preferred v2 entry point; delegates to agent_use_audit.py for compatibility."""
from agent_use_audit import main

if __name__ == "__main__":
    raise SystemExit(main())
