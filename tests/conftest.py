"""Reusable fixtures for zero-model protocol tests."""

from decimal import Decimal

import pytest

from imperium.domain.models import MemberProfile, SovereignRequest, ValueVector


@pytest.fixture
def value_vector() -> ValueVector:
    return ValueVector(weights={"economy": Decimal("0.6"), "reliability": Decimal("0.4")})


@pytest.fixture
def member(value_vector: ValueVector) -> MemberProfile:
    return MemberProfile(
        member_id="accountant",
        title="Accountant",
        purpose="Protect strategic value from unjustified resource commitments.",
        values=value_vector,
        doctrine=("Treat every commitment as carrying an opportunity cost.",),
        jurisdiction=("resource allocation",),
        vigilance=("hidden recurring costs",),
        revision_triggers=("demonstrated lifecycle savings",),
    )


@pytest.fixture
def sovereign_request() -> SovereignRequest:
    return SovereignRequest(
        original_text="Decide whether to launch a new strategic project.",
        goals=("Produce an actionable recommendation.",),
        hard_constraints=("Do not exceed available capacity.",),
        supplied_facts=("The user has limited weekly time.",),
    )
