from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected block not found in {relative}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_between(relative: str, start: str, end: str, replacement: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    start_index = text.find(start)
    if start_index < 0:
        raise RuntimeError(f"start marker not found in {relative}: {start!r}")
    end_index = text.find(end, start_index)
    if end_index < 0:
        raise RuntimeError(f"end marker not found in {relative}: {end!r}")
    path.write_text(
        text[:start_index] + replacement + text[end_index:],
        encoding="utf-8",
    )


# Provider-neutral usage and ambiguity metadata.
replace_exact(
    "src/imperium/providers/base.py",
    "from pydantic import BaseModel, Field\n",
    "from pydantic import BaseModel, Field, model_validator\n",
)
replace_exact(
    "src/imperium/providers/base.py",
    '''class ProviderError(RuntimeError):
    """Raised when a model provider cannot return a valid requested artifact."""


class CallMetadata''',
    '''class ProviderError(RuntimeError):
    """Raised when a model provider cannot return a valid requested artifact."""


class ProviderAmbiguousError(ProviderError):
    """Raised when a provider may have consumed resources but its outcome is unknown."""


class CallMetadata''',
)
replace_exact(
    "src/imperium/providers/base.py",
    '''    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
    retries: int = Field(default=0, ge=0)


class ModelProvider''',
    '''    input_tokens: int = Field(default=0, ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
    retries: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def cached_tokens_are_part_of_input(self):
        if self.cached_input_tokens > self.input_tokens:
            raise ValueError("cached input tokens cannot exceed total input tokens")
        return self


class ModelProvider''',
)

# Codex usage extraction and ambiguous outcomes.
replace_exact(
    "src/imperium/providers/codex_cli.py",
    "from imperium.providers.base import CallMetadata, ModelResult, ProviderError\n",
    "from imperium.providers.base import (\n    CallMetadata,\n    ModelResult,\n    ProviderAmbiguousError,\n    ProviderError,\n)\n",
)
replace_between(
    "src/imperium/providers/codex_cli.py",
    "def _extract_usage(",
    "def _extract_string(",
    '''def _extract_usage(events: tuple[Mapping[str, Any], ...]) -> tuple[int, int, int]:
    input_keys = ("input_tokens", "inputTokens", "prompt_tokens", "promptTokens")
    cached_keys = (
        "cached_input_tokens",
        "cachedInputTokens",
        "cached_tokens",
        "cachedTokens",
    )
    output_keys = ("output_tokens", "outputTokens", "completion_tokens", "completionTokens")
    for event in reversed(events):
        for mapping in _walk_mappings(event):
            input_tokens = _first_int(mapping, input_keys)
            output_tokens = _first_int(mapping, output_keys)
            if input_tokens is not None and output_tokens is not None:
                cached_input_tokens = _first_int(mapping, cached_keys) or 0
                return input_tokens, cached_input_tokens, output_tokens
    return 0, 0, 0


''',
)
replace_exact(
    "src/imperium/providers/codex_cli.py",
    '''            raise ProviderError(
                f"Codex CLI timed out after {self.timeout_seconds:g} seconds; "
                "the call was not retried"
            ) from exc''',
    '''            raise ProviderAmbiguousError(
                f"Codex CLI timed out after {self.timeout_seconds:g} seconds; "
                "the call was not retried and its usage outcome is unknown"
            ) from exc''',
)
replace_exact(
    "src/imperium/providers/codex_cli.py",
    '                raise ProviderError("Codex CLI completed without writing the final structured output")',
    '                raise ProviderAmbiguousError(\n                    "Codex CLI completed without writing the final structured output; "\n                    "the call was not retried and its accepted-output state is unknown"\n                )',
)
replace_exact(
    "src/imperium/providers/codex_cli.py",
    "        input_tokens, output_tokens = _extract_usage(events)\n",
    "        input_tokens, cached_input_tokens, output_tokens = _extract_usage(events)\n",
)
replace_exact(
    "src/imperium/providers/codex_cli.py",
    '''            input_tokens=input_tokens,
            output_tokens=output_tokens,''',
    '''            input_tokens=input_tokens,
            cached_input_tokens=cached_input_tokens,
            output_tokens=output_tokens,''',
)

# Smoke reporting carries cached usage too.
replace_exact(
    "src/imperium/live/models.py",
    '''    input_tokens: Annotated[int, Field(ge=0)]
    output_tokens: Annotated[int, Field(ge=0)]''',
    '''    input_tokens: Annotated[int, Field(ge=0)]
    cached_input_tokens: Annotated[int, Field(ge=0)] = 0
    output_tokens: Annotated[int, Field(ge=0)]''',
)
replace_exact(
    "src/imperium/live/smoke.py",
    '''        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,''',
    '''        input_tokens=result.input_tokens,
        cached_input_tokens=result.cached_input_tokens,
        output_tokens=result.output_tokens,''',
)

# Persist attempts and validate accepted-output digests.
replace_exact(
    "src/imperium/offline/models.py",
    "from imperium.domain.protocol_trace import ProtocolTrace\n",
    '''from imperium.domain.protocol_trace import ProtocolTrace
from imperium.offline.attempts import (
    AttemptStatus,
    ModelAttempt,
    UsageBudget,
    artifact_digest,
)
''',
)
replace_exact(
    "src/imperium/offline/models.py",
    '''    turns: tuple[TurnTrace, ...] = ()
    completed_call_keys: tuple[NonEmptyStr, ...] = ()
    pending_call_key: str | None = None''',
    '''    turns: tuple[TurnTrace, ...] = ()
    attempts: tuple[ModelAttempt, ...] = ()
    usage_budget: UsageBudget = Field(default_factory=UsageBudget)
    completed_call_keys: tuple[NonEmptyStr, ...] = ()
    pending_call_key: str | None = None''',
)
replace_exact(
    "src/imperium/offline/models.py",
    '''        self._validate_council_snapshot()
        if self.artifact_authority == "scenario":''',
    '''        self._validate_attempts()
        self._validate_council_snapshot()
        if self.artifact_authority == "scenario":''',
)
replace_exact(
    "src/imperium/offline/models.py",
    "    def _validate_council_snapshot(self) -> None:\n",
    '''    def _validate_attempts(self) -> None:
        attempt_ids = [item.attempt_id for item in self.attempts]
        if len(attempt_ids) != len(set(attempt_ids)):
            raise ValueError("model attempt IDs must be unique")

        attempts_by_call: dict[str, list[ModelAttempt]] = {}
        for attempt in self.attempts:
            attempts_by_call.setdefault(attempt.call_key, []).append(attempt)
        for call_key, attempts in attempts_by_call.items():
            numbers = sorted(item.attempt_number for item in attempts)
            if numbers != list(range(1, len(numbers) + 1)):
                raise ValueError(f"attempt numbers for {call_key!r} must be contiguous from one")

        pending = [item for item in self.attempts if item.status is AttemptStatus.PENDING]
        if len(pending) > 1:
            raise ValueError("a session cannot contain more than one pending model attempt")
        if pending:
            if self.pending_call_key != pending[0].call_key:
                raise ValueError("pending call key must match the pending model attempt")
        elif self.pending_call_key is not None:
            raise ValueError("pending call key requires a pending model attempt")

        accepted_by_call: dict[str, ModelAttempt] = {}
        for attempt in self.attempts:
            if attempt.status is AttemptStatus.ACCEPTED:
                if attempt.call_key in accepted_by_call:
                    raise ValueError("a call key cannot have multiple accepted model attempts")
                accepted_by_call[attempt.call_key] = attempt
        if self.attempts and set(accepted_by_call) != set(self.completed_call_keys):
            raise ValueError("accepted model attempts and completed call keys must match")

        attempt_by_id = {item.attempt_id: item for item in self.attempts}
        for attempt in self.attempts:
            if attempt.retry_of_attempt_id is not None:
                prior = attempt_by_id.get(attempt.retry_of_attempt_id)
                if (
                    prior is None
                    or prior.call_key != attempt.call_key
                    or prior.attempt_number + 1 != attempt.attempt_number
                    or prior.status is not AttemptStatus.RETRIED
                    or prior.superseded_by_attempt_id != attempt.attempt_id
                ):
                    raise ValueError("retry lineage must identify one explicitly retried prior attempt")
            if attempt.status is AttemptStatus.RETRIED and not any(
                candidate.retry_of_attempt_id == attempt.attempt_id
                for candidate in self.attempts
            ):
                raise ValueError("retried attempts require a persisted replacement attempt")

        if not accepted_by_call:
            return
        turns = {turn.call_key: turn for turn in self.turns}
        calls = {call.call_id: call for call in self.record.model_calls}
        artifacts = self._accepted_artifact_index()
        for call_key, attempt in accepted_by_call.items():
            turn = turns.get(call_key)
            if turn is None or turn.output_artifact_id != attempt.output_artifact_id:
                raise ValueError("accepted attempt output identity must match its turn trace")
            artifact = artifacts.get(attempt.output_artifact_id or "")
            if artifact is None or artifact_digest(artifact) != attempt.output_sha256:
                raise ValueError("accepted attempt output digest does not match checkpoint artifact")
            call = calls.get(call_key)
            if call is None or (
                call.provider != attempt.provider
                or call.model != attempt.model
                or call.input_tokens != attempt.input_tokens
                or call.output_tokens != attempt.output_tokens
                or call.latency_ms != attempt.latency_ms
            ):
                raise ValueError("accepted attempt usage must match its model call record")

    def _accepted_artifact_index(self) -> dict[str, StrictModel]:
        index: dict[str, StrictModel] = {}
        index.update({item.interpretation_id: item for item in self.record.interpretations})
        if self.record.frame_register is not None:
            index["frame-register"] = self.record.frame_register
        index.update({item.proposal_id: item for item in self.record.proposals})
        index.update({item.revision_id: item for item in self.record.revisions})
        index.update({item.challenge_id: item for item in self.protocol_trace.challenges})
        index.update(
            {f"{item.challenge_id}:response": item for item in self.record.challenge_responses}
        )
        index.update(
            {
                item.claim_register.register_id: item.claim_register
                for item in self.protocol_trace.claim_register_snapshots
            }
        )
        index.update({item.plan_id: item for item in self.protocol_trace.challenge_plans})
        index.update(
            {item.decision_id: item for item in self.protocol_trace.continuation_decisions}
        )
        if self.record.adjudication is not None:
            index[self.record.adjudication.adjudication_id] = self.record.adjudication
        if self.record.plan is not None:
            index["actionableplan"] = self.record.plan
        return index

    def _validate_council_snapshot(self) -> None:
''',
)

# Preserve the terminal attempt session when the lifecycle marks a run failed.
replace_exact(
    "src/imperium/offline/engine.py",
    '''        except Exception as exc:
            record = _update_record(session.record, status=SessionStatus.FAILED)
            session = _replace_session(
                session,
                record=record,
                failure_reason=f"{type(exc).__name__}: {exc}",
                pending_call_key=None,
                checkpoint_sequence=session.checkpoint_sequence + 1,
            )''',
    '''        except Exception as exc:
            attempt_session = getattr(exc, "imperium_session", session)
            record = _update_record(attempt_session.record, status=SessionStatus.FAILED)
            session = _replace_session(
                attempt_session,
                record=record,
                failure_reason=f"{type(exc).__name__}: {exc}",
                pending_call_key=None,
                checkpoint_sequence=attempt_session.checkpoint_sequence + 1,
            )''',
)

# Shared engine attempt lifecycle and budgets.
replace_exact(
    "src/imperium/offline/provider_engine.py",
    "from imperium.offline.engine import (\n",
    '''from imperium.offline.attempts import (
    AttemptStatus,
    ModelAttempt,
    RetryAuthorizationRequired,
    UsageBudget,
    UsageBudgetExceeded,
    artifact_digest,
    estimate_input_tokens,
    usage_totals,
)
from imperium.offline.engine import (
''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    "from imperium.providers.base import CallMetadata, ModelProvider, ProviderError\n",
    '''from imperium.providers.base import (
    CallMetadata,
    ModelProvider,
    ProviderAmbiguousError,
    ProviderError,
)
''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    '''        evidence_resolutions: Mapping[str, EvidenceResolution] | None = None,
        artifact_authority: str = "provider",
    ) -> None:''',
    '''        evidence_resolutions: Mapping[str, EvidenceResolution] | None = None,
        usage_budget: UsageBudget | None = None,
        artifact_authority: str = "provider",
    ) -> None:''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    '''        self._session_evidence_resolutions: dict[str, EvidenceResolution] = {}
        self.max_context_bytes = max_context_bytes''',
    '''        self._session_evidence_resolutions: dict[str, EvidenceResolution] = {}
        self._configured_usage_budget = usage_budget
        self.max_context_bytes = max_context_bytes''',
)
replace_between(
    "src/imperium/offline/provider_engine.py",
    "    async def _execute(\n",
    "    def _accepted_output(\n",
    '''    async def _execute(
        self,
        session: OfflineSession,
        *,
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        updates: dict[str, object] = {}
        configured_budget = self._configured_usage_budget
        if session.attempts and configured_budget is not None and (
            session.usage_budget != configured_budget
        ):
            raise ValueError("a resumed session cannot silently change its persisted usage budget")
        if not session.attempts and configured_budget is not None and (
            session.usage_budget != configured_budget
        ):
            updates["usage_budget"] = configured_budget
        if session.artifact_authority != self.artifact_authority:
            updates["artifact_authority"] = self.artifact_authority
        if updates:
            session = _replace_session(
                session,
                **updates,
                checkpoint_sequence=session.checkpoint_sequence + 1,
            )
            write_checkpoint(session, output_dir)
        return await super()._execute(
            session,
            output_dir=output_dir,
            interrupt_after=interrupt_after,
        )

''',
)
replace_between(
    "src/imperium/offline/provider_engine.py",
    "    async def _call(\n",
    "    @staticmethod\n    def _template_for_round",
    '''    @staticmethod
    def _replace_attempt(session: OfflineSession, updated: ModelAttempt) -> OfflineSession:
        attempts = tuple(
            updated if item.attempt_id == updated.attempt_id else item
            for item in session.attempts
        )
        return _replace_session(session, attempts=attempts)

    @staticmethod
    def _attach_attempt_session(exc: Exception, session: OfflineSession) -> None:
        setattr(exc, "imperium_session", session)

    @staticmethod
    def _check_pre_call_budget(
        session: OfflineSession,
        *,
        serialized_provider_input: str,
    ) -> int:
        budget = session.usage_budget
        totals = usage_totals(session.attempts)
        if totals.attempts_launched >= budget.max_attempts:
            raise UsageBudgetExceeded(
                f"attempt budget exhausted: {totals.attempts_launched}/{budget.max_attempts}"
            )
        estimated = estimate_input_tokens(serialized_provider_input, budget)
        if totals.input_tokens + estimated > budget.max_input_tokens:
            raise UsageBudgetExceeded(
                "estimated input token budget would be exceeded before provider launch"
            )
        if (
            totals.output_tokens + budget.output_token_reserve_per_attempt
            > budget.max_output_tokens
        ):
            raise UsageBudgetExceeded(
                "reserved output token budget would be exceeded before provider launch"
            )
        return estimated

    @staticmethod
    def _check_reported_usage(session: OfflineSession, result) -> None:
        budget = session.usage_budget
        totals = usage_totals(session.attempts)
        if totals.input_tokens + result.input_tokens > budget.max_input_tokens:
            raise UsageBudgetExceeded("reported input token budget was exceeded")
        if (
            totals.cached_input_tokens + result.cached_input_tokens
            > budget.max_cached_input_tokens
        ):
            raise UsageBudgetExceeded("reported cached input token budget was exceeded")
        if totals.output_tokens + result.output_tokens > budget.max_output_tokens:
            raise UsageBudgetExceeded("reported output token budget was exceeded")

    async def _call(
        self,
        session: OfflineSession,
        *,
        expected: OutputT,
        resulting_stage: DeliberationStage,
        procedural_role: str,
        prompt_path: str,
        context: StageContext,
        apply: ApplyArtifact[OutputT],
        output_dir: str | Path,
        member_id: str | None = None,
        phase: ChallengePhase | None = None,
        round_number: int | None = None,
        subject: str | None = None,
        interrupt_after: str | None = None,
        validate: ValidateArtifact[OutputT] | None = None,
    ) -> tuple[OfflineSession, OutputT]:
        """Invoke one provider attempt through a durable fail-closed state transition."""

        key = _call_key(
            resulting_stage=resulting_stage,
            role=procedural_role,
            output_type=type(expected),
            member_id=member_id,
            phase=phase,
            round_number=round_number,
            subject=subject,
        )
        if key in set(session.completed_call_keys):
            return session, self._accepted_output(session, key, type(expected))
        prior_attempts = tuple(item for item in session.attempts if item.call_key == key)
        if prior_attempts:
            raise RetryAuthorizationRequired(
                f"call {key!r} already has an attempt; explicit abandon or retry authorization is required"
            )

        if context.member is not None:
            if context.member.member_id != member_id:
                raise ValueError("advocate context must contain only the active member profile")
            if any(
                reference.artifact_type == ArtifactKind.COUNCIL_SNAPSHOT.value
                for reference in context.visible_artifacts
            ):
                raise ValueError("advocate context cannot expose the complete council registry")

        input_text = context.model_dump_json()
        input_bytes = len(input_text.encode("utf-8"))
        if input_bytes > self.max_context_bytes:
            raise ProviderError(
                f"context for {key} is {input_bytes} bytes; "
                f"limit is {self.max_context_bytes} bytes"
            )

        provider = self._session_provider
        if provider is None:
            raise ProviderError("session provider was not prepared before model invocation")
        prompt = session.runtime.source(prompt_path)
        estimated_input_tokens = self._check_pre_call_budget(
            session,
            serialized_provider_input=f"{prompt.content}\n{input_text}",
        )
        attempt = ModelAttempt(
            attempt_id=f"{key}:attempt-1",
            call_key=key,
            attempt_number=1,
            status=AttemptStatus.PENDING,
            stage=session.record.stage,
            member_id=member_id,
            model=self.model,
            prompt_sha256=prompt.sha256,
            input_sha256=_context_hash(context),
            estimated_input_tokens=estimated_input_tokens,
        )
        pending = _replace_session(
            session,
            attempts=(*session.attempts, attempt),
            pending_call_key=key,
            checkpoint_sequence=session.checkpoint_sequence + 1,
        )
        write_checkpoint(pending, output_dir)

        result = None
        try:
            result = await provider.generate(
                model=self.model,
                instructions=prompt.content,
                input_text=input_text,
                output_type=type(expected),
                metadata=CallMetadata(
                    session_id=session.session_id,
                    call_key=key,
                    stage=session.record.stage,
                    member_id=member_id,
                ),
            )
            if result.retries != 0:
                raise ProviderError("providers must not perform automatic retries")
            if member_id is not None:
                authored_member_id = getattr(result.output, "member_id", None)
                if authored_member_id is not None and authored_member_id != member_id:
                    raise ProviderError(
                        f"provider output member {authored_member_id!r} does not match "
                        f"active member {member_id!r} for {key}"
                    )
            self._check_reported_usage(session, result)
            if validate is not None:
                validate(result.output)
            committed = apply(pending, result.output)
        except Exception as exc:
            terminal_status = (
                AttemptStatus.AMBIGUOUS
                if isinstance(exc, ProviderAmbiguousError)
                else AttemptStatus.FAILED
            )
            output = result.output if result is not None else None
            terminal = ModelAttempt.model_validate(
                attempt.model_copy(
                    update={
                        "status": terminal_status,
                        "provider": result.provider if result is not None else None,
                        "response_id": result.response_id if result is not None else None,
                        "output_sha256": artifact_digest(output) if output is not None else None,
                        "output_artifact_id": _artifact_id(output) if output is not None else None,
                        "input_tokens": result.input_tokens if result is not None else 0,
                        "cached_input_tokens": (
                            result.cached_input_tokens if result is not None else 0
                        ),
                        "output_tokens": result.output_tokens if result is not None else 0,
                        "latency_ms": result.latency_ms if result is not None else 0,
                        "error_type": type(exc).__name__,
                        "error_message": str(exc) or type(exc).__name__,
                    }
                ).model_dump(mode="python")
            )
            failed = self._replace_attempt(pending, terminal)
            failed = _replace_session(
                failed,
                pending_call_key=None,
                checkpoint_sequence=failed.checkpoint_sequence + 1,
            )
            write_checkpoint(failed, output_dir)
            self._attach_attempt_session(exc, failed)
            raise

        output_sha256 = artifact_digest(result.output)
        output_artifact_id = _artifact_id(result.output)
        accepted_attempt = ModelAttempt.model_validate(
            attempt.model_copy(
                update={
                    "status": AttemptStatus.ACCEPTED,
                    "provider": result.provider,
                    "response_id": result.response_id,
                    "output_sha256": output_sha256,
                    "output_artifact_id": output_artifact_id,
                    "input_tokens": result.input_tokens,
                    "cached_input_tokens": result.cached_input_tokens,
                    "output_tokens": result.output_tokens,
                    "latency_ms": result.latency_ms,
                }
            ).model_dump(mode="python")
        )
        committed = self._replace_attempt(committed, accepted_attempt)
        call_record = ModelCallRecord(
            call_id=key,
            provider=result.provider,
            model=result.model,
            stage=session.record.stage,
            member_id=member_id,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            retries=result.retries,
        )
        record = _update_record(
            committed.record,
            model_calls=_append_unique(
                committed.record.model_calls,
                call_record,
                identity=lambda item: item.call_id,
            ),
        )
        trace = TurnTrace(
            call_key=key,
            stage=session.record.stage,
            procedural_role=procedural_role,
            member_id=member_id,
            prompt_path=prompt.path,
            prompt_sha256=prompt.sha256,
            visible_artifact_ids=tuple(
                reference.artifact_id for reference in context.visible_artifacts
            ),
            profile_member_id=context.member.member_id if context.member else None,
            input_sha256=_context_hash(context),
            output_artifact_id=output_artifact_id,
            output_type=type(result.output).__name__,
            provider=result.provider,
            model=result.model,
        )
        committed = _replace_session(
            committed,
            record=record,
            turns=(*committed.turns, trace),
            completed_call_keys=(*committed.completed_call_keys, key),
            pending_call_key=None,
            checkpoint_sequence=committed.checkpoint_sequence + 1,
        )
        checkpoint = write_checkpoint(committed, output_dir)
        if interrupt_after == key:
            raise OfflineInterrupted(key, checkpoint)
        return committed, result.output

''',
)

# Codex tests and smoke expectations include cached usage.
replace_exact(
    "tests/test_codex_cli_provider.py",
    "from imperium.providers.base import CallMetadata, ModelResult, ProviderError\n",
    '''from imperium.providers.base import (
    CallMetadata,
    ModelResult,
    ProviderAmbiguousError,
    ProviderError,
)
''',
)
replace_exact(
    "tests/test_codex_cli_provider.py",
    '''                '{"type":"turn.completed","usage":{"input_tokens":321,"output_tokens":87}}\\n'
''',
    '''                '{"type":"turn.completed","usage":{"input_tokens":321,'
                '"cached_input_tokens":123,"output_tokens":87}}\\n'
''',
)
replace_exact(
    "tests/test_codex_cli_provider.py",
    '''    assert result.input_tokens == 321
    assert result.output_tokens == 87''',
    '''    assert result.input_tokens == 321
    assert result.cached_input_tokens == 123
    assert result.output_tokens == 87''',
)
replace_exact(
    "tests/test_codex_cli_provider.py",
    '''            input_tokens=321,
            output_tokens=87,''',
    '''            input_tokens=321,
            cached_input_tokens=123,
            output_tokens=87,''',
)
replace_exact(
    "tests/test_codex_cli_provider.py",
    '''    assert report.input_tokens == 321
    persisted = json.loads''',
    '''    assert report.input_tokens == 321
    assert report.cached_input_tokens == 123
    persisted = json.loads''',
)
replace_exact(
    "tests/test_codex_cli_provider.py",
    '''    assert persisted["reasoning_effort"] == DEFAULT_CODEX_REASONING_EFFORT
    assert persisted["output"]["member_id"] == "steward"''',
    '''    assert persisted["reasoning_effort"] == DEFAULT_CODEX_REASONING_EFFORT
    assert persisted["cached_input_tokens"] == 123
    assert persisted["output"]["member_id"] == "steward"''',
)
replace_exact(
    "tests/test_codex_cli_provider.py",
    '''@pytest.mark.asyncio
async def test_codex_provider_rejects_invalid_structured_output(''',
    '''@pytest.mark.asyncio
async def test_codex_provider_marks_missing_final_output_ambiguous(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = CodexCliProvider(timeout_seconds=30)
    monkeypatch.setattr(provider, "_resolve_executable", lambda: "/usr/bin/codex")

    async def fake_run(command: list[str], *, input_text: str) -> _ProcessResult:
        del command, input_text
        return _ProcessResult(returncode=0, stdout="{}\\n", stderr="")

    monkeypatch.setattr(provider, "_run_process", fake_run)
    with pytest.raises(ProviderAmbiguousError, match="accepted-output state is unknown"):
        await provider.generate(
            model=DEFAULT_CODEX_MODEL,
            instructions="Interpret.",
            input_text="{}",
            output_type=Interpretation,
            metadata=_metadata("smoke:ambiguous"),
        )


@pytest.mark.asyncio
async def test_codex_provider_rejects_invalid_structured_output(''',
)

# Durable status/index documentation.
replace_exact(
    "docs/README.md",
    '''- [`STAGE_5_GATE_2_PROVIDER_INJECTION.md`](STAGE_5_GATE_2_PROVIDER_INJECTION.md) — accepted Gate 2 contract: replay extraction, provider authority, bounded rounds, evidence disposition, shared-engine consolidation, and material second-round validation.
''',
    '''- [`STAGE_5_GATE_2_PROVIDER_INJECTION.md`](STAGE_5_GATE_2_PROVIDER_INJECTION.md) — accepted Gate 2 contract: replay extraction, provider authority, bounded rounds, evidence disposition, shared-engine consolidation, and material second-round validation.
- [`STAGE_5_GATE_2E_ATTEMPT_ACCOUNTING.md`](STAGE_5_GATE_2E_ATTEMPT_ACCOUNTING.md) — current Gate 2E contract: durable attempt states, usage budgets, output digests, and explicit retry prohibition.
''',
)
replace_exact(
    "docs/README.md",
    '''The current engineering gate is Gate 2E live-attempt accounting and cumulative usage controls. PR #13 completed provider-authority consolidation; a complete live council remains blocked.''',
    '''The current engineering gate is Gate 2E attempt accounting and cumulative usage controls under simulated providers. A complete live council remains blocked.''',
)
replace_exact(
    "docs/PROJECT_STATUS.md",
    '''- **Stage 5 Gate 2:** draft PR #13 resolves the shared-engine architecture gate under simulated providers; final review remains before merge.
''',
    '''- **Stage 5 Gate 2:** complete and merged through PR #13, squash commit `d816cc64cc88e28b7472e89bada680217704237f`.
- **Stage 5 Gate 2E:** attempt accounting and cumulative usage controls are in implementation under simulated providers.
''',
)
replace_exact(
    "docs/PROJECT_STATUS.md",
    '''- **Current gate:** review the consolidated Gate 2 implementation before Gate 2E live-failure accounting or any complete live council.''',
    '''- **Current gate:** prove durable attempt accounting and usage budgets before retry controls or any complete live council.''',
)
replace_exact(
    "docs/PROJECT_STATUS.md",
    '''The consolidated implementation passes **146 Python tests** and the Stage 4 artifact workflow. CI and local validation made no live model calls.''',
    '''The merged Gate 2 implementation passed **146 Python tests** and the Stage 4 artifact workflow. CI and local validation made no live model calls.''',
)
