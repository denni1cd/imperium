from pathlib import Path

path = Path(__file__).with_name("apply_gate2e_attempt_slice.py")
text = path.read_text(encoding="utf-8")
replacements = {
    "- [`STAGE_5_GATE_2_PROVIDER_INJECTION.md`](STAGE_5_GATE_2_PROVIDER_INJECTION.md) — accepted Gate 2 contract: replay extraction, provider authority, bounded rounds, evidence disposition, shared-engine consolidation, and material second-round validation.":
    "- [`STAGE_5_GATE_2_PROVIDER_INJECTION.md`](STAGE_5_GATE_2_PROVIDER_INJECTION.md) — current Gate 2 contract and architecture review: replay extraction, provider authority, bounded rounds, evidence disposition, shared-engine consolidation, and remaining live-safety controls.",
    "The current engineering gate is Gate 2E live-attempt accounting and cumulative usage controls. PR #13 completed provider-authority consolidation; a complete live council remains blocked.":
    "The current engineering gate is merge review of the completed Gate 2 shared-engine consolidation. Gate 2E live-failure accounting and every complete live council remain blocked.",
    "- **Stage 5 Gate 2:** draft PR #13 resolves the shared-engine architecture gate under simulated providers; final review remains before merge.":
    "- **Stage 5 Gate 2:** draft PR #13 resolves the shared-engine architecture gate under simulated providers; merge review is pending.",
    "- **Current gate:** review the consolidated Gate 2 implementation before Gate 2E live-failure accounting or any complete live council.":
    "- **Current gate:** review and merge Gate 2 before Gate 2E live-failure accounting or any complete live council.",
    '''        self._validate_attempts()
        self._validate_council_snapshot()
        if self.artifact_authority == "scenario":''':
    '''        self._validate_council_snapshot()
        if self.artifact_authority == "scenario":''',
    '''    def _replace_attempt(session: OfflineSession, updated: ModelAttempt) -> OfflineSession:
        attempts = tuple(
            updated if item.attempt_id == updated.attempt_id else item
            for item in session.attempts
        )
        return _replace_session(session, attempts=attempts)
''':
    '''    def _replace_attempt(
        session: OfflineSession,
        updated: ModelAttempt,
        **updates: object,
    ) -> OfflineSession:
        attempts = tuple(
            updated if item.attempt_id == updated.attempt_id else item
            for item in session.attempts
        )
        return _replace_session(session, attempts=attempts, **updates)
''',
    '''            failed = self._replace_attempt(pending, terminal)
            failed = _replace_session(
                failed,
                pending_call_key=None,
                checkpoint_sequence=failed.checkpoint_sequence + 1,
            )
''':
    '''            failed = self._replace_attempt(
                pending,
                terminal,
                pending_call_key=None,
                checkpoint_sequence=pending.checkpoint_sequence + 1,
            )
''',
    '''        committed = self._replace_attempt(committed, accepted_attempt)
        call_record = ModelCallRecord(
''':
    '''        accepted_attempts = tuple(
            accepted_attempt if item.attempt_id == accepted_attempt.attempt_id else item
            for item in committed.attempts
        )
        call_record = ModelCallRecord(
''',
    '''        committed = _replace_session(
            committed,
            record=record,
''':
    '''        committed = _replace_session(
            committed,
            attempts=accepted_attempts,
            record=record,
''',
    '''        estimated_input_tokens = self._check_pre_call_budget(
            session,
            serialized_provider_input=f"{prompt.content}\\n{input_text}",
        )
''':
    '''        try:
            estimated_input_tokens = self._check_pre_call_budget(
                session,
                serialized_provider_input=f"{prompt.content}\\\\n{input_text}",
            )
        except Exception as exc:
            self._attach_attempt_session(exc, session)
            raise
''',
}
for old, new in replacements.items():
    if old not in text:
        raise RuntimeError(f"expected stale patch text not found: {old[:80]!r}")
    text = text.replace(old, new, 1)

post_authority_attempt_validation = """
replace_exact(
    "src/imperium/offline/models.py",
    '''        else:
            self._validate_provider_artifacts()

        artifact_kinds = self._artifact_kind_index()
''',
    '''        else:
            self._validate_provider_artifacts()

        self._validate_attempts()
        artifact_kinds = self._artifact_kind_index()
''',
)
"""
if "post-authority attempt validation" not in text:
    text += "\n# post-authority attempt validation\n" + post_authority_attempt_validation
path.write_text(text, encoding="utf-8")
