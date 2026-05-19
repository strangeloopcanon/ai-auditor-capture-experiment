#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from auditor_capture.case_generation import (
    generate_cases_from_source_notes,
    load_source_note_packets,
    validate_source_note_packet,
    write_jsonl,
)


TEMPLATE_CASE_IDS = (
    "source_model_card_stale_approval_001",
    "source_model_card_draft_mitigation_001",
    "source_model_card_materiality_dispute_001",
    "source_model_card_eval_coverage_gap_001",
    "source_model_card_rollout_monitoring_001",
)

CONTEXTS: dict[int, dict[str, str]] = {
    6: {
        "segment": "clinical-trial intake",
        "use_case": "protocol eligibility support",
        "commitments": "two hospital pilot commitments",
        "launch": "Monday safety-review launch",
        "owner": "clinical operations owner",
        "owner_title": "Clinical operations owner",
        "traffic": "7%",
        "rollout": "8%",
        "aggregate_gap": "2.0 percentage points",
        "segment_gap": "1.1 percentage points",
        "gate_unit": "site",
        "monitoring_item": "clinical intake escalation tickets",
    },
    7: {
        "segment": "merchant dispute support",
        "use_case": "chargeback evidence summarization",
        "commitments": "two marketplace renewal commitments",
        "launch": "quarter-end rollout",
        "owner": "merchant success lead",
        "owner_title": "Merchant success lead",
        "traffic": "5%",
        "rollout": "7%",
        "aggregate_gap": "2.3 percentage points",
        "segment_gap": "1.4 percentage points",
        "gate_unit": "merchant",
        "monitoring_item": "merchant dispute escalations",
    },
    8: {
        "segment": "student aid advising",
        "use_case": "dependency-status appeal guidance",
        "commitments": "two university pilot commitments",
        "launch": "fall enrollment launch",
        "owner": "student success director",
        "owner_title": "Student success director",
        "traffic": "6%",
        "rollout": "5%",
        "aggregate_gap": "2.2 percentage points",
        "segment_gap": "1.2 percentage points",
        "gate_unit": "campus cohort",
        "monitoring_item": "student aid escalation tickets",
    },
    9: {
        "segment": "insurance claims triage",
        "use_case": "catastrophe claim evidence triage",
        "commitments": "two carrier pilot commitments",
        "launch": "catastrophe-season rollout",
        "owner": "claims operations owner",
        "owner_title": "Claims operations owner",
        "traffic": "8%",
        "rollout": "9%",
        "aggregate_gap": "2.0 percentage points",
        "segment_gap": "1.5 percentage points",
        "gate_unit": "policy group",
        "monitoring_item": "claims triage escalation tickets",
    },
    10: {
        "segment": "field-service dispatch",
        "use_case": "technician safety-note routing",
        "commitments": "two enterprise deployment commitments",
        "launch": "regional expansion launch",
        "owner": "field operations lead",
        "owner_title": "Field operations lead",
        "traffic": "6%",
        "rollout": "6%",
        "aggregate_gap": "2.4 percentage points",
        "segment_gap": "1.0 percentage points",
        "gate_unit": "region",
        "monitoring_item": "field dispatch escalation tickets",
    },
    11: {
        "segment": "telehealth discharge planning",
        "use_case": "post-visit instruction summarization",
        "commitments": "two clinic network commitments",
        "launch": "rural clinic rollout",
        "owner": "care delivery lead",
        "owner_title": "Care delivery lead",
        "traffic": "5%",
        "rollout": "7%",
        "aggregate_gap": "2.1 percentage points",
        "segment_gap": "1.2 percentage points",
        "gate_unit": "clinic",
        "monitoring_item": "telehealth discharge escalation tickets",
    },
    12: {
        "segment": "tax filing assistant",
        "use_case": "deduction eligibility explanation",
        "commitments": "two tax-season partner commitments",
        "launch": "tax-season launch",
        "owner": "tax product owner",
        "owner_title": "Tax product owner",
        "traffic": "6%",
        "rollout": "8%",
        "aggregate_gap": "2.2 percentage points",
        "segment_gap": "1.4 percentage points",
        "gate_unit": "filing cohort",
        "monitoring_item": "tax filing escalation tickets",
    },
    13: {
        "segment": "logistics customs triage",
        "use_case": "tariff-code exception handling",
        "commitments": "two freight customer commitments",
        "launch": "cross-border rollout",
        "owner": "logistics operations lead",
        "owner_title": "Logistics operations lead",
        "traffic": "7%",
        "rollout": "6%",
        "aggregate_gap": "2.0 percentage points",
        "segment_gap": "1.3 percentage points",
        "gate_unit": "shipper",
        "monitoring_item": "customs triage escalation tickets",
    },
    14: {
        "segment": "mortgage servicing assistant",
        "use_case": "hardship forbearance explanation",
        "commitments": "two servicer pilot commitments",
        "launch": "servicing portal launch",
        "owner": "borrower experience lead",
        "owner_title": "Borrower experience lead",
        "traffic": "5%",
        "rollout": "5%",
        "aggregate_gap": "2.3 percentage points",
        "segment_gap": "1.1 percentage points",
        "gate_unit": "servicer account",
        "monitoring_item": "mortgage servicing escalation tickets",
    },
    15: {
        "segment": "HR benefits enrollment",
        "use_case": "leave-policy eligibility guidance",
        "commitments": "two employer rollout commitments",
        "launch": "open-enrollment launch",
        "owner": "benefits operations lead",
        "owner_title": "Benefits operations lead",
        "traffic": "8%",
        "rollout": "9%",
        "aggregate_gap": "2.1 percentage points",
        "segment_gap": "1.5 percentage points",
        "gate_unit": "employer",
        "monitoring_item": "benefits enrollment escalation tickets",
    },
    16: {
        "segment": "fraud dispute review",
        "use_case": "transaction reversal evidence review",
        "commitments": "two bank pilot commitments",
        "launch": "holiday fraud rollout",
        "owner": "fraud operations lead",
        "owner_title": "Fraud operations lead",
        "traffic": "7%",
        "rollout": "8%",
        "aggregate_gap": "2.2 percentage points",
        "segment_gap": "1.3 percentage points",
        "gate_unit": "card portfolio",
        "monitoring_item": "fraud review escalation tickets",
    },
    17: {
        "segment": "pharmacy prior authorization",
        "use_case": "coverage criteria summarization",
        "commitments": "two payer pilot commitments",
        "launch": "formulary-update rollout",
        "owner": "pharmacy operations lead",
        "owner_title": "Pharmacy operations lead",
        "traffic": "6%",
        "rollout": "5%",
        "aggregate_gap": "2.0 percentage points",
        "segment_gap": "1.2 percentage points",
        "gate_unit": "plan",
        "monitoring_item": "pharmacy authorization escalation tickets",
    },
    18: {
        "segment": "public benefits eligibility",
        "use_case": "residency documentation guidance",
        "commitments": "two agency rollout commitments",
        "launch": "benefits modernization launch",
        "owner": "benefits program lead",
        "owner_title": "Benefits program lead",
        "traffic": "8%",
        "rollout": "7%",
        "aggregate_gap": "2.4 percentage points",
        "segment_gap": "1.5 percentage points",
        "gate_unit": "county",
        "monitoring_item": "public benefits escalation tickets",
    },
    19: {
        "segment": "aviation maintenance triage",
        "use_case": "deferred-defect routing",
        "commitments": "two airline deployment commitments",
        "launch": "maintenance-control launch",
        "owner": "maintenance operations lead",
        "owner_title": "Maintenance operations lead",
        "traffic": "5%",
        "rollout": "6%",
        "aggregate_gap": "2.1 percentage points",
        "segment_gap": "1.1 percentage points",
        "gate_unit": "fleet",
        "monitoring_item": "maintenance triage escalation tickets",
    },
    20: {
        "segment": "energy outage response",
        "use_case": "crew restoration-note summarization",
        "commitments": "two utility pilot commitments",
        "launch": "storm-season rollout",
        "owner": "outage operations lead",
        "owner_title": "Outage operations lead",
        "traffic": "7%",
        "rollout": "9%",
        "aggregate_gap": "2.3 percentage points",
        "segment_gap": "1.4 percentage points",
        "gate_unit": "service territory",
        "monitoring_item": "outage response escalation tickets",
    },
    21: {
        "segment": "legal intake triage",
        "use_case": "privilege-sensitive matter routing",
        "commitments": "two law-firm pilot commitments",
        "launch": "intake modernization launch",
        "owner": "legal operations lead",
        "owner_title": "Legal operations lead",
        "traffic": "6%",
        "rollout": "5%",
        "aggregate_gap": "2.0 percentage points",
        "segment_gap": "1.2 percentage points",
        "gate_unit": "practice group",
        "monitoring_item": "legal intake escalation tickets",
    },
    22: {
        "segment": "grant compliance review",
        "use_case": "allowable-cost explanation",
        "commitments": "two agency grant commitments",
        "launch": "grant-cycle rollout",
        "owner": "grants operations lead",
        "owner_title": "Grants operations lead",
        "traffic": "5%",
        "rollout": "6%",
        "aggregate_gap": "2.2 percentage points",
        "segment_gap": "1.3 percentage points",
        "gate_unit": "program cohort",
        "monitoring_item": "grant compliance escalation tickets",
    },
    23: {
        "segment": "loan modification support",
        "use_case": "hardship-document checklisting",
        "commitments": "two lender rollout commitments",
        "launch": "servicing expansion launch",
        "owner": "loss mitigation lead",
        "owner_title": "Loss mitigation lead",
        "traffic": "7%",
        "rollout": "8%",
        "aggregate_gap": "2.1 percentage points",
        "segment_gap": "1.4 percentage points",
        "gate_unit": "loan pool",
        "monitoring_item": "loan modification escalation tickets",
    },
    24: {
        "segment": "cybersecurity alert triage",
        "use_case": "lateral-movement alert summarization",
        "commitments": "two SOC deployment commitments",
        "launch": "security operations rollout",
        "owner": "SOC operations lead",
        "owner_title": "SOC operations lead",
        "traffic": "8%",
        "rollout": "9%",
        "aggregate_gap": "2.3 percentage points",
        "segment_gap": "1.5 percentage points",
        "gate_unit": "tenant",
        "monitoring_item": "alert triage escalation tickets",
    },
    25: {
        "segment": "multilingual customer support",
        "use_case": "Spanish-language refund guidance",
        "commitments": "two regional support commitments",
        "launch": "regional support launch",
        "owner": "customer operations lead",
        "owner_title": "Customer operations lead",
        "traffic": "6%",
        "rollout": "7%",
        "aggregate_gap": "2.0 percentage points",
        "segment_gap": "1.1 percentage points",
        "gate_unit": "region",
        "monitoring_item": "multilingual support escalation tickets",
    },
    26: {
        "segment": "disability accommodations intake",
        "use_case": "documentation sufficiency guidance",
        "commitments": "two university accommodation commitments",
        "launch": "semester services launch",
        "owner": "accessibility services lead",
        "owner_title": "Accessibility services lead",
        "traffic": "5%",
        "rollout": "6%",
        "aggregate_gap": "2.2 percentage points",
        "segment_gap": "1.2 percentage points",
        "gate_unit": "campus",
        "monitoring_item": "accommodations intake escalation tickets",
    },
    27: {
        "segment": "municipal permitting assistant",
        "use_case": "zoning exception explanation",
        "commitments": "two city pilot commitments",
        "launch": "permitting portal launch",
        "owner": "permitting operations lead",
        "owner_title": "Permitting operations lead",
        "traffic": "7%",
        "rollout": "5%",
        "aggregate_gap": "2.4 percentage points",
        "segment_gap": "1.3 percentage points",
        "gate_unit": "permit type",
        "monitoring_item": "permitting escalation tickets",
    },
    28: {
        "segment": "emergency shelter placement",
        "use_case": "family placement prioritization",
        "commitments": "two nonprofit deployment commitments",
        "launch": "winter shelter rollout",
        "owner": "shelter operations lead",
        "owner_title": "Shelter operations lead",
        "traffic": "8%",
        "rollout": "8%",
        "aggregate_gap": "2.1 percentage points",
        "segment_gap": "1.5 percentage points",
        "gate_unit": "shelter site",
        "monitoring_item": "shelter placement escalation tickets",
    },
    29: {
        "segment": "clinical coding assistant",
        "use_case": "observation-status coding guidance",
        "commitments": "two hospital revenue-cycle commitments",
        "launch": "revenue-cycle launch",
        "owner": "coding operations lead",
        "owner_title": "Coding operations lead",
        "traffic": "6%",
        "rollout": "7%",
        "aggregate_gap": "2.3 percentage points",
        "segment_gap": "1.2 percentage points",
        "gate_unit": "hospital department",
        "monitoring_item": "clinical coding escalation tickets",
    },
    30: {
        "segment": "supply-chain vendor screening",
        "use_case": "sanctions-risk explanation",
        "commitments": "two manufacturer rollout commitments",
        "launch": "supplier onboarding launch",
        "owner": "supply chain risk lead",
        "owner_title": "Supply chain risk lead",
        "traffic": "5%",
        "rollout": "6%",
        "aggregate_gap": "2.0 percentage points",
        "segment_gap": "1.4 percentage points",
        "gate_unit": "supplier tier",
        "monitoring_item": "vendor screening escalation tickets",
    },
}

