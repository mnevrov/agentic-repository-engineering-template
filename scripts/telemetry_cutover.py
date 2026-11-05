"""One-time cutover from the template's telemetry to a new project's ledger.

The cutover exception is bound to provenance, not to the mere presence of an
initializer marker. A reset is allowed only when every condition below holds;
any unverifiable condition fails closed:

1. Provenance identity: the repository the check runs in must expose an
   origin whose URL parses to a hosted ``host/owner/repo`` identity. A missing
   or unparsable (local path, file://, exotic) origin is not a trustworthy
   credential and forbids the exception. The identity must not be the source
   template repository itself.
2. Lineage: the marker must be committed in HEAD, read from the HEAD blob
   (never from the worktree), absent in the base ref, and absent in the
   repository's root commit; the base ref must be an ancestor of HEAD.
3. Baseline shape: the root commit's telemetry (when present) must be
   source-only; the base ledger must be source-only TEMPLATE-* history; the
   new ledger must contain no TEMPLATE-* rows.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit

MARKER = ".ai/project-initialized"
SOURCE_REPOSITORY = "mnevrov/agentic-repository-engineering-template"

# scp-style ssh remote: [user@]host:owner/repo(.git)
_SCP_STYLE = re.compile(r"^(?:[^@/]+@)?(?P<host>[^/\s:]+):(?P<path>\S+)$")
_TRUSTED_SCHEMES = {"http", "https", "ssh", "git"}


def repository_identity(url: str) -> str | None:
    """Normalize a git remote URL to 'host/owner/repo' (lowercase).

    Returns None when the URL cannot be parsed into a trustworthy hosted
    repository identity (missing host, local path, file:// or single-segment
    path). Callers must treat None as 'identity not verifiable'.
    """
    url = url.strip().lower().rstrip("/")
    if not url:
        return None
    if url.endswith(".git"):
        url = url[:-4]
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
    host = host.partition(":")[0]
    segments = [segment for segment in path.split("/") if segment]
    if "." not in host or len(segments) < 2:
        return None
    return "/".join([host] + segments[-2:])


def source_url_matches(url: str) -> bool:
    """Broad raw-URL containment check against the source template name.

    Used by init-project's defensive guard: any origin whose normalized URL
    ends with the source repository path (including local-path clones) is
    treated as the source template checkout.
    """
    url = url.strip().lower().rstrip("/")
    if url.endswith(".git"):
        url = url[:-4]
    source = SOURCE_REPOSITORY.lower()
    return url.endswith("/" + source) or url.endswith(":" + source)


def source_identity_matches(identity: str | None) -> bool:
    return bool(identity) and identity.endswith("/" + SOURCE_REPOSITORY.lower())


def origin_url(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=repo, capture_output=True, text=True
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def trusted_repository_identity(repo: Path) -> str | None:
    """Parse remote.origin.url of `repo` into a hosted identity, or None."""
    return repository_identity(origin_url(repo))


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


def _marker_exists_at(repo: Path, ref: str) -> bool:
    """True when the `ref` tree contains the marker path. Fails closed on
    any git error (the caller has already verified `ref` is a commit)."""
    proc = _git(repo, "ls-tree", "--name-only", "-r", ref, "--", MARKER)
    if proc.returncode != 0:
        raise RuntimeError(f"cannot inspect marker at {ref}: {proc.stderr.strip()}")
    return bool(proc.stdout.strip())


def _marker_text_at_head(repo: Path) -> str | None:
    """Marker content committed at HEAD, or None when absent/unreadable."""
    proc = _git(repo, "show", f"HEAD:{MARKER}")
    if proc.returncode != 0:
        return None
    return proc.stdout


def _root_commit(repo: Path) -> str | None:
    proc = _git(repo, "rev-list", "--max-parents=0", "HEAD")
    if proc.returncode != 0:
        return None
    roots = proc.stdout.split()
    if len(roots) != 1:
        # Disjoint or grafted history: provenance cannot be verified.
        return None
    return roots[0]


def _valid_marker_content(text: str) -> bool:
    lines = text.splitlines()
    return bool(
        any(line.startswith("project_name=") and line[13:].strip() for line in lines)
        and any(line.startswith("bootstrap_id=") and line[13:].strip() for line in lines)
    )


def bootstrap_cutover(repo: Path, base_ref: str, old: list[str], new: list[str]) -> bool:
    """Allow a ledger reset only for a verified first downstream bootstrap.

    Every condition is mandatory and fail-closed. Never allow this exception
    after the marker exists in the baseline, in the repository's root commit,
    in the source template repository itself, or when the running repository's
    origin does not provide a trustworthy hosted identity.
    """
    # 1. Provenance identity of the repository the check runs in.
    identity = trusted_repository_identity(repo)
    if identity is None or source_identity_matches(identity):
        return False

    # The base must be a real commit and an ancestor of HEAD.
    if _git(repo, "rev-parse", "--verify", "--quiet", f"{base_ref}^{{commit}}").returncode != 0:
        return False
    if _git(repo, "merge-base", "--is-ancestor", base_ref, "HEAD").returncode != 0:
        return False

    # 2. Marker committed in HEAD (content from the HEAD blob, never the
    #    worktree), absent in the base ref.
    marker = _marker_text_at_head(repo)
    if marker is None or not _valid_marker_content(marker):
        return False
    if _marker_exists_at(repo, base_ref):
        return False

    # 2b. Lineage: marker must not exist at the root commit, and the base must
    #     descend from a single root whose telemetry is source-only or absent.
    root = _root_commit(repo)
    if root is None:
        return False
    if _marker_exists_at(repo, root):
        return False
    root_telemetry = _git(repo, "show", f"{root}:.ai/telemetry/cycles.jsonl")
    if root_telemetry.returncode == 0:
        rows = root_telemetry.stdout.splitlines()
        if rows and not source_only(rows):
            return False
    elif "does not exist in" not in root_telemetry.stderr and \
            "exists on disk, but not in" not in root_telemetry.stderr:
        return False

    # 3. Baseline shape: TEMPLATE-* only before, never after.
    if not source_only(old):
        return False
    try:
        records = [json.loads(line) for line in new]
    except (TypeError, ValueError):
        return False
    return all(
        isinstance(row, dict)
        and isinstance(row.get("task_id"), str)
        and not row["task_id"].startswith("TEMPLATE-")
        for row in records
    )
