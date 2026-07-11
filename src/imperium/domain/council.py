"""Validated profiles and fixed-council configuration for Imperium Stage 2."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import field_validator, model_validator

from imperium.domain.enums import CouncilRole
from imperium.domain.models import MemberProfile, NonEmptyStr, StrictModel, ValueVector
from imperium.domain.vocabulary import ValueVocabulary


class CouncilMemberProfile(MemberProfile):
    """Approved, versioned strategic profile for one council office."""

    profile_version: NonEmptyStr
    status: Literal["approved"]
    role: CouncilRole
    participates_in_advocacy: bool
    operating_constraints: tuple[NonEmptyStr, ...]

    @field_validator("doctrine")
    @classmethod
    def require_substantive_doctrine(cls, doctrine: tuple[str, ...]) -> tuple[str, ...]:
        if len(doctrine) < 2:
            raise ValueError("an approved member profile requires at least two doctrine statements")
        return doctrine

    @field_validator(
        "jurisdiction",
        "vigilance",
        "accepted_sacrifices",
        "evidence_requirements",
        "revision_triggers",
        "operating_constraints",
    )
    @classmethod
    def require_profile_section(cls, entries: tuple[str, ...]) -> tuple[str, ...]:
        if not entries:
            raise ValueError("approved member profile sections cannot be empty")
        return entries

    @field_validator("presentation")
    @classmethod
    def restrict_presentation_metadata(cls, presentation: dict[str, str]) -> dict[str, str]:
        allowed = {"label", "tone"}
        unexpected = set(presentation) - allowed
        if unexpected:
            raise ValueError(
                "presentation metadata may contain only label and tone; "
                f"unexpected keys: {sorted(unexpected)}"
            )
        return presentation

    @model_validator(mode="after")
    def enforce_role_boundary(self) -> Self:
        if self.role is CouncilRole.ADVOCATE and not self.participates_in_advocacy:
            raise ValueError("advocate profiles must participate in independent advocacy")
        if self.role is CouncilRole.SENESCHAL and self.participates_in_advocacy:
            raise ValueError("the Seneschal must not participate as an independent advocate")
        return self

    @property
    def presentation_label(self) -> str | None:
        """Return the optional thematic label, which never defines strategic behavior."""

        return self.presentation.get("label")

    @property
    def dominant_value(self) -> str:
        """Return the highest-weighted strategic value for inspection and testing."""

        return max(self.values.weights, key=self.values.weights.__getitem__)


class MemberDifferentiation(StrictModel):
    """Inspectable claim explaining why one profile earns a council seat."""

    member_id: NonEmptyStr
    distinctive_question: NonEmptyStr
    expected_contribution: NonEmptyStr
    likely_failure_mode: NonEmptyStr
    counterweight_member_ids: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def prevent_self_counterweight(self) -> Self:
        if self.member_id in self.counterweight_member_ids:
            raise ValueError("a member cannot list itself as a strategic counterweight")
        if len(set(self.counterweight_member_ids)) != len(self.counterweight_member_ids):
            raise ValueError("counterweight member identifiers must be unique")
        return self


class CouncilConfiguration(StrictModel):
    """Approved fixed roster used for the first controlled experiments."""

    version: NonEmptyStr
    status: Literal["approved"]
    vocabulary_version: NonEmptyStr
    fixed_for_initial_experiments: Literal[True]
    seneschal_member_id: NonEmptyStr
    advocate_member_ids: tuple[NonEmptyStr, ...]
    members: tuple[CouncilMemberProfile, ...]
    differentiation: tuple[MemberDifferentiation, ...]
    known_coverage_risks: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_roster_structure(self) -> Self:
        if not self.members:
            raise ValueError("a council configuration must include member profiles")
        if len(self.advocate_member_ids) < 2:
            raise ValueError("the initial council requires at least two independent advocates")
        if len(set(self.advocate_member_ids)) != len(self.advocate_member_ids):
            raise ValueError("advocate member identifiers must be unique")

        member_ids = [profile.member_id for profile in self.members]
        if len(set(member_ids)) != len(member_ids):
            raise ValueError("council member identifiers must be unique")

        titles = [profile.title.casefold() for profile in self.members]
        if len(set(titles)) != len(titles):
            raise ValueError("council member titles must be unique")

        labels = [
            profile.presentation_label.casefold()
            for profile in self.members
            if profile.presentation_label is not None
        ]
        if len(set(labels)) != len(labels):
            raise ValueError("thematic presentation labels must be unique")

        seneschals = [profile for profile in self.members if profile.role is CouncilRole.SENESCHAL]
        if len(seneschals) != 1:
            raise ValueError("the fixed council must contain exactly one Seneschal")
        if seneschals[0].member_id != self.seneschal_member_id:
            raise ValueError("seneschal_member_id must identify the configured Seneschal")

        configured_advocates = {
            profile.member_id for profile in self.members if profile.role is CouncilRole.ADVOCATE
        }
        declared_advocates = set(self.advocate_member_ids)
        if configured_advocates != declared_advocates:
            missing = configured_advocates - declared_advocates
            unexpected = declared_advocates - configured_advocates
            raise ValueError(
                "advocate_member_ids must exactly match advocate profiles; "
                f"missing: {sorted(missing)}; unexpected: {sorted(unexpected)}"
            )
        if self.seneschal_member_id in declared_advocates:
            raise ValueError("the Seneschal cannot also be declared as an advocate")

        vector_fingerprints: dict[tuple[tuple[str, str], ...], str] = {}
        for profile in self.members:
            fingerprint = tuple(
                sorted((name, str(weight)) for name, weight in profile.values.weights.items())
            )
            duplicate = vector_fingerprints.get(fingerprint)
            if duplicate is not None:
                raise ValueError(
                    f"member profiles {duplicate!r} and {profile.member_id!r} "
                    "must not use identical value vectors"
                )
            vector_fingerprints[fingerprint] = profile.member_id

        differentiation_ids = [entry.member_id for entry in self.differentiation]
        if len(set(differentiation_ids)) != len(differentiation_ids):
            raise ValueError("member differentiation entries must be unique")
        if set(differentiation_ids) != set(member_ids):
            raise ValueError("every configured member requires exactly one differentiation entry")

        valid_ids = set(member_ids)
        differentiation_by_id = {entry.member_id: entry for entry in self.differentiation}
        for member_id, entry in differentiation_by_id.items():
            unknown = set(entry.counterweight_member_ids) - valid_ids
            if unknown:
                raise ValueError(
                    f"member {member_id!r} references unknown counterweights: {sorted(unknown)}"
                )
            if member_id in declared_advocates and not entry.counterweight_member_ids:
                raise ValueError(
                    f"advocate member {member_id!r} requires at least one strategic counterweight"
                )

        return self

    def validate_against_vocabulary(self, vocabulary: ValueVocabulary) -> Self:
        """Validate every profile against the exact approved vocabulary version."""

        if self.vocabulary_version != vocabulary.version:
            raise ValueError(
                "council vocabulary version does not match loaded vocabulary; "
                f"council={self.vocabulary_version!r}, vocabulary={vocabulary.version!r}"
            )
        for profile in self.members:
            vocabulary.validate_vector(profile.values)
        return self

    @property
    def seneschal(self) -> CouncilMemberProfile:
        """Return the sole procedural coordinator."""

        return next(profile for profile in self.members if profile.member_id == self.seneschal_member_id)

    @property
    def advocates(self) -> tuple[CouncilMemberProfile, ...]:
        """Return independent advocates in the explicitly configured order."""

        profiles = {profile.member_id: profile for profile in self.members}
        return tuple(profiles[member_id] for member_id in self.advocate_member_ids)

    @property
    def value_vectors(self) -> dict[str, ValueVector]:
        """Return an inspectable member-to-vector mapping."""

        return {profile.member_id: profile.values for profile in self.members}
