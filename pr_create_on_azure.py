#!/usr/bin/env python3
"""Create an Azure DevOps PR the same way Cursor does for the `pr` trigger.

Mirrors `.cursor/rules/azure-devops-pr-work-item.mdc`:
  - resolve stacked parent target (HEAD reflog → surviving ancestor)
  - push if needed
  - create PR titled from the work item title when available
  - link Task from branch prefix
  - add Android team reviewers (m.mokhtari required)
  - set auto-complete
  - move Task to Review (Completed += Remaining, Remaining = 0)
  - print a Goft-ready block

Requires: AZDO_PAT (see docs/azure-devops-pat.md). Stdlib only.

Usage:
  ./pr_create_on_azure.py
  ./pr_create_on_azure.py --into 55816-Feature-Loan
  ./pr_create_on_azure.py --draft --dry-run
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ORG = "https://azure.charisma.tech/Brokerage"
COLLECTION_APIS = f"{ORG}/_apis"
PROJECT_APIS = f"{ORG}/Trader/_apis"
REPO_NAME = "AndriodTraderApp"
PROJECT_ID = "e45539a6-393c-4129-9db8-1ce5febabe6c"
REPO_ID = "887f1492-4676-4e62-83a1-6a5fb9203aab"
ANDROID_TEAM_ID = "2e7de6e8-bb95-4b8f-808f-fa45b7f57c5c"
REQUIRED_REVIEWER_ID = "485a87be-9627-4004-b022-f76816ce8354"
REQUIRED_REVIEWER_NAME = "Masood Mokhtari"
TRUNK_BRANCHES = ("develop", "staging", "master")
JUNK_BRANCH_RE = re.compile(
    r"^(aaaaaaaaaaa|tmp|temp|test|wip)$",
    re.IGNORECASE,
)
CHECKOUT_RE = re.compile(
    r"checkout: moving from (?P<frm>\S+) to (?P<to>\S+)\s*$"
)
CREATED_FROM_RE = re.compile(r"branch: Created from (?P<ref>\S+)\s*$")
TASK_ID_RE = re.compile(r"^(\d+)-")


class Fatal(SystemExit):
    """Exit with a short message (no traceback)."""


def run(cmd: list[str], *, check: bool = True) -> str:
    result = subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        err = (result.stderr or result.stdout or "").strip()
        raise Fatal(f"Command failed ({result.returncode}): {' '.join(cmd)}\n{err}")
    return (result.stdout or "").rstrip("\n")


def strip_ref(name: str) -> str:
    name = name.strip()
    for prefix in ("refs/heads/", "refs/remotes/origin/", "origin/"):
        if name.startswith(prefix):
            name = name[len(prefix) :]
    return name


def is_junk(name: str) -> bool:
    return bool(JUNK_BRANCH_RE.match(name)) or name in {".", ".."}


def remote_exists(branch: str) -> bool:
    code = subprocess.run(
        ["git", "rev-parse", "--verify", f"origin/{branch}"],
        capture_output=True,
        text=True,
    ).returncode
    return code == 0


def ahead_count(branch: str) -> int | None:
    if not remote_exists(branch):
        return None
    mb = run(["git", "merge-base", "HEAD", f"origin/{branch}"])
    return int(run(["git", "rev-list", "--count", f"{mb}..HEAD"]))


def is_ancestor(branch: str) -> bool:
    if not remote_exists(branch):
        return False
    return (
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", f"origin/{branch}", "HEAD"],
            capture_output=True,
        ).returncode
        == 0
    )


def is_usable_target(branch: str, current: str) -> bool:
    """True if origin/<branch> can be a PR base for HEAD (never the current branch)."""
    if not branch or branch == current or is_junk(branch):
        return False
    if not remote_exists(branch):
        return False
    # Hopping between unrelated locals (A→B→A) must not pick B as parent of A
    # unless B is actually in HEAD's history.
    return is_ancestor(branch)


def parse_task_id(branch: str) -> str | None:
    m = TASK_ID_RE.match(branch)
    return m.group(1) if m else None


def load_pat() -> str:
    pat = os.environ.get("AZDO_PAT", "").strip()
    if pat:
        return pat
    # Non-interactive shells often skip most of ~/.bashrc; pull the export line.
    for rc in (Path.home() / ".bashrc", Path.home() / ".zshrc", Path.home() / ".profile"):
        if not rc.is_file():
            continue
        for line in rc.read_text(errors="ignore").splitlines():
            s = line.strip()
            if s.startswith("#") or "AZDO_PAT=" not in s:
                continue
            if s.startswith("export "):
                s = s[len("export ") :]
            if s.startswith("AZDO_PAT="):
                value = s.split("=", 1)[1].strip()
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]
                if value:
                    return value
    raise Fatal(
        "AZDO_PAT is not set. See docs/azure-devops-pat.md "
        "(export AZDO_PAT=... then restart the shell)."
    )


@dataclass
class TargetResolution:
    branch: str
    step: str
    deleted_intermediate: str | None = None


def resolve_target(current: str, override: str | None) -> TargetResolution:
    if override:
        override = strip_ref(override)
        if not remote_exists(override):
            raise Fatal(f"Override target origin/{override} does not exist.")
        return TargetResolution(override, "user override (--into)")

    head_log = run(["git", "reflog", "show", "HEAD", "-80"], check=False)
    checkouts: list[tuple[str, str]] = []
    for line in head_log.splitlines():
        # e.g. "abc123 HEAD@{1}: checkout: moving from A to B"
        if "checkout: moving from " not in line:
            continue
        m = CHECKOUT_RE.search(line)
        if not m:
            continue
        frm, to = strip_ref(m.group("frm")), strip_ref(m.group("to"))
        if frm and to and frm != to:
            checkouts.append((frm, to))

    # Step 2: walk HEAD reflog stack from current
    immediate: str | None = None
    for frm, to in checkouts:
        if to == current and frm != current and not is_junk(frm):
            immediate = frm
            break
    if immediate and is_usable_target(immediate, current):
        return TargetResolution(immediate, "HEAD reflog (immediate parent)")
    if immediate:
        # Walk through deleted (or unusable) stack branches. Skip bounces
        # back to the current branch (checkout A→B then B→A).
        cursor = immediate
        deleted = immediate if not remote_exists(immediate) else None
        for frm, to in checkouts:
            if to != cursor or is_junk(frm) or frm == cursor or frm == current:
                continue
            if is_usable_target(frm, current):
                return TargetResolution(
                    frm,
                    "HEAD reflog (nearest surviving parent)",
                    deleted_intermediate=deleted or immediate,
                )
            if not remote_exists(frm):
                deleted = deleted or frm
            cursor = frm

    # Step 3: current-branch reflog
    branch_log = run(["git", "reflog", "show", current, "-40"], check=False)
    for line in branch_log.splitlines():
        parent: str | None = None
        m = CHECKOUT_RE.search(line)
        if m and strip_ref(m.group("to")) == current:
            parent = strip_ref(m.group("frm"))
        else:
            m2 = CREATED_FROM_RE.search(line)
            if m2:
                parent = strip_ref(m2.group("ref"))
        if not parent or not is_usable_target(parent, current):
            continue
        return TargetResolution(parent, "current-branch reflog")

    # Step 4: nearest surviving feature ancestor from known stack bases
    candidates: list[str] = []
    missing_parent_task = parse_task_id(immediate) if immediate else None
    current_task = parse_task_id(current)
    for task in (missing_parent_task, current_task):
        if not task:
            continue
        listing = run(["git", "branch", "-r", "--list", f"origin/{task}-*"], check=False)
        for line in listing.splitlines():
            name = strip_ref(line.strip())
            if is_usable_target(name, current):
                candidates.append(name)

    # known stack bases from HEAD reflog checkouts
    for frm, to in checkouts:
        for name in (frm, to):
            if name in TRUNK_BRANCHES:
                continue
            if is_usable_target(name, current):
                candidates.append(name)

    picked = _pick_best(
        candidates, current, prefer_reflog_order=[frm for frm, _ in checkouts]
    )
    if picked:
        return TargetResolution(
            picked,
            "nearest surviving feature ancestor",
            deleted_intermediate=immediate if immediate and not remote_exists(immediate) else None,
        )

    # Step 5: trunk fallback
    trunk_pick = _pick_best(list(TRUNK_BRANCHES), current, prefer_reflog_order=[])
    if trunk_pick:
        return TargetResolution(trunk_pick, "trunk fallback")

    raise Fatal(
        "Could not resolve a remote parent/target branch. "
        "Pass --into <branch> explicitly."
    )


def _pick_best(
    candidates: list[str],
    current: str,
    prefer_reflog_order: list[str],
) -> str | None:
    scored: list[tuple[int, int, int, int, str]] = []
    # lower is better: (non_ancestor, ahead, trunk_penalty, reflog_index, name)
    reflog_index = {name: i for i, name in enumerate(prefer_reflog_order)}
    seen: set[str] = set()
    for name in candidates:
        if name in seen or not is_usable_target(name, current):
            continue
        seen.add(name)
        ahead = ahead_count(name)
        if ahead is None:
            continue
        non_ancestor = 0 if is_ancestor(name) else 1
        trunk_penalty = 0 if name not in TRUNK_BRANCHES else 1
        idx = reflog_index.get(name, 10_000)
        scored.append((non_ancestor, ahead, trunk_penalty, idx, name))
    if not scored:
        return None
    scored.sort()
    return scored[0][4]


class AzdoClient:
    def __init__(self, pat: str) -> None:
        self._auth = "Basic " + base64.b64encode(f":{pat}".encode()).decode()

    def request(
        self,
        method: str,
        url: str,
        body: Any | None = None,
        *,
        content_type: str = "application/json",
    ) -> Any:
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": self._auth,
                "Accept": "application/json",
                **({"Content-Type": content_type} if data is not None else {}),
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")
            raise Fatal(f"Azure DevOps {method} {url} → HTTP {e.code}\n{detail[:2000]}") from e
        except urllib.error.URLError as e:
            raise Fatal(f"Azure DevOps {method} {url} → {e}") from e

    def get(self, url: str) -> Any:
        return self.request("GET", url)

    def post(self, url: str, body: Any) -> Any:
        return self.request("POST", url, body)

    def put(self, url: str, body: Any) -> Any:
        return self.request("PUT", url, body)

    def patch(self, url: str, body: Any, *, json_patch: bool = False) -> Any:
        ctype = "application/json-patch+json" if json_patch else "application/json"
        return self.request("PATCH", url, body, content_type=ctype)


def ensure_pushed(current: str) -> None:
    run(["git", "fetch", "origin", "--prune"], check=False)
    upstream = run(
        ["git", "rev-parse", "--abbrev-ref", f"{current}@{{upstream}}"],
        check=False,
    )
    if not upstream:
        print(f"Pushing {current} (no upstream)…")
        run(["git", "push", "-u", "origin", "HEAD"])
        return
    local = run(["git", "rev-parse", "HEAD"])
    remote = run(["git", "rev-parse", upstream])
    if local != remote:
        print(f"Pushing {current} (local ahead/behind remote)…")
        run(["git", "push", "origin", "HEAD"])
    else:
        print(f"Branch up to date with {upstream}")


def fetch_work_item_title(client: AzdoClient, task_id: str) -> str | None:
    """Return System.Title for the work item, or None if missing/unreachable."""
    try:
        wi = client.get(f"{PROJECT_APIS}/wit/workitems/{task_id}?api-version=7.0")
    except Fatal as e:
        print(f"Warning: could not fetch work item #{task_id} for title: {e}", file=sys.stderr)
        return None
    title = (wi.get("fields") or {}).get("System.Title")
    if isinstance(title, str):
        title = title.strip()
        return title or None
    return None


def build_title_and_description(
    target: str,
    task_id: str | None,
    work_item_title: str | None = None,
) -> tuple[str, str]:
    commits = run(
        ["git", "log", "--oneline", f"origin/{target}..HEAD"],
        check=False,
    ).splitlines()
    if not commits:
        raise Fatal(f"No commits between origin/{target} and HEAD — nothing to PR.")

    # Prefer Azure work item title when available (same wording as the Task).
    if work_item_title:
        if task_id:
            # Avoid "#123 #123 Title" if WI title already starts with the id.
            wi = work_item_title
            if re.match(rf"^#?{re.escape(task_id)}\b", wi):
                title = wi if wi.startswith("#") else f"#{wi}"
            else:
                title = f"#{task_id} {wi}"
        else:
            title = work_item_title
    else:
        subject = commits[0].split(" ", 1)[-1]
        if task_id and not subject.startswith(f"#{task_id}"):
            title = f"#{task_id} {subject}"
        else:
            title = subject

    bullets = []
    for line in commits[:8]:
        msg = line.split(" ", 1)[-1]
        bullets.append(f"- {msg}")
    if len(commits) > 8:
        bullets.append(f"- …and {len(commits) - 8} more commit(s)")

    description = "## Summary\n" + "\n".join(bullets) + "\n\n## Test plan\n- [ ] Manual verification on device/emulator\n"
    return title, description


def short_description(commits_subject: str) -> str:
    # Strip leading "#12345 " for Goft blurb
    return re.sub(r"^#\d+\s*", "", commits_subject).strip()


def create_pr_flow(
    *,
    into: str | None,
    draft: bool,
    dry_run: bool,
    skip_push: bool,
) -> None:
    current = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if current in {"HEAD", ""}:
        raise Fatal("Detached HEAD — checkout a branch first.")

    if not skip_push and not dry_run:
        ensure_pushed(current)
    else:
        run(["git", "fetch", "origin", "--prune"], check=False)

    resolution = resolve_target(current, into)
    target = resolution.branch
    task_id = parse_task_id(current)

    print(f"Branch:  {current}")
    print(f"Target:  {target}  [{resolution.step}]")
    if resolution.deleted_intermediate:
        print(
            f"Note:    intermediate parent '{resolution.deleted_intermediate}' "
            "missing on origin; used nearest surviving parent"
        )
    print(f"Task:    {task_id or '(none — work-item update will be skipped)'}")
    ahead = ahead_count(target)
    print(f"Ahead:   {ahead} commit(s)")

    # Need PAT early so the PR title can use the work item title.
    client: AzdoClient | None = None
    work_item_title: str | None = None
    if task_id:
        try:
            client = AzdoClient(load_pat())
            work_item_title = fetch_work_item_title(client, task_id)
            if work_item_title:
                print(f"WI title: {work_item_title}")
        except Fatal as e:
            if dry_run:
                print(f"Warning: {e}", file=sys.stderr)
            else:
                raise

    title, description = build_title_and_description(
        target, task_id, work_item_title=work_item_title
    )
    print(f"Title:   {title}")

    if dry_run:
        print("\n[dry-run] Would create PR with body:\n")
        print(description)
        print("[dry-run] Skipping create / reviewers / autocomplete / work item.")
        return

    if client is None:
        client = AzdoClient(load_pat())

    # Active PR already?
    q = urllib.parse.urlencode(
        {
            "searchCriteria.sourceRefName": f"refs/heads/{current}",
            "searchCriteria.status": "active",
            "api-version": "7.0",
        }
    )
    existing = client.get(
        f"{PROJECT_APIS}/git/repositories/{REPO_NAME}/pullrequests?{q}"
    )
    if existing.get("count"):
        pr = existing["value"][0]
        url = (
            f"{ORG}/Trader/_git/{REPO_NAME}/pullrequest/{pr['pullRequestId']}"
        )
        raise Fatal(
            f"Active PR already exists: #{pr['pullRequestId']} → "
            f"{pr.get('targetRefName')}\n{url}"
        )

    body: dict[str, Any] = {
        "sourceRefName": f"refs/heads/{current}",
        "targetRefName": f"refs/heads/{target}",
        "title": title,
        "description": description,
        "isDraft": draft,
    }
    if task_id:
        body["workItemRefs"] = [{"id": task_id}]

    pr = client.post(
        f"{PROJECT_APIS}/git/repositories/{REPO_NAME}/pullrequests?api-version=7.0",
        body,
    )
    pr_id = pr["pullRequestId"]
    author_id = pr["createdBy"]["id"]
    pr_url = f"{ORG}/Trader/_git/{REPO_NAME}/pullrequest/{pr_id}"
    print(f"\nCreated PR #{pr_id} (draft={bool(pr.get('isDraft'))})")
    print(pr_url)

    # Reviewers
    members = client.get(
        f"{COLLECTION_APIS}/projects/Trader/teams/{ANDROID_TEAM_ID}/members?api-version=7.0"
    )
    added: list[str] = []
    to_add: list[tuple[str, bool, str]] = []
    if REQUIRED_REVIEWER_ID != author_id:
        to_add.append((REQUIRED_REVIEWER_ID, True, REQUIRED_REVIEWER_NAME))
    for entry in members.get("value", []):
        ident = entry.get("identity") or entry
        if ident.get("isContainer"):
            continue
        rid = ident.get("id")
        name = ident.get("displayName") or rid
        if not rid or rid == author_id or rid == REQUIRED_REVIEWER_ID:
            continue
        to_add.append((rid, False, name))

    for rid, required, name in to_add:
        client.put(
            f"{PROJECT_APIS}/git/repositories/{REPO_NAME}/pullRequests/"
            f"{pr_id}/reviewers/{rid}?api-version=7.0",
            {"vote": 0, "isRequired": required},
        )
        kind = "required" if required else "optional"
        added.append(f"{name} ({kind})")
        print(f"Reviewer: {name} [{kind}]")

    # Auto-complete
    try:
        client.patch(
            f"{PROJECT_APIS}/git/repositories/{REPO_NAME}/pullRequests/"
            f"{pr_id}?api-version=7.0",
            {
                "autoCompleteSetBy": {"id": author_id},
                "completionOptions": {
                    "mergeStrategy": "noFastForward",
                    "deleteSourceBranch": True,
                    "transitionWorkItems": True,
                },
            },
        )
        print("Auto-complete: set")
    except Fatal as e:
        print(f"Auto-complete: FAILED (continuing)\n{e}", file=sys.stderr)

    # Verify / repair work item link
    if task_id:
        linked = client.get(
            f"{PROJECT_APIS}/git/repositories/{REPO_NAME}/pullRequests/"
            f"{pr_id}/workitems?api-version=7.0"
        )
        ids = {str(x.get("id")) for x in linked.get("value", [])}
        if task_id not in ids:
            artifact = (
                f"vstfs:///Git/PullRequestId/"
                f"{PROJECT_ID}%2F{REPO_ID}%2F{pr_id}"
            )
            client.patch(
                f"{PROJECT_APIS}/wit/workitems/{task_id}?api-version=7.0",
                [
                    {
                        "op": "add",
                        "path": "/relations/-",
                        "value": {
                            "rel": "ArtifactLink",
                            "url": artifact,
                            "attributes": {"name": "Pull Request"},
                        },
                    }
                ],
                json_patch=True,
            )
            print(f"Linked task #{task_id} via work-item relation")
        else:
            print(f"Work item linked: #{task_id}")

        # Update Task scheduling / state
        wi = client.get(f"{PROJECT_APIS}/wit/workitems/{task_id}?api-version=7.0")
        fields = wi.get("fields", {})
        wi_type = fields.get("System.WorkItemType")
        wi_url = (
            wi.get("_links", {}).get("html", {}).get("href")
            or f"{ORG}/Trader/_workitems/edit/{task_id}"
        )
        if wi_type != "Task":
            print(f"Skipped work-item update: type is {wi_type!r}, expected Task")
        else:
            completed = fields.get("Microsoft.VSTS.Scheduling.CompletedWork") or 0
            remaining = fields.get("Microsoft.VSTS.Scheduling.RemainingWork") or 0
            try:
                completed_f = float(completed)
            except (TypeError, ValueError):
                completed_f = 0.0
            try:
                remaining_f = float(remaining)
            except (TypeError, ValueError):
                remaining_f = 0.0
            new_completed = completed_f + remaining_f
            state_before = fields.get("System.State")
            client.patch(
                f"{PROJECT_APIS}/wit/workitems/{task_id}?api-version=7.0",
                [
                    {
                        "op": "add",
                        "path": "/fields/Microsoft.VSTS.Scheduling.CompletedWork",
                        "value": new_completed,
                    },
                    {
                        "op": "add",
                        "path": "/fields/Microsoft.VSTS.Scheduling.RemainingWork",
                        "value": 0,
                    },
                    {"op": "add", "path": "/fields/System.State", "value": "Review"},
                ],
                json_patch=True,
            )
            print(f"Work item: {wi_url}")
            print(
                f"  State:     {state_before} → Review\n"
                f"  Completed: {completed_f} → {new_completed}\n"
                f"  Remaining: {remaining_f} → 0"
            )

    print("\n--- Goft (cip_android) ---")
    print(pr_url)
    print(short_description(title))
    print("--------------------------")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Create an Azure DevOps PR (same workflow as Cursor `pr_create_on_azure.sh`)."
    )
    parser.add_argument(
        "--into",
        metavar="BRANCH",
        help="Override target/base branch (default: resolve stacked parent)",
    )
    parser.add_argument(
        "--draft",
        action="store_true",
        help="Create the PR as a draft",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve target and print title/body; do not call Azure APIs",
    )
    parser.add_argument(
        "--skip-push",
        action="store_true",
        help="Do not push the branch before creating the PR",
    )
    args = parser.parse_args(argv)

    # Ensure we run from a git work tree (prefer repo root)
    try:
        root = run(["git", "rev-parse", "--show-toplevel"])
        os.chdir(root)
    except Fatal:
        raise Fatal("Not inside a git repository.") from None

    create_pr_flow(
        into=args.into,
        draft=args.draft,
        dry_run=args.dry_run,
        skip_push=args.skip_push,
    )


if __name__ == "__main__":
    try:
        main()
    except Fatal as e:
        print(str(e) or "Failed.", file=sys.stderr)
        raise SystemExit(e.code if isinstance(e.code, int) else 1) from None
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130) from None
