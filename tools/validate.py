"""Offline structural validation, never approval or organizational execution."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from datetime import datetime

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = (
    "decisions/records/",
    "amendments/records/",
    "governance/approvals/",
    "governance/authority_snapshots/",
    "audit/events/",
    "history/",
    "constitution/",
    "architecture/decisions/",
)
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"}
MANIFEST = "integrity/manifest.json"
IMMUTABLE_PROPOSAL = (
    "amendment_id", "change_type", "original_principle", "proposed_principle",
    "proposed_by", "reason", "evidence", "expected_impact", "document_sha256", "revisits",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def local_path(root, reference):
    """Repository references use portable URI-style separators on every OS."""
    relative = PurePosixPath(reference)
    require(
        bool(reference) and not relative.is_absolute()
        and "\\" not in reference and ":" not in reference
        and ".." not in relative.parts,
        f"Not a repository-relative path: {reference}",
    )
    path = root.joinpath(*relative.parts).resolve()
    require(path.is_relative_to(root.resolve()), f"Path escapes repository: {reference}")
    require(path.is_file(), f"Missing referenced file: {reference}")
    return path


def read(root, reference):
    return json.loads(local_path(root, reference).read_text(encoding="utf-8"))


def check_schema(root, reference, value):
    require({"date-time", "uri"} <= FormatChecker.checkers.keys(),
            "Required timestamp/URI format checker missing; install requirements-dev.txt")
    schema = read(root, reference)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)


def references(root, values):
    for value in values:
        if value.startswith("https://"):
            require(len(value) > len("https://"), "Empty external evidence URL")
        else:
            local_path(root, value)


def records(root, directory, schema, id_key="id"):
    result = {}
    for path in sorted((root / directory).glob("*.json")):
        reference = path.relative_to(root).as_posix()
        value = read(root, reference)
        check_schema(root, schema, value)
        if id_key:
            require(path.stem == value[id_key], f"Record ID/filename mismatch: {reference}")
        result[reference] = value
    return result


def validate_approvals(root):
    approvals = records(root, "governance/approvals", "governance/approval_schema.json")
    for reference, approval in approvals.items():
        require(approval["authority_ref"] == "governance/authority_matrix.yaml",
                f"Unrecognized authority baseline: {reference}")
        authority = read(root, approval["authority_ref"])
        require(authority["status"] == "ACTIVE", "Draft authority cannot validate new approvals")
        humans = authority["authorized_humans"]
        matches = [h for h in humans if h["id"] == approval["reviewer"]["id"]]
        require(len(matches) == 1, f"Human is not uniquely enrolled: {reference}")
        human = matches[0]
        require(human["actor_type"] == "human", "Approval authority must be human")
        reviewed = timestamp(approval["reviewed_at"])
        require(timestamp(human["valid_from"]) <= reviewed, "Approval predates enrollment")
        require(human["valid_until"] is None or reviewed < timestamp(human["valid_until"]),
                "Approval follows expired mandate")
        scope = "amendments" if approval["target"].startswith("amendments/records/") else "documents"
        require(scope in human["scopes"], "Human approval exceeds enrolled scope")
        references(root, human["enrollment_evidence"])
        require(bool(human["enrollment_evidence"]), "Missing human enrollment evidence")
        require(digest(local_path(root, approval["target"])) == approval["target_sha256"],
                f"Approval target digest mismatch: {reference}")
        references(root, approval["evidence"])
    return approvals


def validate_decisions(root, approvals):
    decisions = records(root, "decisions/records", "decisions/schema.json")
    for reference, decision in decisions.items():
        references(root, decision["evidence"])
        previous = decision["supersedes"]
        if previous is not None:
            require(previous in decisions and previous != reference, "Invalid prior decision")
            require(decisions[previous]["date"] <= decision["date"], "Decision predates predecessor")
            seen = {reference}
            ancestor = previous
            while ancestor is not None:
                require(ancestor not in seen, "Cyclic decision history")
                require(ancestor in decisions, "Missing prior decision")
                seen.add(ancestor)
                ancestor = decisions[ancestor]["supersedes"]
        if decision["record_type"] == "human_instruction":
            require(reference == "decisions/records/DEC-0001.json",
                    "Only the founding instruction has bootstrap authority")
        if decision["record_type"] in {"human_approved", "authorized_actor_decision"}:
            approval = approvals.get(decision["authorization"]["approval_ref"])
            require(approval is not None and approval["decision"] == "approve",
                    "Decision needs explicit human approval evidence")
            require(previous is not None and approval["target"] == previous,
                    "Decision approval must bind the prior proposal")
            require(decisions[previous]["record_type"] == "ai_recommendation",
                    "Decision must identify its recorded recommendation")
            require(timestamp(approval["reviewed_at"]).date().isoformat() <= decision["date"],
                    "Decision predates approval")
            require(
                decision["statement"] == decisions[previous]["statement"],
                "Approved decision statement differs from reviewed proposal",
            )
            require(decision["record_type"] != "authorized_actor_decision",
                    "Other-actor mandates are deferred; record and validate mandate policy first")
    return decisions


def validate_principle(root, principle):
    check_schema(root, "principles/schema.json", principle)
    document = principle["document"]
    expected = f"history/principle_evolution/{principle['id']}-v{principle['version']}.md"
    require(document == expected, "Principle document ID/version mismatch")
    local_path(root, document)
    require(read(root, str(PurePosixPath(document).with_suffix(".json"))) == principle,
            "Principle metadata differs from historical version")
    local_path(root, principle["source"])


def validate_amendments(root, approvals):
    snapshots = records(root, "amendments/records", "amendments/schema.json", id_key=None)
    groups = {}
    for reference, snapshot in snapshots.items():
        expected = f"{snapshot['amendment_id']}-R{snapshot['record_number']:03}.json"
        require(PurePosixPath(reference).name == expected, "Amendment filename mismatch")
        groups.setdefault(snapshot["amendment_id"], []).append((reference, snapshot))
        validate_principle(root, snapshot["proposed_principle"])
        if snapshot["original_principle"] is not None:
            validate_principle(root, snapshot["original_principle"])
        require(
            digest(local_path(root, snapshot["proposed_principle"]["document"]))
            == snapshot["document_sha256"],
            "Proposed principle document digest mismatch",
        )
        references(root, snapshot["evidence"])

    activated = []
    pending = []
    transitions = {
        "proposed": {"in_review"},
        "in_review": {"approved", "rejected"},
        "approved": {"activated"},
        "rejected": set(),
        "activated": set(),
    }
    for amendment_id, group in groups.items():
        group.sort(key=lambda pair: pair[1]["record_number"])
        first_ref, first = group[0]
        require(first["status"] == "proposed" and first["previous_record"] is None,
                "Amendment must start as a proposal")
        if first["revisits"] is not None:
            rejected = snapshots.get(first["revisits"])
            require(rejected is not None and rejected["status"] == "rejected",
                    "Revisit must reference a retained rejection")
            require(rejected["amendment_id"] != amendment_id, "Revisit needs a new amendment ID")
            require(timestamp(rejected["recorded_at"]) < timestamp(first["recorded_at"]),
                    "Revisit must follow rejection")
            require(first["reason"] != rejected["reason"] or first["evidence"] != rejected["evidence"],
                    "Revisit must record new evidence or circumstances")
        for index, (reference, snapshot) in enumerate(group):
            require(snapshot["record_number"] == index + 1, "Missing or duplicate amendment snapshot")
            require(all(snapshot[key] == first[key] for key in IMMUTABLE_PROPOSAL),
                    "Proposal content changed during review; create a new amendment")
            if index:
                previous_ref, previous = group[index - 1]
                require(snapshot["previous_record"] == previous_ref, "Broken amendment predecessor")
                require(snapshot["status"] in transitions[previous["status"]],
                        "Invalid amendment transition")
                require(timestamp(previous["recorded_at"]) < timestamp(snapshot["recorded_at"]),
                        "Lifecycle timestamps must increase")
            if snapshot["human_review"] is not None:
                approval = approvals.get(snapshot["human_review"])
                require(approval is not None, "Missing human review record")
                require(approval["target"] == first_ref, "Review must bind exact initial proposal")
                expected_decision = "reject" if snapshot["status"] == "rejected" else "approve"
                require(approval["decision"] == expected_decision, "Review decision mismatch")
                require(timestamp(group[1][1]["recorded_at"]) <= timestamp(approval["reviewed_at"])
                        <= timestamp(snapshot["recorded_at"]), "Review outside human review phase")
            if snapshot["status"] == "activated":
                previous = group[index - 1][1]
                require(snapshot["human_review"] == previous["human_review"],
                        "Activation must retain the recorded approval")
                require(timestamp(snapshot["effective_at"]) == timestamp(snapshot["recorded_at"]),
                        "Activation must record actual implementation time")
                activated.append(snapshot)
        if group[-1][1]["status"] in {"proposed", "in_review", "approved"}:
            pending.append(amendment_id)
    return activated, sorted(pending)


def validate_registry(root, activated):
    bootstrap = read(root, "history/principle_evolution/G-001-v1.0.0.json")
    validate_principle(root, bootstrap)
    current = {bootstrap["id"]: bootstrap}
    for amendment in sorted(activated, key=lambda a: (timestamp(a["effective_at"]), a["amendment_id"])):
        proposed = amendment["proposed_principle"]
        original = amendment["original_principle"]
        principle_id = proposed["id"]
        if amendment["change_type"] == "addition":
            require(principle_id not in current, "Principle ID cannot be reused")
            require(proposed["status"] == "active", "New principle must activate")
        else:
            require(current.get(principle_id) == original, "Amendment original is not current")
            require(original["status"] == "active", "Retired principle IDs cannot be reactivated")
            require(proposed["created"] == original["created"], "Creation date must remain stable")
            old_version = tuple(map(int, original["version"].split(".")))
            new_version = tuple(map(int, proposed["version"].split(".")))
            require(new_version > old_version, "Principle revision must increment version")
            expected_status = "retired" if amendment["change_type"] == "retirement" else "active"
            require(proposed["status"] == expected_status, "Amendment change/status mismatch")
        current[principle_id] = proposed
    registry = read(root, "principles/registry.json")
    require(set(registry) == {"principles"}, "Unexpected principle registry fields")
    indexed = {}
    for principle in registry["principles"]:
        validate_principle(root, principle)
        require(principle["id"] not in indexed, "Duplicate principle ID")
        indexed[principle["id"]] = principle
    require(indexed == current, "Registry differs from bootstrap plus authorized activations")
    for principle in indexed.values():
        require(set(principle["related_principles"]) <= set(indexed), "Unknown related principle")
    return sorted(f"{p['id']}@{p['version']}" for p in indexed.values() if p["status"] == "active")


def validate_audit(root):
    events = records(root, "audit/events", "audit/schema.json")
    require(bool(events), "Missing foundation audit")
    previous_ref = None
    previous = None
    ordered = sorted(events.items(), key=lambda pair: int(pair[1]["id"].split("-")[1]))
    for reference, event in ordered:
        require(event["previous_event"] == previous_ref, "Broken audit predecessor")
        if previous_ref is not None:
            require(event["previous_sha256"] == digest(local_path(root, previous_ref)),
                    "Audit predecessor digest mismatch")
            require(timestamp(previous["recorded_at"]) < timestamp(event["recorded_at"]),
                    "Audit timestamps must increase")
        references(root, event["references"])
        previous_ref, previous = reference, event


def manifest_files(root):
    return {
        path.relative_to(root).as_posix(): digest(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not (set(path.relative_to(root).parts) & EXCLUDED_PARTS)
        and path.relative_to(root).as_posix() != MANIFEST
        and path.suffix not in {".pyc", ".pyo"}
    }


def write_manifest(root):
    destination = root / MANIFEST
    destination.parent.mkdir(exist_ok=True)
    value = {"algorithm": "sha256", "files": manifest_files(root)}
    destination.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")


def validate_manifest(root):
    manifest = read(root, MANIFEST)
    require(manifest["algorithm"] == "sha256", "Unsupported integrity algorithm")
    require(manifest["files"] == manifest_files(root),
            "Integrity manifest mismatch: review changes; do not auto-bless a failed check")


def validate_history(root, base):
    if not base or set(base) == {"0"}:
        roots = subprocess.check_output(
            ["git", "rev-list", "--max-parents=0", "HEAD"], cwd=root, text=True
        ).splitlines()
        require(len(roots) == 1, "History baseline requires one explicit root")
        base = roots[0]
    require(re.fullmatch(r"[a-fA-F0-9]{7,40}", base) is not None, "Invalid history base SHA")
    changes = subprocess.check_output(
        ["git", "--no-pager", "diff", "--name-status", "--no-renames", base, "--", *HISTORICAL],
        cwd=root, text=True,
    )
    for line in changes.splitlines():
        status, name = line.split("\t", 1)
        require(status == "A", f"Historical rewrite forbidden: {status} {name}")


def validate_markdown_links(root):
    for path in root.rglob("*.md"):
        if set(path.relative_to(root).parts) & EXCLUDED_PARTS:
            continue
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            if target.startswith(("https://", "#")):
                continue
            resolved = (path.parent / target.split("#", 1)[0]).resolve()
            require(resolved.is_relative_to(root.resolve()) and resolved.is_file(),
                    f"Broken local Markdown link in {path.relative_to(root)}: {target}")


def validate_runtime_specs(root, state):
    for kind in ("agent", "node", "task", "leadership_lease"):
        reference = f"schemas/{kind}.schema.json"
        schema = read(root, reference)
        require(bool(schema.get("examples")), f"Missing synthetic schema example: {reference}")
        for example in schema["examples"]:
            check_schema(root, reference, example)
    nodes = read(root, "governance/node_permissions.yaml")
    runtime = read(root, "governance/runtime_permissions.yaml")
    for policy in (nodes, runtime):
        require(policy["status"] == "PROPOSED" and policy["default"] == "deny",
                "Runtime permission specifications are not deployed policy grants")
        require(policy["runtime_enabled"] is False, "Runtime execution is not enabled")
        require(policy["confirmed_constraint"] == "G-001", "Runtime must preserve G-001")
    require(not nodes["registered_nodes"] and not runtime["current_grants"],
            "Specification-only update cannot register nodes or grant runtime permissions")
    require(nodes["direct_authoritative_writes"] is False
            and nodes["governance_approval"] is False
            and nodes["personal_credential_access"] is False,
            "Execution nodes cannot gain direct authority or personal credentials")
    require(runtime["maximum_logical_ceos"] == runtime["maximum_active_controllers"] == 1
            and runtime["logical_ceo_agent_id"] == "amo-ceo",
            "AMO must retain one logical CEO and at most one active controller")
    require(runtime["leadership_fencing_required"] is True
            and runtime["task_fencing_required"] is True
            and runtime["runtime_governance_self_approval"] is False
            and runtime["autonomous_financial_transactions"] is False
            and runtime["credential_inheritance_between_nodes"] is False,
            "Runtime specification cannot bypass fencing, approval or credential boundaries")
    architecture = state["architecture"]
    reference = architecture["path"]
    require(architecture["decision_id"] == "ADR-0001"
            and architecture["status"] == "CONFIRMED_BY_FOUNDER"
            and architecture["logical_ceo_agent_id"] == runtime["logical_ceo_agent_id"],
            "State summary must preserve founder-confirmed Architecture A")
    require(nodes["architecture_ref"] == runtime["architecture_ref"] == reference,
            "Runtime policies disagree about the authoritative ADR")
    text = local_path(root, reference).read_text(encoding="utf-8")
    require("Status: CONFIRMED_BY_FOUNDER" in text
            and f"Accepted: {architecture['accepted_on']}" in text,
            "ADR status/date differs from state summary")


def validate(root, *, check_manifest=True):
    # Every JSON schema and data file must at least parse, including unused schemas.
    for path in root.rglob("*.json"):
        if set(path.relative_to(root).parts) & EXCLUDED_PARTS:
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        if "$schema" in value:
            Draft202012Validator.check_schema(value)
    for name in ("authority_matrix", "approval_policy", "agent_permissions"):
        read(root, f"governance/{name}.yaml")
    approvals = validate_approvals(root)
    validate_decisions(root, approvals)
    activated, pending = validate_amendments(root, approvals)
    active = validate_registry(root, activated)
    validate_audit(root)
    state = read(root, "operations/state.json")
    require(state["organization"] == "amo", "Wrong organizational identity")
    require(state["active_principles"] == active, "Stale active principle state summary")
    require(state["pending_amendments"] == pending, "Stale pending amendment state summary")
    require(state["runtime_enabled"] is False, "This foundation does not enable a runtime")
    require(read(root, "governance/agent_permissions.yaml")["runtime_enabled"] is False,
            "This foundation does not grant runtime permissions")
    validate_runtime_specs(root, state)
    validate_markdown_links(root)
    if check_manifest:
        validate_manifest(root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true",
                        help="Generate consistency hashes, NOT approval; review all changes")
    parser.add_argument("--history-base", help="Reject historical rewrites since this Git commit")
    args = parser.parse_args()
    try:
        validate(ROOT, check_manifest=not args.write_manifest)
        if args.history_base is not None:
            validate_history(ROOT, args.history_base)
        if args.write_manifest:
            write_manifest(ROOT)
            validate_manifest(ROOT)
            print("Manifest generated. Human review and independent anchoring are still required.")
        print("PASS: foundation structure and consistency (not human authentication).")
    except (ValueError, KeyError, TypeError, OSError, ValidationError, subprocess.CalledProcessError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
