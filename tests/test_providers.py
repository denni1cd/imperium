"""Tests for zero-cost provider substitutes."""

from decimal import Decimal

import pytest

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import FrameRegister, Interpretation
from imperium.providers.base import CallMetadata, ProviderError
from imperium.providers.fake import FakeProvider
from imperium.providers.replay import ReplayProvider


def interpretation() -> Interpretation:
    return Interpretation(
        member_id="accountant",
        core_decision="Whether the expected value justifies the commitment.",
        desired_outcome="A plan with bounded opportunity cost.",
        risks=("The project consumes scarce capacity.",),
        assumptions=("The expected demand is real.",),
        initial_inclination="Validate before committing.",
        value_influence={"economy": "Prioritize lifecycle return over novelty."},
        confidence=Decimal("0.7"),
    )


def metadata(call_key: str = "interpret.accountant") -> CallMetadata:
    return CallMetadata(
        session_id="session-1",
        call_key=call_key,
        stage=DeliberationStage.COUNCIL_SELECTED,
        member_id="accountant",
    )


@pytest.mark.asyncio
async def test_fake_provider_returns_queued_artifact() -> None:
    expected = interpretation()
    provider = FakeProvider((expected,))

    result = await provider.generate(
        model="test-model",
        instructions="Interpret independently.",
        input_text="request",
        output_type=Interpretation,
        metadata=metadata(),
    )

    assert result.output == expected
    assert result.provider == "fake"
    assert provider.remaining == 0
    assert provider.calls == [metadata()]


@pytest.mark.asyncio
async def test_fake_provider_rejects_wrong_artifact_type() -> None:
    provider = FakeProvider((FrameRegister(),))

    with pytest.raises(ProviderError, match="expected Interpretation"):
        await provider.generate(
            model="test-model",
            instructions="Interpret independently.",
            input_text="request",
            output_type=Interpretation,
            metadata=metadata(),
        )


@pytest.mark.asyncio
async def test_replay_provider_validates_recorded_output() -> None:
    expected = interpretation()
    provider = ReplayProvider(
        {
            "interpret.accountant": [
                {
                    "output": expected.model_dump(mode="json"),
                    "provider": "codex-cli",
                    "model": "recorded-model",
                    "input_tokens": 120,
                    "output_tokens": 80,
                }
            ]
        }
    )

    result = await provider.generate(
        model="fallback-model",
        instructions="Interpret independently.",
        input_text="request",
        output_type=Interpretation,
        metadata=metadata(),
    )

    assert result.output == expected
    assert result.provider == "codex-cli"
    assert result.model == "recorded-model"
    assert result.input_tokens == 120
    assert result.output_tokens == 80


@pytest.mark.asyncio
async def test_replay_provider_requires_matching_key() -> None:
    provider = ReplayProvider({})

    with pytest.raises(ProviderError, match="no replay record"):
        await provider.generate(
            model="test-model",
            instructions="Interpret independently.",
            input_text="request",
            output_type=Interpretation,
            metadata=metadata(),
        )
