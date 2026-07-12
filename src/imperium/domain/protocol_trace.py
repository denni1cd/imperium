"""Inspectable Stage 3 record fragment for normalized debate state."""

from __future__ import annotations

from pydantic import model_validator

from imperium.domain.enums import ChallengePhase
from imperium.domain.models import StrictModel
from imperium.domain.protocol import ChallengePlan, ClaimRegister, ContinuationDecision


class ProtocolTrace(StrictModel):
    """Typed protocol artifacts that Stage 4 will attach to a deliberation session."""

    claim_registers: tuple[ClaimRegister, ...] = ()
    challenge_plans: tuple[ChallengePlan, ...] = ()
    continuation_decisions: tuple[ContinuationDecision, ...] = ()

    @model_validator(mode="after")
    def validate_phase_records(self) -> "ProtocolTrace":
        register_phases = [register.phase for register in self.claim_registers]
        if len(set(register_phases)) != len(register_phases):
            raise ValueError("a protocol trace may contain only one claim register per phase")

        plan_keys = [(plan.phase, plan.round_number) for plan in self.challenge_plans]
        if len(set(plan_keys)) != len(plan_keys):
            raise ValueError("challenge plan phase and round combinations must be unique")

        decision_keys = [
            (decision.phase, decision.completed_round)
            for decision in self.continuation_decisions
        ]
        if len(set(decision_keys)) != len(decision_keys):
            raise ValueError("continuation decision phase and round combinations must be unique")

        plan_key_set = set(plan_keys)
        missing_plans = set(decision_keys) - plan_key_set
        if missing_plans:
            rendered = sorted((phase.value, round_number) for phase, round_number in missing_plans)
            raise ValueError(
                "every continuation decision requires a matching challenge plan: "
                f"{rendered}"
            )

        known_phases = {ChallengePhase.FRAME, ChallengePhase.PROPOSAL}
        if set(register_phases) - known_phases:
            raise ValueError("protocol trace contains an unsupported challenge phase")
        return self
