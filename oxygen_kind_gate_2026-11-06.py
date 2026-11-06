#!/usr/bin/env python3
"""Gates for this session.

oxygen_kind_gate: refuse to treat three oxygen sentences as one phenomenon.
interval_admissibility: refuse a binomial interval when the denominator
is not a set of binary trials.

Neither function mints a class, a particle, or a metabolism.
"""

from __future__ import annotations

from typing import Any


KINDS = {
    "abyssal_chamber_o2": {
        "kind": "local dissolved-oxygen time series inside a benthic chamber",
        "time": "hours to days, present day",
        "status": "disputed",
        "supports": "nothing global until H2, a sufficient in-situ voltage, and a nodule-absent control are reported",
    },
    "paleozoic_tl_redox": {
        "kind": "basin-scale redox proxy over geological time",
        "time": "10^8 years, Paleozoic",
        "status": "a 2026 secondary report of a Science Advances dataset; paper not opened here",
        "supports": "a later date for stable deep-ocean oxygen than the old 540 Ma switch, with a sampling gap of roughly one rock per 450,000 years",
    },
    "surface_photosynthesis": {
        "kind": "oxygenic photosynthesis",
        "time": "continuous where there is light",
        "status": "established for sunlit water",
        "supports": "not a mechanism for a dark chamber and not a date for the abyss",
    },
    "hadal_seep_chemosynthesis": {
        "kind": "microbial use of methane and sulfide, animals eating that production",
        "time": "present, hadal seeps",
        "status": "reported at the Kuril-Kamchatka trench (Peng et al., Nature 2025) and said to recur in a southern Pacific trench",
        "supports": "animals without sunlight. Not oxygen production. Not a global coverage fraction.",
    },
}


def oxygen_kind_gate(sentence_a: str, sentence_b: str, source_already_separates: bool) -> dict[str, Any]:
    """Return a verdict. Do not mint.

    KIND_COLLAPSE only if both sentences are in the table, they differ in kind,
    and the source being judged does not already separate them.
    """
    if sentence_a not in KINDS or sentence_b not in KINDS:
        return {"verdict": "NO_SENTENCE", "mint": False}
    if sentence_a == sentence_b:
        return {"verdict": "SAME_KIND", "mint": False}
    if source_already_separates:
        return {"verdict": "SOURCE_ALREADY_SEPARATES", "mint": False}
    if KINDS[sentence_a]["kind"] == KINDS[sentence_b]["kind"]:
        return {"verdict": "SAME_KIND", "mint": False}
    return {
        "verdict": "KIND_COLLAPSE",
        "mint": False,
        "a": sentence_a,
        "b": sentence_b,
        "a_kind": KINDS[sentence_a]["kind"],
        "b_kind": KINDS[sentence_b]["kind"],
        "rule": "Do not use one sentence as evidence for the other.",
    }


def interval_admissibility(numerator: float, denominator: float, denominator_is_binary_trials: bool) -> dict[str, Any]:
    """Wilson intervals are for binary trials. Species totals and map percents are not.

    Returns the interval only when the denominator is that kind of sample.
    """
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    if numerator < 0 or numerator > denominator:
        raise ValueError("numerator outside [0, denominator]")
    if not denominator_is_binary_trials:
        return {
            "interval": None,
            "reason": "Refused. This denominator is not a set of binary trials. A Wilson interval would fake a sampling error.",
        }
    z = 1.96
    n = denominator
    phat = numerator / n
    den = 1 + z * z / n
    center = (phat + z * z / (2 * n)) / den
    margin = z * ((phat * (1 - phat) + z * z / (4 * n)) / n) ** 0.5 / den
    lo, hi = max(0.0, center - margin), min(1.0, center + margin)
    return {"interval": [lo, hi], "point": phat, "reason": "Admitted. Binary cohort."}


def withdraw_cross_kind_ranking(rows: list[dict[str, str]]) -> dict[str, Any]:
    """The first script sorted unlike quantities by residue. That ranking is withdrawn."""
    kinds = {row["kind"] for row in rows}
    if len(kinds) > 1:
        return {
            "ranking": None,
            "reason": "Withdrawn. Unlike kinds do not form an order. Report each fraction inside its own kind only.",
            "kinds_present": sorted(kinds),
        }
    return {"ranking": rows, "reason": "Single kind. An order is allowed."}


CASES = [
    ("abyssal_chamber_o2", "paleozoic_tl_redox", False, "using the Paleozoic proxy to vouch for nodule electrolysis"),
    ("abyssal_chamber_o2", "hadal_seep_chemosynthesis", False, "calling seep animals evidence that nodules make oxygen"),
    ("abyssal_chamber_o2", "surface_photosynthesis", False, "treating darkness as a minor variant of the photosynthetic oxygen story"),
    ("hadal_seep_chemosynthesis", "surface_photosynthesis", True, "Peng et al. already separate seep chemistry from sunlight"),
    ("paleozoic_tl_redox", "paleozoic_tl_redox", False, "same sentence repeated"),
]


def main() -> None:
    import json

    verdicts = []
    for a, b, separates, label in CASES:
        verdict = oxygen_kind_gate(a, b, separates)
        verdict["label"] = label
        verdicts.append(verdict)

    intervals = {
        "bodien_unresponsive_60_of_241": interval_admissibility(60, 241, True),
        "bodien_responsive_43_of_112": interval_admissibility(43, 112, True),
        "mora_species_fraction": interval_admissibility(1.2e6, 8.7e6, False),
        "seabed_2030_percent": interval_admissibility(28.7, 100, False),
    }
    ranking = withdraw_cross_kind_ranking([
        {"name": "borehole radial reach", "kind": "length ratio"},
        {"name": "stellar mass-energy share", "kind": "cosmic inventory"},
        {"name": "eukaryote catalogue fraction", "kind": "species tally"},
        {"name": "bathymetric coverage", "kind": "map coverage"},
        {"name": "command-following cohort", "kind": "binary clinical cohort"},
    ])
    print(json.dumps({
        "mint": False,
        "oxygen_kind_gate": verdicts,
        "interval_admissibility": intervals,
        "cross_kind_ranking": ranking,
    }, indent=2))


if __name__ == "__main__":
    main()
