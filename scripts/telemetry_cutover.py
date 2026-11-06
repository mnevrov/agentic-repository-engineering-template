"""One-time cutover from the template's telemetry to a new project's ledger.

The cutover exception is bound to provenance, not to the mere presence of an
initializer marker. A reset is allowed only when every condition below holds;
any unverifiable condition fails closed:

1. Shape (cheap, checked first): the base ledger is source-only ``TEMPLATE-*``
   history and the new ledger holds no ``TEMPLATE-*`` rows.
2. Verifiable history: full (non-shallow) clone, no ``url.*.insteadOf``
   rewriting that could mask the real fetch target.
3. Provenance identity: ``remote.origin.url`` must parse, after
   canonicalization (no dot-segments, dotted host, >=2 path segments), to a
   hosted ``host/owner/repo`` identity whose repository-name segment is
   neither the source template's nor an equal-named mirror of it. Missing or
   unparsable origins (local path, file://, single-segment) are not a
   trustworthy credential.
4. Lineage and single use: ``base_ref`` is a well-formed, dash-free commit and
   an ancestor of HEAD; the marker is a regular-file blob committed in HEAD
   (content read from the HEAD blob only, never the worktree) with valid
   content; the marker is absent in ``base_ref`` and in the unique root
   commit; EVERY commit strictly between ``base_ref`` and HEAD carries the
   marker; and every such commit's project ledger (when present and
   non-source-only) is a prefix of the new ledger. Presenting an older
   pre-bootstrap ancestor as the base therefore can never re-open the
   exception after the first project commit, and mid-history deletions stay
   append-only violations.
5. Birth-from-template: the unique root commit must carry the ledger with the
   template's source-only ``TEMPLATE-*`` rows — the signature of a repository
   created from the template contents (GitHub 'Create from template' and the
   documented `git init` method both keep them). A full clone of the source
   template has no ledger at its root at all, so re-labelling its origin can
   never let it cut the inherited ledger over, and mid-history project rows
   stay protected by the prefix condition above.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

MARKER = ".ai/project-initialized"
TELEMETRY_REL = ".ai/telemetry/cycles.jsonl"
SOURCE_REPOSITORY = "mnevrov/agentic-repository-engineering-template"
SOURCE_REPOSITORY_NAME = SOURCE_REPOSITORY.rsplit("/", 1)[-1]

# scp-style ssh remote: [user@]host:owner/repo(.git)
_SCP_STYLE = re.compile(r"^(?:[^@/]+@)?(?P<host>[^/\s:]+):(?P<path>\S+)$")
_TRUSTED_SCHEMES = {"http", "https", "ssh", "git"}
# Refs feeding git command lines must never look like options or hold spaces.
UNSAFE_REF = re.compile(r"^-|\s")
_MARKER_MODES = {"100644": "blob", "100755": "blob", "120000": "symlink",
                 "160000": "submodule"}


def _strip_git_suffix(path: str) -> str:
    return path[:-4] if path.endswith(".git") else path


def _canonical_segments(path: str) -> list[str] | None:
    """Split a URL path into canonical segments or return None.

    Rejects dot-segments outright: `..` in a remote path is an aliasing trick
    (git and HTTP servers resolve it). Empty and `.` segments are dropped, and
    one optional trailing `.git` suffix on the repository segment is stripped.
    """
    segments = [segment for segment in path.split("/") if segment and segment != "."]
    if any(segment == ".." for segment in segments):
        return None
    if segments and segments[-1].endswith(".git"):
        segments[-1] = segments[-1][:-4]
    return segments


def repository_identity(url: str) -> str | None:
    """Normalize a git remote URL to 'host/owner/repo' (lowercase).

    Returns None when the URL cannot be parsed into a trustworthy hosted
    repository identity (missing host, local path, file://, host without a
    dot, fewer than two canonical path segments, dot-segment aliasing).
    Callers must treat None as 'identity not verifiable'.
    """
    url = url.strip().lower().rstrip("/")
    if not url:
        return None
    if "://" in url:
        parts = urlsplit(url)
        if parts.scheme not in _TRUSTED_SCHEMES:
            return None
        host = parts.netloc.rsplit("@", 1)[-1]
        path = parts.path
    else:
        match = _SCP_STYLE.match(url)
        if not match:
            # A bare filesystem path is not a verifiable hosted identity.
            return None
        host, path = match.group("host"), match.group("path")
    host = host.partition(":")[0].rstrip(".")
    segments = _canonical_segments(path)
    if not host or "." not in host or segments is None or len(segments) < 2:
        return None
    return "/".join([host] + segments[-2:])


def source_identity_matches(identity: str | None) -> bool:
    """True when the identity IS the source template or an equal-named mirror.

    Mirrors (e.g. an internal GitLab copy keeping the repository name under a
    different owner path) must not cut their inherited ledger over; a
    downstream project is expected to have its own repository name before
    bootstrap.
    """
    if not identity:
        return False
    return identity.rsplit("/", 1)[-1] == SOURCE_REPOSITORY_NAME


def source_url_matches(url: str) -> bool:
    """Broad raw-URL containment check against the source template.

    Used by init-project's destructive-action guard where the cost of a false
    'this is the source' verdict is only refusing init. Matches the canonical
    source path on any host/scheme and treats any URL or local path whose
    final path segment equals the source repository name as the source:
    a clone that kept the template's name (including `git clone /path/to/…`)
    still carries the full template history and must never be initialized in
    place. Downstream projects rename the repository before init.
    """
    url = url.strip().lower().rstrip("/")
    if not url:
        return False
    source = SOURCE_REPOSITORY.lower()
    if url.endswith("/" + source) or url.endswith(":" + source):
        return True
    tail = url.replace("://", "/").rsplit("/", 1)[-1]
    return _strip_git_suffix(tail) == SOURCE_REPOSITORY_NAME


def origin_url(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=repo, capture_output=True, text=True
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _insteadof_bases(config_entries: list[tuple[str, str]]) -> list[str]:
    """All configured url.<base>.insteadOf bases (each may rewrite origins)."""
    return [value for key, value in config_entries
            if key.startswith("url.") and key.endswith(".insteadof")
            and value.strip()]


def _origin_rewritten(repo: Path, url: str) -> bool:
    proc = subprocess.run(
        ["git", "config", "--list", "--null"],
        cwd=repo, capture_output=True, text=True
    )
    if proc.returncode != 0:
        return True
    entries: list[tuple[str, str]] = []
    for record in proc.stdout.split("\0"):
        if not record:
            continue
        key, _, value = record.partition("\n")
        entries.append((key.lower(), value))
    return any(url.startswith(base) for base in _insteadof_bases(entries))


def trusted_repository_identity(repo: Path) -> str | None:
    """Parse remote.origin.url of `repo` into a hosted identity, or None.

    Returns None when the effective fetch target cannot be trusted: a missing
    or unparsable origin, or an origin subject to url.*.insteadOf rewriting.
    """
    url = origin_url(repo)
    identity = repository_identity(url)
    if identity is None:
        return None
    if _origin_rewritten(repo, url):
        return None
    return identity


def source_only(lines: list[str]) -> bool:
    if not lines:
        return False
    try:
        rows = [json.loads(line) for line in lines]
    except (TypeError, ValueError):
        return False
    return all(
        isinstance(row, dict)
        and isinstance(row.get("task_id"), str)
        and row["task_id"].startswith("TEMPLATE-")
        for row in rows
    )


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)


def _marker_kind_at(repo: Path, ref: str) -> str | None:
    """'blob'/'symlink'/'submodule'/… for MARKER at `ref`, or None (absent).

    Fails closed (raises) on any git error; the caller has already verified
    `ref` is a commit.
    """
    proc = _git(repo, "ls-tree", "-r", ref, "--", MARKER)
    if proc.returncode != 0:
        raise RuntimeError(f"cannot inspect marker at {ref}: {proc.stderr.strip()}")
    entry = proc.stdout.strip()
    if not entry:
        return None
    return _MARKER_MODES.get(entry.split()[0], "special")


def _marker_exists_at(repo: Path, ref: str) -> bool:
    return _marker_kind_at(repo, ref) is not None


def _regular_marker_text_at(repo: Path, ref: str) -> str | None:
    """Marker content committed at `ref` when the path is a regular file."""
    if _marker_kind_at(repo, ref) != "blob":
        return None
    proc = _git(repo, "show", f"{ref}:{MARKER}")
    if proc.returncode != 0:
        return None
    return proc.stdout


def _valid_marker_content(text: str) -> bool:
    lines = text.splitlines()
    return bool(
        any(line.startswith("project_name=") and line[13:].strip() for line in lines)
        and any(line.startswith("bootstrap_id=") and line[13:].strip() for line in lines)
    )


def _telemetry_lines_at(repo: Path, ref: str) -> list[str] | None:
    """Ledger lines committed at `ref`, or None when the path is absent."""
    proc = _git(repo, "show", f"{ref}:{TELEMETRY_REL}")
    if proc.returncode == 0:
        return proc.stdout.splitlines()
    if "does not exist in" in proc.stderr or "exists on disk, but not in" in proc.stderr:
        return None
    raise RuntimeError(f"cannot read telemetry at {ref}: {proc.stderr.strip()}")


def _root_commit(repo: Path) -> str | None:
    proc = _git(repo, "rev-list", "--max-parents=0", "HEAD")
    if proc.returncode != 0:
        return None
    roots = proc.stdout.split()
    if len(roots) != 1:
        # Disjoint or grafted history: provenance cannot be verified.
        return None
    return roots[0]


def _is_shallow(repo: Path) -> bool:
    proc = _git(repo, "rev-parse", "--is-shallow-repository")
    # Unknown output is treated as shallow: fail closed.
    return proc.returncode != 0 or proc.stdout.strip() != "false"


def _unverifiable_new(rows: list[str]) -> bool:
    try:
        records = [json.loads(line) for line in rows]
    except (TypeError, ValueError):
        return True
    return not all(
        isinstance(row, dict)
        and isinstance(row.get("task_id"), str)
        and not row["task_id"].startswith("TEMPLATE-")
        for row in records
    )


def _is_subsequence(needle: list[str], haystack: list[str]) -> bool:
    """Order-preserving containment, tolerant of rows interleaved by merges."""
    position = 0
    for line in needle:
        try:
            position = haystack.index(line, position) + 1
        except ValueError:
            return False
    return True


def history_monotonic(repo: Path, base_ref: str, new: list[str]) -> bool:
    """True when no ledger committed between base_ref and HEAD contradicts
    the final ledger.

    Only commits that touched the ledger are inspected. Every such historical
    ledger must be an order-preserving subsequence of `new`; a row that was
    deleted, rewritten, or reordered in the middle of the range cannot be
    hidden by driving the check against an older legitimate base, such as a
    stale PR target branch. Source-only (TEMPLATE-*) ledgers are the normal
    state for merge bases and pre-cutover commits and are exempt. Malformed
    `base_ref` values are a violation of the append-only contract itself.
    """
    if not base_ref or UNSAFE_REF.search(base_ref):
        return False
    touching = _git(repo, "rev-list", f"{base_ref}..HEAD", "--", TELEMETRY_REL)
    if touching.returncode != 0:
        return False
    for commit in touching.stdout.split():
        try:
            rows = _telemetry_lines_at(repo, commit)
        except RuntimeError:
            return False
        if rows is None or source_only(rows):
            continue
        if not _is_subsequence(rows, new):
            return False
    return True


def bootstrap_cutover(repo: Path, base_ref: str, old: list[str], new: list[str]) -> bool:
    """Allow a ledger reset only for a verified first downstream bootstrap.

    Every condition is mandatory and fail-closed. Never allow this exception
    after the marker exists in the baseline or in any commit between base and
    HEAD, in the repository's root commit, in the source template or any
    equal-named mirror, in a shallow clone, or when the running repository's
    origin does not provide a trustworthy hosted identity.
    """
    # 1. Baseline shape first: it is free and rejects the common case.
    if not base_ref or UNSAFE_REF.search(base_ref) or not source_only(old) or _unverifiable_new(new):
        return False

    # 2. Verifiable full history; no insteadOf masking of the fetch target.
    if _is_shallow(repo):
        return False

    # 3. Provenance identity of the repository the check runs in.
    identity = trusted_repository_identity(repo)
    if identity is None or source_identity_matches(identity):
        return False

    # The base must be a real commit and an ancestor of HEAD.
    if _git(repo, "rev-parse", "--verify", "--quiet", f"{base_ref}^{{commit}}").returncode != 0:
        return False
    if _git(repo, "merge-base", "--is-ancestor", base_ref, "HEAD").returncode != 0:
        return False

    # 4. Marker: regular-file blob committed in HEAD with valid content read
    #    from the HEAD blob (never the worktree); absent in the base ref.
    marker = _regular_marker_text_at(repo, "HEAD")
    if marker is None or not _valid_marker_content(marker):
        return False
    if _marker_exists_at(repo, base_ref):
        return False

    # 4b. Birth-from-template: the unique root's ledger must exist and be
    #     source-only (a repository created FROM the template contents), and
    #     the marker must not exist there. This rejects full clones of the
    #     source template, whose root predates the ledger entirely. A root
    #     with no/empty ledger never needs this exception at all: history in
    #     such a repo never held TEMPLATE-* rows, so plain append-only applies.
    root = _root_commit(repo)
    if root is None or _marker_exists_at(repo, root):
        return False
    root_rows = _telemetry_lines_at(repo, root)
    if root_rows is None or not source_only(root_rows):
        return False

    # 4c. Single use and mid-history integrity over the whole range: every
    #     commit between base and HEAD (exclusive of base, checked above)
    #     must carry the marker, and no ledger inside the range may contradict
    #     the new one. An older pre-bootstrap ancestor can therefore never be
    #     presented as base to re-open the exception, and rewriting project
    #     rows in the middle of the range fails as well.
    between = _git(repo, "rev-list", f"{base_ref}..HEAD")
    if between.returncode != 0:
        return False
    for commit in between.stdout.split():
        if not _marker_exists_at(repo, commit):
            return False
    return history_monotonic(repo, base_ref, new)
