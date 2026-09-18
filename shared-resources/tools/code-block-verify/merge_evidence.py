#!/usr/bin/env python3
"""Merge standard verify.py evidence into a current manifest without trusting block IDs.

Usage:
  python merge_evidence.py --manifest manifest.jsonl --run RUN_DIR [--run RUN_DIR ...] --output OUTPUT_DIR

Each run directory must contain manifest.jsonl and results.jsonl.  A result can
only be reused when (file, lang, sha256(manifest content)) matches the current
manifest.  Later --run values win for an identical content key.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


def content_hash(record: dict[str, Any]) -> str:
    """Hash exact UTF-8 manifest content; never trust a supplied source hash."""
    return hashlib.sha256(record.get("content", "").encode("utf-8")).hexdigest()


def key(record: dict[str, Any]) -> tuple[str, str, str]:
    return (record.get("file", ""), record.get("lang", ""), content_hash(record))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def classification(result: dict[str, Any] | None) -> str:
    if result is None:
        return "NOT_VERIFIED"
    # legacy_hash_exception remains visible metadata. It must not mask a FAIL,
    # but it also must not discard an actual successful L1/L2 check.
    l1 = result.get("l1", {}).get("status", "NOT_VERIFIED")
    l2 = result.get("l2", {}).get("status", "NOT_VERIFIED")
    if {l1, l2} & {"FAIL", "ERROR_TOOL", "TIMEOUT", "MISS"}:
        return "NEEDS_REVIEW"
    if l1 == "PASS":
        return "PASS_CHECKED_SCOPE"
    return "NOT_VERIFIED"


def merge(current: list[dict[str, Any]], run_dirs: list[Path]) -> list[dict[str, Any]]:
    evidence: dict[tuple[str, str, str], tuple[str, dict[str, Any]]] = {}
    for run_dir in run_dirs:
        manifests = {str(item["id"]): item for item in read_jsonl(run_dir / "manifest.jsonl")}
        for result in read_jsonl(run_dir / "results.jsonl"):
            source = manifests.get(str(result.get("id")))
            if source is None:
                continue
            if result.get("source_sha256") not in (None, content_hash(source)):
                raise ValueError(f"Mismatched manifest/result content in {run_dir.name}, block {result.get('id')}")
            evidence[key(source)] = (run_dir.name, result)

    merged: list[dict[str, Any]] = []
    for item in current:
        found = evidence.get(key(item))
        legacy = bool(item.get("legacy_hash_exception", False))
        if found is None:
            merged.append({
                "id": item.get("id"), "lang": item.get("lang"), "module": item.get("module"),
                "file": item.get("file"), "start": item.get("start"), "end": item.get("end"),
                "source_sha256": content_hash(item), "legacy_hash_exception": legacy,
                "l1": {"status": "NOT_VERIFIED", "detail": "no matching evidence for current content"},
                "l2": {"status": "NOT_VERIFIED", "detail": "no matching evidence for current content"},
                "classification": "NOT_VERIFIED", "evidence_run": None, "evidence_original_id": None,
            })
            continue

        run_name, result = found
        legacy = bool(result.get("legacy_hash_exception", legacy))
        merged.append({
            "id": item.get("id"), "lang": item.get("lang"), "module": item.get("module"),
            "file": item.get("file"), "start": item.get("start"), "end": item.get("end"),
            "source_sha256": content_hash(item), "legacy_hash_exception": legacy,
            "l1": result.get("l1", {"status": "NOT_VERIFIED", "detail": "missing L1 evidence"}),
            "l2": result.get("l2", {"status": "NOT_VERIFIED", "detail": "missing L2 evidence"}),
            "classification": classification(result),
            "evidence_run": Path(run_name).name, "evidence_original_id": result.get("id"),
        })
    return merged


def write_output(records: list[dict[str, Any]], output: Path, runs: list[Path]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    with (output / "results.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    summary = {
        "total": len(records),
        "classification": dict(sorted(Counter(item["classification"] for item in records).items())),
        "l1": dict(sorted(Counter(item["l1"]["status"] for item in records).items())),
        "l2": dict(sorted(Counter(item["l2"]["status"] for item in records).items())),
        "evidence_runs": [run.name for run in runs],
        "match_key": ["file", "lang", "sha256(manifest.content UTF-8)"],
    }
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "report.md").write_text(
        "# Merged verification evidence\n\n"
        f"Merged {len(records)} current manifest records. Evidence is reused only when `{summary['match_key'][0]}`, "
        f"`{summary['match_key'][1]}`, and `{summary['match_key'][2]}` match; later run directories take priority. "
        "Unmatched content remains `NOT_VERIFIED`. The legacy hash marker is retained but does not override actual L1/L2 evidence. "
        "If a manifest has duplicate blocks with the same content key, each may reuse the same matching evidence row.\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--run", required=True, action="append", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    for run_dir in args.run:
        for name in ("manifest.jsonl", "results.jsonl"):
            if not (run_dir / name).is_file():
                parser.error(f"{run_dir} does not contain {name}")
    records = merge([b for b in read_jsonl(args.manifest) if not b.get("skipped", False)], args.run)
    write_output(records, args.output, args.run)


if __name__ == "__main__":
    main()