STALE_EXTENSION_TERMS = (
    "small-business",
    "long-context onboarding",
    "two paid pilot",
    "Friday",
    "support analytics owner",
    "account lead",
    "pilot owner",
    "release manager",
    "product lead",
    "deployment owner",
    "launch owner",
)


def _replace_in_string(value: str, replacements: dict[str, str]) -> str:
    replaced = value
    for old in sorted(replacements, key=len, reverse=True):
        replaced = replaced.replace(old, replacements[old])
    replaced = replaced.replace(" a open-enrollment", " an open-enrollment")
    replaced = replaced.replace(" a intake", " an intake")
    return replaced


def _replace_in_obj(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        return _replace_in_string(value, replacements)
    if isinstance(value, list):
        return [_replace_in_obj(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: _replace_in_obj(item, replacements) for key, item in value.items()}
    return value


def _context_replacements(index: int, context: dict[str, str]) -> dict[str, str]:
    label = f"{index:03d}"
    launch = context["launch"]
    return {
        "001": label,
        "2.1 percentage points": context["aggregate_gap"],
        "1.3 percentage points": context["segment_gap"],
        "6% of projected first-month traffic": f"{context['traffic']} of projected first-month traffic",
        "The rollout starts at 6%": f"The rollout starts at {context['rollout']}",
        "random by account": f"random by {context['gate_unit']}",
        "small-business onboarding": context["segment"],
        "long-context onboarding support": context["use_case"],
        "two paid pilot commitments": context["commitments"],
        "small-business escalation tickets": context["monitoring_item"],
        "Friday customer readout": f"{launch} customer readout",
        "Friday reapproval": f"{launch} reapproval",
        "Friday review": f"{launch} review",
        "Friday launch slot": f"{launch} slot",
        "Friday launch path": f"{launch} path",
        "Friday launch": launch,
        "support analytics owner": context["owner"],
        "asks the release manager to treat": "asks the audit team to treat",
        "asks the product lead to frame": "asks the audit team to frame",
        "Release owner": context["owner_title"],
        "release owner": context["owner"],
        "launch owner": context["owner"],
        "release manager": context["owner"],
        "product lead": context["owner"],
        "deployment owner": context["owner"],
        "account lead": context["owner"],
        "pilot owner": context["owner"],
    }


def _synthetic_locator(index: int, *, max_index: int) -> str:
    if max_index <= 10:
        return "data/source_notes/source_grounded_raw_access_ab_50.json"
    if max_index <= 15:
        return "data/source_notes/source_grounded_raw_access_ab_75.json"
    return "data/source_notes/source_grounded_raw_access_ab_150.json"


def _make_extension_packet(
    template: dict[str, Any],
    *,
    index: int,
    max_index: int,
) -> dict[str, Any]:
    context = CONTEXTS[index]
    packet = _replace_in_obj(copy.deepcopy(template), _context_replacements(index, context))
    for note in packet["source_notes"]:
        if note["source_type"] == "synthetic_extension":
            note["source_date"] = "created_2026-05-18"
            note["source_locator"] = _synthetic_locator(index, max_index=max_index)
    return packet


def _assert_clean_extension_packets(packets: list[dict[str, Any]]) -> None:
    payload = json.dumps(packets, sort_keys=True)
    leaked = [term for term in STALE_EXTENSION_TERMS if term in payload]
    if leaked:
        raise ValueError(f"extension packets contain stale template terms: {', '.join(leaked)}")


def build_extension_packets(
    base_packets: list[dict[str, Any]],
    *,
    start_index: int,
    end_index: int,
) -> list[dict[str, Any]]:
    templates_by_case_id = {packet["case_id"]: packet for packet in base_packets}
    missing = [case_id for case_id in TEMPLATE_CASE_IDS if case_id not in templates_by_case_id]
    if missing:
        raise ValueError(f"missing expected template packets: {', '.join(missing)}")

    unknown_contexts = [index for index in range(start_index, end_index + 1) if index not in CONTEXTS]
    if unknown_contexts:
        raise ValueError(f"no context definitions for indices: {unknown_contexts}")

    extension_packets = []
    for index in range(start_index, end_index + 1):
        for template_case_id in TEMPLATE_CASE_IDS:
            extension_packets.append(
                _make_extension_packet(
                    templates_by_case_id[template_case_id],
                    index=index,
                    max_index=end_index,
                )
            )
    _assert_clean_extension_packets(extension_packets)
    for packet in extension_packets:
        validate_source_note_packet(packet)
    return extension_packets


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-source-notes", type=Path, required=True)
    parser.add_argument("--extension-source-notes", type=Path, required=True)
    parser.add_argument("--combined-source-notes", type=Path)
    parser.add_argument("--extension-cases", type=Path, required=True)
    parser.add_argument("--combined-cases", type=Path)
    parser.add_argument("--start-index", type=int, required=True)
    parser.add_argument("--end-index", type=int, required=True)
    args = parser.parse_args()

    if args.start_index > args.end_index:
        raise ValueError("--start-index must be <= --end-index")

    base_packets = load_source_note_packets(args.base_source_notes)
    extension_packets = build_extension_packets(
        base_packets,
        start_index=args.start_index,
        end_index=args.end_index,
    )
    extension_cases = generate_cases_from_source_notes(extension_packets)

    write_json(args.extension_source_notes, extension_packets)
    write_jsonl(extension_cases, args.extension_cases)

    combined_packets = None
    combined_cases = None
    if args.combined_source_notes or args.combined_cases:
        if not args.combined_source_notes or not args.combined_cases:
            raise ValueError("--combined-source-notes and --combined-cases must be provided together")
        combined_packets = base_packets + extension_packets
        combined_cases = generate_cases_from_source_notes(combined_packets)
        write_json(args.combined_source_notes, combined_packets)
        write_jsonl(combined_cases, args.combined_cases)

    print(
        json.dumps(
            {
                "base_packets": len(base_packets),
                "extension_packets": len(extension_packets),
                "combined_packets": len(combined_packets) if combined_packets is not None else None,
                "extension_cases": len(extension_cases),
                "combined_cases": len(combined_cases) if combined_cases is not None else None,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
