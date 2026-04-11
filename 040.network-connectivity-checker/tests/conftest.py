"""
Shared pytest fixtures for check_network_connectivity tests.
"""
import sys
import os

import pytest

# Make the scripts directory importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
