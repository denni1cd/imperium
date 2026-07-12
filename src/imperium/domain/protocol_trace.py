"""Inspectable Stage 3 record fragment for normalized debate state."""

from __future__ import annotations

from pydantic import Field, model_validator

from imperium.domain.enums import ChallengePhase
from imperium.domain.models import StrictModel
from imperium.domain.protocol import (
    ChallengeArtifact,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
)


class ClaimRegisterSnapshot(StrictModel):
    """Versioned canonical claims visible for one phase and debate round."""

    phase: ChallengePhase
    round_number: int = Field(ge=0)
    claim_register: ClaimRegister
    supersedes_register_id: str | None = None

    @model_validator(mode="after")
    def validate_snapshot(self) -> "ClaimRegisterSnapshot":
        if self.claim_register.phase is not self.phase:
            raise ValueError("claim-register snapshot phase must match the register")
        if self.round_number == 0 and self.supersedes_register_id is not None:
            raise ValueError("the initial claim register cannot supersede another register")
        if self.round_number > 0 and not self.supersedes_register_id:
            raise ValueError("a later claim-register snapshot must identify what it supersedes")
        return self


class ProtocolTrace(StrictModel):
    """Typed protocol artifacts that Stage 4 will attach to a deliberation session."""

    claim_register_snapshots: tuple[ClaimRegisterSnapshot, ...] = ()
    challenge_plans: tuple[ChallengePlan, ...] = ()
    challenges: tuple[ChallengeArtifact, ...] = ()
    continuation_decisions: tuple[ContinuationDecision, ...] = ()

    @model_validator(mode="after")
    def validate_phase_records(self) -> "ProtocolTrace":
        snapshot_keys = [
            (snapshot.phase, snapshot.round_number)
            for snapshot in self.claim_register_snapshots
        ]
        if len(set(snapshot_keys)) != len(snapshot_keys):
            raise ValueError("claim-register phase and round combinations must be unique")

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

        assignment_by_id = {
            assignment.challenge_id: assignment
            for plan in self.challenge_plans
            for assignment in plan.assignments
        }
        challenge_ids = [challenge.challenge_id for challenge in self.challenges]
        if len(set(challenge_ids)) != len(challenge_ids):
            raise ValueError("authored challenge identifiers must be unique")

        for challenge in self.challenges:
            assignment = assignment_by_id.get(challenge.challenge_id)
            if assignment is None:
                raise ValueError(
                    f"authored challenge {challenge.challenge_id!r} has no assignment"
                )
            expected = (
                assignment.phase,
                assignment.round_number,
                assignment.challenger_member_id,
                assignment.target_member_id,
                assignment.target_artifact_id,
                assignment.target_claim_id,
            )
            actual = (
                challenge.phase,
                challenge.round_number,
                challenge.challenger_member_id,
                challenge.target_member_id,
                challenge.target_artifact_id,
                challenge.target_claim_id,
            )
            if actual != expected:
                raise ValueError(
                    f"authored challenge {challenge.challenge_id!r} does not match its assignment"
                )

        snapshots_by_phase: dict[ChallengePhase, list[ClaimRegisterSnapshot]] = {}
        for snapshot in self.claim_register_snapshots:
            snapshots_by_phase.setdefault(snapshot.phase, []).append(snapshot)

        for phase, snapshots in snapshots_by_phase.items():
            ordered = sorted(snapshots, key=lambda item: item.round_number)
            rounds = [snapshot.round_number for snapshot in ordered]
            if rounds[0] != 0 or rounds != list(range(rounds[-1] + 1)):
                raise ValueError(
                    f"claim-register snapshots for {phase.value!r} must begin at round 0 "
                    "and remain contiguous"
                )
            for previous, current in zip(ordered, ordered[1:], strict=False):
                if current.supersedes_register_id != previous.claim_register.register_id:
                    raise ValueError(
                        f"claim-register snapshot round {current.round_number} for "
                        f"{phase.value!r} must supersede the prior register"
                    )
        return self
