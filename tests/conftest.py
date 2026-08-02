import copy
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools.check_invariants import load_sources_ledger  # noqa: E402

SEED = REPO / "data" / "2026-07-31.seed.json"


@pytest.fixture(scope="session")
def seed():
    return json.loads(SEED.read_text(encoding="utf-8"))


@pytest.fixture()
def snap(seed):
    """Mutable deep copy of the seed for violation-crafting tests."""
    return copy.deepcopy(seed)


@pytest.fixture(scope="session")
def ledger():
    return load_sources_ledger(REPO / "governance" / "SOURCES.md")
