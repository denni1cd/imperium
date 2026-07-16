from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected repair block not found in {path}")
    path.write_text(text.replace(old, new), encoding="utf-8")


provider = ROOT / "src/imperium/offline/provider_engine.py"
replace_exact(
    provider,
    '''    @staticmethod
    def _claims_with_new_input(
        previous: ClaimRegister | None,
        current: ClaimRegister,
        responses: tuple[ChallengeResponse, ...] = (),
        challenges: tuple[ChallengeArtifact, ...] = (),
    ) -> tuple[str, ...]:
        if previous is None:
            return tuple(claim.claim_id for claim in current.claims)
        prior_ids = {claim.claim_id for claim in previous.claims}
        new_ids = {claim.claim_id for claim in current.claims if claim.claim_id not in prior_ids}
        challenged_claim_ids = {
            challenge.challenge_id: challenge.target_claim_id for challenge in challenges
        }
        revised_ids = {
            challenged_claim_ids[response.challenge_id]
            for response in responses
            if response.revised_claim is not None
            and response.challenge_id in challenged_claim_ids
        }
        return tuple(
            claim.claim_id
            for claim in current.claims
            if claim.claim_id in new_ids or claim.claim_id in revised_ids
        )
''',
    '''    @staticmethod
    def _claims_with_new_input(
        previous: ClaimRegister | None,
        current: ClaimRegister,
        responses: tuple[ChallengeResponse, ...] = (),
        challenges: tuple[ChallengeArtifact, ...] = (),
        *,
        phase: ChallengePhase | None = None,
        prior_round_number: int | None = None,
    ) -> tuple[str, ...]:
        """Return claims with inspectable, protocol-approved material new input.

        A carried claim qualifies only when the immediately preceding round accepted a
        REFINE response and the next canonical register contains that exact normalized
        revision. Merely changing another field, regenerating the register, or attaching
        an unincorporated ``revised_claim`` does not unlock a repeated challenge.
        """

        active_phase = phase or current.phase
        if current.phase is not active_phase or (
            previous is not None and previous.phase is not active_phase
        ):
            raise ValueError("claim registers must match the active challenge phase")
        if previous is None:
            return tuple(claim.claim_id for claim in current.claims)

        def normalize(value: str) -> str:
            return " ".join(value.split()).casefold()

        prior_by_id = {claim.claim_id: claim for claim in previous.claims}
        current_by_id = {claim.claim_id: claim for claim in current.claims}
        new_ids = set(current_by_id) - set(prior_by_id)
        eligible_challenges = {
            challenge.challenge_id: challenge
            for challenge in challenges
            if challenge.phase is active_phase
            and (
                prior_round_number is None
                or challenge.round_number == prior_round_number
            )
        }

        revised_ids: set[str] = set()
        for response in responses:
            challenge = eligible_challenges.get(response.challenge_id)
            if (
                challenge is None
                or response.disposition is not ChallengeDisposition.REFINE
                or response.revised_claim is None
                or response.member_id != challenge.target_member_id
            ):
                continue
            prior_claim = prior_by_id.get(challenge.target_claim_id)
            current_claim = current_by_id.get(challenge.target_claim_id)
            if prior_claim is None or current_claim is None:
                continue
            prior_text = normalize(prior_claim.statement)
            revised_text = normalize(response.revised_claim)
            current_text = normalize(current_claim.statement)
            if revised_text != prior_text and current_text == revised_text:
                revised_ids.add(challenge.target_claim_id)

        return tuple(
            claim.claim_id
            for claim in current.claims
            if claim.claim_id in new_ids or claim.claim_id in revised_ids
        )
''',
)
replace_exact(
    provider,
    '''            new_input_claim_ids = self._claims_with_new_input(
                previous_claims,
                claims,
                session.record.challenge_responses,
                session.protocol_trace.challenges,
            )
''',
    '''            new_input_claim_ids = self._claims_with_new_input(
                previous_claims,
                claims,
                session.record.challenge_responses,
                session.protocol_trace.challenges,
                phase=phase,
                prior_round_number=round_number - 1,
            )
''',
)

fixtures = ROOT / "src/imperium/offline/fixtures.py"
replace_exact(
    fixtures,
    '''        else "Stage 4 should implement the complete challenged path plus explicit empty, halt, "
        "conditional, and interruption acceptance fixtures before local review."
''',
    '''        else "Implement the challenged complete path plus explicit empty, halt, conditional, "
        "and interruption acceptance fixtures before local review."
''',
)

tests = ROOT / "tests/test_provider_bound_engine.py"
replace_exact(
    tests,
    '''from imperium.domain.enums import (
    ChallengePhase,
''',
    '''from imperium.domain.enums import (
    ChallengeDisposition,
    ChallengePhase,
''',
)
replace_exact(
    tests,
    '''def test_accepted_revised_claim_is_material_new_input() -> None:
    scenario = build_challenged_scenario()
    first, second = scenario.proposal_rounds

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        first.claim_register,
        second.claim_register,
        first.responses,
        first.challenges,
    ) == ("claim-vanguard-scope", "claim-architect-reuse")


def test_genuinely_new_claim_id_is_material_new_input() -> None:
''',
    '''def test_only_incorporated_refinement_is_material_new_input() -> None:
    scenario = build_challenged_scenario()
    first, second = scenario.proposal_rounds

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        first.claim_register,
        second.claim_register,
        first.responses,
        first.challenges,
        phase=ChallengePhase.PROPOSAL,
        prior_round_number=1,
    ) == ("claim-vanguard-scope",)


def test_unincorporated_refinement_is_not_material_new_input() -> None:
    scenario = build_challenged_scenario()
    first, second = scenario.proposal_rounds
    unchanged = second.claim_register.model_copy(
        update={
            "claims": (
                first.claim_register.claims[0],
                *second.claim_register.claims[1:],
            )
        }
    )

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        first.claim_register,
        unchanged,
        first.responses,
        first.challenges,
        phase=ChallengePhase.PROPOSAL,
        prior_round_number=1,
    ) == ()


def test_non_refine_response_cannot_unlock_repetition() -> None:
    scenario = build_challenged_scenario()
    first, second = scenario.proposal_rounds
    scope_response = first.responses[0].model_copy(
        update={"disposition": ChallengeDisposition.DEFEND}
    )

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        first.claim_register,
        second.claim_register,
        (scope_response,),
        first.challenges,
        phase=ChallengePhase.PROPOSAL,
        prior_round_number=1,
    ) == ()


def test_other_round_refinement_cannot_unlock_repetition() -> None:
    scenario = build_challenged_scenario()
    first, second = scenario.proposal_rounds

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        first.claim_register,
        second.claim_register,
        first.responses,
        first.challenges,
        phase=ChallengePhase.PROPOSAL,
        prior_round_number=2,
    ) == ()


def test_genuinely_new_claim_id_is_material_new_input() -> None:
''',
)

doc = ROOT / "docs/STAGE_5_GATE_2_PROVIDER_INJECTION.md"
replace_exact(
    doc,
    '''## Stop Condition Applied

The Gate 2 stop condition is now active. Implementation pauses here because the behavior was achieved with enough duplicated orchestration and validation-order risk to require design review before further expansion.
''',
    '''## Review Boundary Applied

The shared-engine, validation-order, and material-new-input blockers are resolved under simulated providers. Implementation pauses here for merge review; Gate 2E failure accounting, cumulative usage budgets, captured-session replay, and every complete live council remain blocked.
''',
)
