"""Validated contracts for the shared strategic value vocabulary."""

from __future__ import annotations

from typing import Literal, Self

from pydantic import field_validator, model_validator

from imperium.domain.models import NonEmptyStr, StrictModel, ValueVector


class StrategicValueDefinition(StrictModel):
    """One approved strategic priority shared by every council member."""

    value_id: NonEmptyStr
    name: NonEmptyStr
    definition: NonEmptyStr
    high_weight_behavior: tuple[NonEmptyStr, ...]
    low_weight_behavior: tuple[NonEmptyStr, ...]
    tensions: tuple[NonEmptyStr, ...] = ()
    prohibited_interpretations: tuple[NonEmptyStr, ...]

    @field_validator(
        "high_weight_behavior",
        "low_weight_behavior",
        "prohibited_interpretations",
    )
    @classmethod
    def require_multiple_examples(cls, entries: tuple[str, ...]) -> tuple[str, ...]:
        if len(entries) < 2:
            raise ValueError("strategic values require at least two entries in each behavior rule")
        return entries

    @model_validator(mode="after")
    def reject_self_tension(self) -> Self:
        if self.value_id in self.tensions:
            raise ValueError(f"strategic value {self.value_id!r} cannot be in tension with itself")
        if len(set(self.tensions)) != len(self.tensions):
            raise ValueError(f"strategic value {self.value_id!r} contains duplicate tensions")
        return self


class ValueDistinction(StrictModel):
    """A realistic scenario that distinguishes two neighboring strategic values."""

    value_a: NonEmptyStr
    value_b: NonEmptyStr
    scenario: NonEmptyStr
    difference: NonEmptyStr

    @model_validator(mode="after")
    def require_distinct_values(self) -> Self:
        if self.value_a == self.value_b:
            raise ValueError("a value distinction must compare two different values")
        return self

    @property
    def pair(self) -> frozenset[str]:
        """Return an order-independent identity for duplicate detection."""

        return frozenset((self.value_a, self.value_b))


class ValueVocabulary(StrictModel):
    """The approved, versioned strategic value vocabulary."""

    version: NonEmptyStr
    status: Literal["approved"]
    values: tuple[StrategicValueDefinition, ...]
    distinctions: tuple[ValueDistinction, ...]

    @model_validator(mode="after")
    def validate_vocabulary(self) -> Self:
        if not self.values:
            raise ValueError("the strategic value vocabulary cannot be empty")

        value_ids = [definition.value_id for definition in self.values]
        value_names = [definition.name.casefold() for definition in self.values]
        if len(set(value_ids)) != len(value_ids):
            raise ValueError("strategic value identifiers must be unique")
        if len(set(value_names)) != len(value_names):
            raise ValueError("strategic value names must be unique")

        approved = set(value_ids)
        tensions_by_value = {
            definition.value_id: set(definition.tensions) for definition in self.values
        }
        for value_id, tensions in tensions_by_value.items():
            unknown = tensions - approved
            if unknown:
                raise ValueError(
                    f"strategic value {value_id!r} references unknown tensions: {sorted(unknown)}"
                )
            asymmetric = {
                tension
                for tension in tensions
                if value_id not in tensions_by_value.get(tension, set())
            }
            if asymmetric:
                raise ValueError(
                    f"strategic value {value_id!r} has non-reciprocal tensions: "
                    f"{sorted(asymmetric)}"
                )

        seen_pairs: set[frozenset[str]] = set()
        covered_values: set[str] = set()
        for distinction in self.distinctions:
            referenced = {distinction.value_a, distinction.value_b}
            unknown = referenced - approved
            if unknown:
                raise ValueError(
                    f"value distinction references unknown values: {sorted(unknown)}"
                )
            if distinction.pair in seen_pairs:
                raise ValueError(
                    "value distinctions must not repeat the same pair in reverse or duplicate form"
                )
            seen_pairs.add(distinction.pair)
            covered_values.update(referenced)

        uncovered = approved - covered_values
        if uncovered:
            raise ValueError(
                "every approved strategic value requires a differentiation scenario; "
                f"missing: {sorted(uncovered)}"
            )

        return self

    @property
    def value_ids(self) -> tuple[str, ...]:
        """Return approved identifiers in their configured presentation order."""

        return tuple(definition.value_id for definition in self.values)

    def validate_vector(self, vector: ValueVector) -> ValueVector:
        """Require a normalized vector to use every approved value exactly once."""

        expected = set(self.value_ids)
        actual = set(vector.weights)
        missing = expected - actual
        unexpected = actual - expected
        if missing or unexpected:
            details: list[str] = []
            if missing:
                details.append(f"missing values: {sorted(missing)}")
            if unexpected:
                details.append(f"unexpected values: {sorted(unexpected)}")
            raise ValueError("value vector does not match the approved vocabulary; " + "; ".join(details))
        return vector
