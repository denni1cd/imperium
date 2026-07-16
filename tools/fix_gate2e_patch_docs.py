from pathlib import Path

path = Path(__file__).with_name("apply_gate2e_attempt_slice.py")
text = path.read_text(encoding="utf-8")
replacements = {
    "- [`STAGE_5_GATE_2_PROVIDER_INJECTION.md`](STAGE_5_GATE_2_PROVIDER_INJECTION.md) — accepted Gate 2 contract: replay extraction, provider authority, bounded rounds, evidence disposition, shared-engine consolidation, and material second-round validation.":
    "- [`STAGE_5_GATE_2_PROVIDER_INJECTION.md`](STAGE_5_GATE_2_PROVIDER_INJECTION.md) — current Gate 2 contract and architecture review: replay extraction, provider authority, bounded rounds, evidence disposition, shared-engine consolidation, and remaining live-safety controls.",
    "The current engineering gate is Gate 2E live-attempt accounting and cumulative usage controls. PR #13 completed provider-authority consolidation; a complete live council remains blocked.":
    "The current engineering gate is merge review of the completed Gate 2 shared-engine consolidation. Gate 2E live-failure accounting and every complete live council remain blocked.",
}
for old, new in replacements.items():
    if old not in text:
        raise RuntimeError(f"expected stale patch text not found: {old[:80]!r}")
    text = text.replace(old, new, 1)
path.write_text(text, encoding="utf-8")
