# VEI Mapping

The experiment should use VEI as the institutional substrate rather than as a generic message log. This kit currently exports VEI-compatible transcript records; the next integration step is to write them into a VEI workspace as canonical events and provenance artifacts.

## Conceptual Mapping

```text
Case file
  -> VEI scenario / seeded workspace state

Admissible evidence
  -> visible documents, tickets, logs, receipts, and event-spine slices

Inadmissible/private/hindsight evidence
  -> hidden events, private channel records, post-t events, or regulator-only state

Treatment
  -> policy profile + router visibility rules

Actor output
  -> governed agent action + public audit packet

Auditor initial report
  -> private auditor workpaper event

Actor response
  -> public or private response event depending on treatment

Auditor final report
  -> final audit decision event

Regulator score
  -> deterministic contract result over event state and hidden labels
```

## Required VEI Surfaces

- `WorldSession` as the deterministic world kernel.
- Canonical event spine for all evidence and message-routing events.
- Provenance export for per-case transcripts.
- Policy profiles for evidence-access and communication topology.
- Approval queue / governance state for access-exception tasks.
- Snapshots and replay for repeatable case execution.
- Contract-style predicates for core scoring.

## Event Fields This Kit Already Emits

Each live or dry-run call record includes:

- `run_id`
- `case_id`
- `treatment_id`
- `stage`
- `model`
- `channel`
- `visible_context_hash`
- `prompt_hash`
- `output_path`
- `schema_path`

Each transcript should be mapped into VEI as an append-only sequence of events with the same `case_id`, `treatment_id`, and stage tags.
