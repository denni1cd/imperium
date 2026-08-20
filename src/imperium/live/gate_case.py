"""Frozen strategic question for the first complete live council gate."""

from __future__ import annotations

from imperium.domain.models import SovereignRequest
from imperium.offline.fixtures import build_challenged_scenario
from imperium.offline.models import OfflineScenario

LIVE_COUNCIL_SCENARIO_ID = "stage5-gate-2f-live-council"


def build_live_council_scenario() -> OfflineScenario:
    """Return the pre-registered Gate 2F case and schema exemplars.

    The provider-bound engine treats all fixture reasoning artifacts as schema and
    routing exemplars only.  Live provider outputs remain authoritative.
    """

    exemplar = build_challenged_scenario()
    request = SovereignRequest(
        request_id="request-stage5-live-council-platform-decision",
        original_text=(
            "Decide whether a 20-person data engineering group should spend the next "
            "six months building an internal AI coding and orchestration platform, adopt "
            "commercial tools, run a bounded hybrid pilot, or defer the investment. "
            "Produce one council judgment and an actionable plan."
        ),
        goals=(
            "Reduce median delivery lead time by at least 20 percent within six months.",
            "Protect confidential source code and data.",
            "Create reusable capability only where the expected leverage justifies it.",
            "Avoid an operational burden the group cannot sustain.",
        ),
        hard_constraints=(
            "First-year incremental cash spend may not exceed 120,000 USD.",
            "Ongoing platform and maintenance burden may not exceed 1.5 FTE.",
            "Every production change requires human review.",
            "No autonomous production deployment is permitted.",
            "Treat this as a decision under the supplied facts, not a request to "
            "implement software.",
        ),
        prohibitions=(
            "Do not inspect repositories, run commands, browse the web, or invent external facts.",
            "Do not silently redefine the six-month outcome or the stated resource limits.",
            "Do not mistake agreement, summaries, or dialogue volume for consequential debate.",
            "Do not claim that one council run proves the Imperium hypothesis.",
        ),
        supplied_facts=(
            "The group has 20 engineers in four squads; current median delivery lead "
            "time is 18 days.",
            "A six-engineer commercial coding-assistant pilot reported about 15 percent "
            "faster implementation, but did not measure end-to-end delivery lead time.",
            "Security will approve only products that contractually do not retain prompts, "
            "source code, or submitted data.",
            "The internal-platform estimate is three engineers for four months plus about "
            "one FTE of ongoing maintenance.",
            "Internal platform work would displace committed roadmap work.",
            "Adoption is uneven: roughly half of the engineers are reluctant to change "
            "their current workflow.",
            "Unknowns should be exposed as assumptions or decision triggers; conditional "
            "planning is permitted.",
        ),
        context={
            "experiment_condition": "C — full Imperium deliberation",
            "research_access": "disabled",
            "test_case_status": "frozen before live results",
        },
    )
    return OfflineScenario.model_validate(
        exemplar.model_copy(
            update={
                "scenario_id": LIVE_COUNCIL_SCENARIO_ID,
                "description": (
                    "First complete provider-authoritative council deliberation on a frozen "
                    "technology investment decision."
                ),
                "request": request,
            }
        ).model_dump(mode="python")
    )
