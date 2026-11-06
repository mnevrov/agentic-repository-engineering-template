#!/usr/bin/env python3
"""One-command finalization for v0.1.0, run by an authenticated repository admin.

Requires GitHub CLI with repository Administration:write, a configured local
Git signing identity/key registered on GitHub, and an up-to-date clean checkout.
No secrets are written into files, Git commits or diagnostic output.

This tool is NOT invoked by CI and intentionally cannot forge either the
branch ruleset, the independent-review waiver, or the verified tag.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = "mnevrov/agentic-repository-engineering-template"
TAG = "v0.1.0"
RULESET_NAME = "protect-main-opencode-template"
REQUIRED_CHECKS = {
    "doctor",
    "OpenCode v2.1.2 configuration",
    "OpenCode v2.2.5 configuration",
}
ROOT = Path(__file__).resolve().parents[1]
RULESET_PATH = ROOT / "docs/release/MAIN_RULESET.json"
NOTES_PATH = ROOT / "docs/releases/v0.1.0.md"
APPROVAL_PATH = ROOT / "docs/release/OWNER_RELEASE_APPROVAL.md"


class FinalizationBlocked(RuntimeError):
    """A release gate or required local capability has not been satisfied."""


def command(*args: str, check: bool = True) -> str:
    try:
        process = subprocess.run(args, cwd=ROOT, text=True,
                                 capture_output=True, timeout=120)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        raise FinalizationBlocked(
            f"Required command unavailable or timed out: {args[0]}"
        ) from exc
    if check and process.returncode:
        # Do not echo raw command output: it could contain credentials.
        raise FinalizationBlocked(
            f"Command failed (exit {process.returncode}): {args[0]} {args[1] if len(args)>1 else ''}"
        )
    return process.stdout.strip()


def gh_api(endpoint: str) -> object:
    result = command("gh", "api", f"repos/{REPO}/{endpoint}")
    try:
        return json.loads(result)
    except json.JSONDecodeError as exc:
        raise FinalizationBlocked(f"Invalid JSON from GitHub API: {endpoint}") from exc


def validate_rules(rules: list[dict]) -> None:
    """Fail closed if the effective branch rules omit any hard requirement."""
    types = {rule.get("type") for rule in rules}
    needed = {"deletion", "non_fast_forward",
              "pull_request", "required_status_checks"}
    if not needed <= types:
        raise FinalizationBlocked(
            f"Active rules do not cover all required types: {sorted(needed - types)}"
        )
    checks = set()
    for rule in rules:
        if rule.get("type") == "required_status_checks":
            params = rule.get("parameters") or {}
            if not params.get("strict_required_status_checks_policy"):
                raise FinalizationBlocked("Required CI checks must be strict")
            checks |= {
                item["context"] for item in params.get("required_status_checks", [])
                if isinstance(item, dict) and isinstance(item.get("context"), str)
            }
    if not REQUIRED_CHECKS <= checks:
        raise FinalizationBlocked(
            f"Missing required status checks: {sorted(REQUIRED_CHECKS - checks)}"
        )


def check_exact_ci(sha: str) -> None:
    doc = gh_api(f"commits/{sha}/check-runs?per_page=100")
    if not isinstance(doc, dict):
        raise FinalizationBlocked("GitHub check-runs payload has wrong shape")
    runs = doc.get("check_runs")
    if not isinstance(runs, list):
        raise FinalizationBlocked("No check-runs returned for the exact commit")
    by_name = {
        item.get("name"): item for item in runs if isinstance(item, dict)
    }
    bad = {
        name for name in REQUIRED_CHECKS
        if name not in by_name or by_name[name].get("conclusion") != "success"
        or by_name[name].get("status") != "completed"
    }
    if bad:
        raise FinalizationBlocked(
            f"Exact SHA {sha[:12]} has missing/non-PASS CI: {sorted(bad)}"
        )


def current_main_sha() -> str:
    remote = gh_api("branches/main")
    if not isinstance(remote, dict):
        raise FinalizationBlocked("Cannot identify remote main")
    sha = (remote.get("commit") or {}).get("sha")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise FinalizationBlocked("Malformed GitHub main SHA")
    return sha


def check_local_checkout(sha: str) -> None:
    if command("gh", "repo", "view", "--json", "nameWithOwner",
               "--jq", ".nameWithOwner") != REPO:
        raise FinalizationBlocked("Current checkout is not the expected repository")
    if command("git", "branch", "--show-current") != "main":
        raise FinalizationBlocked("Switch to local main before signing")
    if command("git", "status", "--porcelain"):
        raise FinalizationBlocked("Local working tree is not clean")
    if command("git", "rev-parse", "HEAD") != sha:
        raise FinalizationBlocked(
            "Local HEAD differs from GitHub main; update using git pull --ff-only"
        )
    approval = APPROVAL_PATH.read_text(encoding="utf-8")
    for phrase in ("OWNER APPROVED", "independent review: waived", "E4: owner-reported"):
        if phrase not in approval:
            raise FinalizationBlocked(f"Missing release approval record: {phrase}")


def check_signing_prerequisites() -> None:
    """Refuse to change remote protection before checking signing tools."""
    if not command("git", "config", "--get", "user.name", check=False):
        raise FinalizationBlocked("Git user.name is missing")
    if not command("git", "config", "--get", "user.email", check=False):
        raise FinalizationBlocked("Git user.email is missing")
    sec = command("gpg", "--list-secret-keys", "--with-colons", check=False)
    if not any(line.startswith("sec:") for line in sec.splitlines()):
        raise FinalizationBlocked(
            "No local GPG secret signing key; configure Git signing before release"
        )


def ensure_active_ruleset() -> None:
    rulesets = gh_api("rulesets")
    if not isinstance(rulesets, list):
        raise FinalizationBlocked("GitHub rulesets response is not a list")
    matching = [v for v in rulesets if v.get("name") == RULESET_NAME]
    if len(matching) > 1:
        raise FinalizationBlocked("Ambiguous duplicate release rulesets")
    if not matching:
        if not RULESET_PATH.is_file():
            raise FinalizationBlocked("Ruleset source JSON missing")
        desired = json.loads(RULESET_PATH.read_text(encoding="utf-8"))
        validate_rules(desired.get("rules", []))
        print("Applying main ruleset using GitHub repository admin permission")
        command("gh", "api", "--method", "POST",
                f"repos/{REPO}/rulesets", "--input", str(RULESET_PATH))
        rulesets = gh_api("rulesets")
        matching = [v for v in rulesets if v.get("name") == RULESET_NAME]
    if len(matching) != 1:
        raise FinalizationBlocked("Ruleset was not created exactly once")
    record = gh_api(f"rulesets/{matching[0]['id']}")
    if not isinstance(record, dict) or record.get("enforcement") != "active":
        raise FinalizationBlocked("Ruleset is not active")
    validate_rules(record.get("rules", []))
    branch = gh_api("branches/main")
    if not isinstance(branch, dict) or not branch.get("protected"):
        raise FinalizationBlocked("GitHub main is not actually protected")
    # Required effective protection can also include org rulesets.
    effective = gh_api("rules/branches/main")
    if not isinstance(effective, list):
        raise FinalizationBlocked("Cannot verify effective branch rules")
    validate_rules(effective)
    print("Active main protection verified by GitHub")


def git_tag_ref() -> tuple[str, str] | None:
    """Return (annotated tag object SHA, target commit SHA) if tag exists."""
    refs = command("git", "ls-remote", "--tags", "origin",
                   f"refs/tags/{TAG}", f"refs/tags/{TAG}^{{}}")
    if not refs:
        return None
    mapping = {}
    for line in refs.splitlines():
        sha, ref = line.split("\t", 1)
        mapping[ref] = sha
    obj = mapping.get(f"refs/tags/{TAG}")
    commit = mapping.get(f"refs/tags/{TAG}^{{}}")
    if not obj or not commit:
        raise FinalizationBlocked("Existing tag is lightweight or not annotated")
    return obj, commit


def ensure_signed_verified_tag(sha: str) -> None:
    existing = git_tag_ref()
    if not existing:
        if command("git", "tag", "--list", TAG):
            raise FinalizationBlocked(
                "Local tag exists but remote does not: inspect manually"
            )
        print(f"Signing annotated tag {TAG} with configured local Git key")
        command("git", "tag", "-s", TAG, "-m",
                f"Agentic Repository Engineering Template {TAG}", sha)
        command("git", "tag", "-v", TAG)
        command("git", "push", "origin", f"refs/tags/{TAG}")
        existing = git_tag_ref()
    if not existing or existing[1] != sha:
        raise FinalizationBlocked("Remote signed tag target differs from exact CI SHA")
    tag_obj = gh_api(f"git/tags/{existing[0]}")
    if not isinstance(tag_obj, dict):
        raise FinalizationBlocked("GitHub did not return an annotated tag")
    if ((tag_obj.get("object") or {}).get("sha") != sha
            or (tag_obj.get("verification") or {}).get("verified") is not True):
        raise FinalizationBlocked(
            "GitHub does not mark the annotated tag as Verified; release stopped"
        )
    print("GitHub verified the signed tag")


def publish_and_verify(sha: str) -> str:
    existing = command("gh", "release", "view", TAG,
                       "--json", "tagName,isDraft,isPrerelease,url", check=False)
    if existing:
        try:
            data = json.loads(existing)
        except json.JSONDecodeError as exc:
            raise FinalizationBlocked("Unable to inspect existing release") from exc
        if (data.get("tagName") != TAG or data.get("isDraft") is True
                or data.get("isPrerelease") is True):
            raise FinalizationBlocked("Existing release is not a final v0.1.0")
        url = data.get("url")
    else:
        print("Publishing final GitHub Release from verified signed tag")
        command("gh", "release", "create", TAG, "--verify-tag",
                "--title", f"Agentic Repository Engineering Template {TAG}",
                "--notes-file", str(NOTES_PATH))
        data = json.loads(command("gh", "release", "view", TAG,
                                  "--json", "tagName,isDraft,isPrerelease,url"))
        if (data.get("tagName") != TAG or data.get("isDraft")
                or data.get("isPrerelease")):
            raise FinalizationBlocked("Published release is not final")
        url = data.get("url")
    if not isinstance(url, str) or not url.startswith("https://github.com/"):
        raise FinalizationBlocked("Release URL cannot be verified")
    if current_main_sha() != sha:
        raise FinalizationBlocked("main changed during release process")
    return url


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--preflight", action="store_true",
                   help="read-only checks; never apply rulesets or publish")
    args = p.parse_args()
    sha = current_main_sha()
    check_local_checkout(sha)
    check_exact_ci(sha)
    if not NOTES_PATH.is_file():
        raise FinalizationBlocked("Missing final release notes")
    check_signing_prerequisites()
    print(f"Exact main CI PASS: {sha}")
    if args.preflight:
        print("PRE-FLIGHT PASS: code and consent recorded; no remote changes")
        return 0
    ensure_active_ruleset()
    if current_main_sha() != sha:
        raise FinalizationBlocked("main moved after ruleset activation")
    ensure_signed_verified_tag(sha)
    url = publish_and_verify(sha)
    print(f"FINAL RELEASE PUBLISHED: {url}")
    # A release is already complete at this point. Failure to update the issue
    # must not misreport the published release as uncreated.
    try:
        command(
            "gh", "issue", "comment", "9", "--repo", REPO,
            "--body", (
                f"v0.1.0 RELEASED: {url}\n"
                f"Exact SHA: `{sha}`\n"
                "Tag: signed and GitHub Verified. main rules active. "
                "Owner waiver of final independent review and owner-reported "
                "HOST/E4 documented in docs/release/OWNER_RELEASE_APPROVAL.md."
            ),
        )
        command("gh", "issue", "close", "9", "--repo", REPO,
                "--reason", "completed")
        print("Release gate issue #9 closed with provenance")
    except FinalizationBlocked as exc:
        print(f"WARNING: release exists, but issue #9 update failed: {exc}",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FinalizationBlocked as exc:
        print(f"RELEASE BLOCKED: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
