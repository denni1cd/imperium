"""Smallest falsifiable Stage 5 live-provider workflow."""

from __future__ import annotations

from pathlib import Path

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import Interpretation, SovereignRequest
from imperium.engine.context import ContextBuilder
from imperium.live.models import CodexSmokeReport
from imperium.offline.runtime import freeze_runtime
from imperium.providers.base import CallMetadata, ProviderError
from imperium.providers.codex_cli import DEFAULT_CODEX_MODEL, CodexCliProvider


async def run_codex_smoke(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    model: str = DEFAULT_CODEX_MODEL,
    executable: str = "codex",
    timeout_seconds: float = 300.0,
) -> CodexSmokeReport:
    """Run one Terra-low Accountant interpretation and persist a safe report."""

    root = Path(project_root).resolve()
    destination = Path(output_dir).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    runtime = freeze_runtime(root)
    if runtime.protocol.version != "1.3":
        raise ValueError(
            f"Stage 5 smoke requires protocol 1.3; loaded {runtime.protocol.version!r}"
        )
    member = next(
        advocate for advocate in runtime.council.advocates if advocate.member_id == "steward"
    )
    request = SovereignRequest(
        request_id="stage5-codex-smoke-request",
        original_text=(
            "Decide whether a team should run one narrowly scoped live model test before "
            "investing in a larger evaluation harness."
        ),
        goals=(
            "Identify the central decision and a bounded next step.",
            "Preserve the distinction between process validation and strategic proof.",
        ),
        hard_constraints=(
            "Do not recommend a broad platform build.",
            "Do not assume that one successful call proves the council hypothesis.",
        ),
        prohibitions=(
            "Do not use external facts, repository context, tools, or hidden prior conversation.",
        ),
        supplied_facts=(
            "The offline protocol already completes successfully with deterministic replay.",
            "The current question is only whether to attempt one isolated live call.",
        ),
    )
    context = ContextBuilder.independent_interpretation(request, member)
    contract = runtime.protocol.contract_for(DeliberationStage.INTERPRETATIONS_COMPLETE)
    if not contract.prompt_template:
        raise ValueError("independent interpretation requires a prompt template")
    prompt = runtime.source(contract.prompt_template)
    call_key = "stage5-smoke:interpretation:steward"
    session_id = "stage5-codex-smoke"
    provider = CodexCliProvider(
        executable=executable,
        timeout_seconds=timeout_seconds,
        event_log_dir=destination / "events",
    )
    result = await provider.generate(
        model=model,
        instructions=prompt.content,
        input_text=context.model_dump_json(),
        output_type=Interpretation,
        metadata=CallMetadata(
            session_id=session_id,
            call_key=call_key,
            stage=DeliberationStage.COUNCIL_SELECTED,
            member_id=member.member_id,
        ),
    )
    if result.output.member_id != member.member_id:
        raise ProviderError(
            "Codex smoke output changed the active member identity; "
            f"expected {member.member_id!r}, received {result.output.member_id!r}"
        )
    report = CodexSmokeReport(
        session_id=session_id,
        call_key=call_key,
        member_id=member.member_id,
        provider=result.provider,
        model=result.model,
        response_id=result.response_id,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        latency_ms=result.latency_ms,
        retries=result.retries,
        output=result.output,
    )
    temporary = destination / "smoke-report.json.tmp"
    final = destination / "smoke-report.json"
    temporary.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    temporary.replace(final)
    return report
