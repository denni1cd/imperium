from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_exact(relative: str, old: str, new: str) -> None:
    path = ROOT / relative
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"expected integrity-review block not found in {relative}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_exact(
    "src/imperium/offline/provider_engine.py",
    '''    UsageBudgetExceeded,
    artifact_digest,
    estimate_input_tokens,
    usage_totals,
)''',
    '''    UsageBudgetExceeded,
    artifact_digest,
    charged_input_tokens,
    charged_output_tokens,
    estimate_input_tokens,
    usage_totals,
)''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    '''        totals = usage_totals(session.attempts)
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
''',
    '''        totals = usage_totals(session.attempts)
        if totals.attempts_launched >= budget.max_attempts:
            raise UsageBudgetExceeded(
                f"attempt budget exhausted: {totals.attempts_launched}/{budget.max_attempts}"
            )
        estimated = estimate_input_tokens(serialized_provider_input, budget)
        if charged_input_tokens(session.attempts) + estimated > budget.max_input_tokens:
            raise UsageBudgetExceeded(
                "estimated input token budget would be exceeded before provider launch"
            )
        if (
            charged_output_tokens(session.attempts, budget)
            + budget.output_token_reserve_per_attempt
            > budget.max_output_tokens
        ):
            raise UsageBudgetExceeded(
                "reserved output token budget would be exceeded before provider launch"
            )
        return estimated

    @staticmethod
    def _check_reported_usage(
        session: OfflineSession,
        result,
        *,
        estimated_input_tokens: int,
    ) -> None:
        budget = session.usage_budget
        totals = usage_totals(session.attempts)
        charged_input = max(result.input_tokens, estimated_input_tokens)
        if charged_input_tokens(session.attempts) + charged_input > budget.max_input_tokens:
            raise UsageBudgetExceeded("reported input token budget was exceeded")
        if (
            totals.cached_input_tokens + result.cached_input_tokens
            > budget.max_cached_input_tokens
        ):
            raise UsageBudgetExceeded("reported cached input token budget was exceeded")
        charged_output = max(
            result.output_tokens,
            budget.output_token_reserve_per_attempt,
        )
        if (
            charged_output_tokens(session.attempts, budget) + charged_output
            > budget.max_output_tokens
        ):
            raise UsageBudgetExceeded("reported output token budget was exceeded")
''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    "            self._check_reported_usage(session, result)\n",
    '''            self._check_reported_usage(
                session,
                result,
                estimated_input_tokens=estimated_input_tokens,
            )
''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    '''        if prior_attempts:
            raise RetryAuthorizationRequired(
                f"call {key!r} already has an attempt; explicit abandon or retry authorization is required"
            )
''',
    '''        if prior_attempts:
            exc = RetryAuthorizationRequired(
                f"call {key!r} already has an attempt; explicit abandon or retry authorization is required"
            )
            self._attach_attempt_session(exc, session)
            raise exc
''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    '''            if context.member.member_id != member_id:
                raise ValueError("advocate context must contain only the active member profile")
''',
    '''            if context.member.member_id != member_id:
                exc = ValueError("advocate context must contain only the active member profile")
                self._attach_attempt_session(exc, session)
                raise exc
''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    '''            ):
                raise ValueError("advocate context cannot expose the complete council registry")

        input_text = context.model_dump_json()
''',
    '''            ):
                exc = ValueError("advocate context cannot expose the complete council registry")
                self._attach_attempt_session(exc, session)
                raise exc

        input_text = context.model_dump_json()
''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    '''        if input_bytes > self.max_context_bytes:
            raise ProviderError(
                f"context for {key} is {input_bytes} bytes; "
                f"limit is {self.max_context_bytes} bytes"
            )
''',
    '''        if input_bytes > self.max_context_bytes:
            exc = ProviderError(
                f"context for {key} is {input_bytes} bytes; "
                f"limit is {self.max_context_bytes} bytes"
            )
            self._attach_attempt_session(exc, session)
            raise exc
''',
)
replace_exact(
    "src/imperium/offline/provider_engine.py",
    '''        if provider is None:
            raise ProviderError("session provider was not prepared before model invocation")
''',
    '''        if provider is None:
            exc = ProviderError("session provider was not prepared before model invocation")
            self._attach_attempt_session(exc, session)
            raise exc
''',
)

replace_exact(
    "src/imperium/offline/models.py",
    '''        for call_key, attempts in attempts_by_call.items():
            numbers = sorted(item.attempt_number for item in attempts)
            if numbers != list(range(1, len(numbers) + 1)):
                raise ValueError(f"attempt numbers for {call_key!r} must be contiguous from one")

        pending = [item for item in self.attempts if item.status is AttemptStatus.PENDING]
''',
    '''        for call_key, attempts in attempts_by_call.items():
            numbers = sorted(item.attempt_number for item in attempts)
            if numbers != list(range(1, len(numbers) + 1)):
                raise ValueError(f"attempt numbers for {call_key!r} must be contiguous from one")
            for attempt in attempts:
                if attempt.attempt_number == 1 and attempt.retry_of_attempt_id is not None:
                    raise ValueError("the first attempt cannot identify retry lineage")
                if attempt.attempt_number > 1 and attempt.retry_of_attempt_id is None:
                    raise ValueError("attempts after the first require retry lineage")

        pending = [item for item in self.attempts if item.status is AttemptStatus.PENDING]
''',
)
replace_exact(
    "src/imperium/offline/models.py",
    '''            turn = turns.get(call_key)
            if turn is None or turn.output_artifact_id != attempt.output_artifact_id:
                raise ValueError("accepted attempt output identity must match its turn trace")
            artifact = artifacts.get(attempt.output_artifact_id or "")
''',
    '''            turn = turns.get(call_key)
            if turn is None or turn.output_artifact_id != attempt.output_artifact_id:
                raise ValueError("accepted attempt output identity must match its turn trace")
            if (
                turn.prompt_sha256 != attempt.prompt_sha256
                or turn.input_sha256 != attempt.input_sha256
            ):
                raise ValueError("accepted attempt input and prompt digests must match its turn trace")
            if (
                turn.stage is not attempt.stage
                or turn.member_id != attempt.member_id
                or turn.provider != attempt.provider
                or turn.model != attempt.model
            ):
                raise ValueError("accepted attempt execution identity must match its turn trace")
            artifact = artifacts.get(attempt.output_artifact_id or "")
''',
)
